from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SubscriptionTier(enum.Enum):
    BASIC = "basic"
    PRO = "pro"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    subscription_tier = Column(
        Enum(SubscriptionTier), default=SubscriptionTier.BASIC)
    daily_message_count = Column(Integer, default=0)
    last_message_date = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    chatrooms = relationship("Chatroom", back_populates="user")
    otps = relationship("OTP", back_populates="user")
