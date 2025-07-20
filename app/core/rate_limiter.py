from datetime import datetime, date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, SubscriptionTier


class RateLimiter:
    @staticmethod
    def check_message_limit(user: User, db: Session):
        if user.subscription_tier == SubscriptionTier.PRO:
            return True

        today = date.today()

        # Reset daily count if it's a new day
        if user.last_message_date is None or user.last_message_date.date() != today:
            user.daily_message_count = 0
            user.last_message_date = datetime.now()
            db.commit()

        # Check if user has exceeded daily limit
        if user.daily_message_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily message limit exceeded. Upgrade to Pro for unlimited messages."
            )

        return True

    @staticmethod
    def increment_message_count(user: User, db: Session):
        if user.subscription_tier == SubscriptionTier.BASIC:
            user.daily_message_count += 1
            user.last_message_date = datetime.now()
            db.commit()
