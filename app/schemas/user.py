from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.user import SubscriptionTier


class UserResponse(BaseModel):
    id: int
    mobile_number: str
    subscription_tier: SubscriptionTier
    daily_message_count: int
    created_at: datetime

    class Config:
        from_attributes = True
