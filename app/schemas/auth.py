from pydantic import BaseModel, Field
from typing import Optional


class UserSignup(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)
    password: Optional[str] = None


class SendOTP(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)


class VerifyOTP(BaseModel):
    mobile_number: str = Field(..., min_length=10, max_length=15)
    otp_code: str = Field(..., min_length=6, max_length=6)


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
