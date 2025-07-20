from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MessageCreate(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=1000)


class MessageResponse(BaseModel):
    id: int
    user_message: str
    gemini_response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
