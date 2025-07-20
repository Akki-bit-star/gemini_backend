from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User, SubscriptionTier
from app.services.stripe_service import StripeService
from app.config import settings
import stripe

router = APIRouter(tags=["Subscription"])


@router.post("/subscribe/pro")
async def subscribe_pro(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        # Create or get Stripe customer
        if not current_user.stripe_customer_id:
            customer = StripeService.create_customer(
                email=f"{current_user.mobile_number}@example.com",
                name=f"User {current_user.mobile_number}"
            )
            current_user.stripe_customer_id = customer.id
            print("Created Stripe customer:", customer.id)
            db.commit()

        # Create checkout session
        session = StripeService.create_checkout_session(
            customer_id=current_user.stripe_customer_id
        )

        return {"checkout_url": session.url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/subscription/status")
async def get_subscription_status(current_user: User = Depends(get_current_user)):
    return {
        "subscription_tier": current_user.subscription_tier,
        "daily_message_count": current_user.daily_message_count,
        "daily_limit": 5 if current_user.subscription_tier == SubscriptionTier.BASIC else "unlimited"
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        customer_id = session['customer']

        # Update user subscription
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_tier = SubscriptionTier.PRO
            db.commit()

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        customer_id = subscription['customer']

        # Downgrade user subscription
        user = db.query(User).filter(
            User.stripe_customer_id == customer_id).first()
        if user:
            user.subscription_tier = SubscriptionTier.BASIC
            db.commit()

    return {"status": "success"}
