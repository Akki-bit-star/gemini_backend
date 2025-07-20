from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from .message import MessageResponse


class ChatroomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ChatroomResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatroomDetail(ChatroomResponse):
    messages: List[MessageResponse] = []
    model_config = {'from_attributes': True}
