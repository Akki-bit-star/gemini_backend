import stripe
from app.config import settings

stripe.api_key = settings.stripe_secret_key


class StripeService:
    @staticmethod
    def create_checkout_session(customer_email: str = None, customer_id: str = None):

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Gemini Pro Subscription',
                        },
                        'unit_amount': 999,  # $9.99 in cents
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                customer=customer_id,
                customer_email=customer_email,
                success_url='http://localhost:8000/static/success.html',
                cancel_url='http://localhost:8000/static/cancel.html',

            )
            return session
        except Exception as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_customer(email: str, name: str = None):
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer
        except Exception as e:
            print("Error creating customer:", e)
            raise Exception(f"Stripe error: {str(e)}")
