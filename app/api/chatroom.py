from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.core.auth import get_current_user
from app.core.cache import cache
from app.core.rate_limiter import RateLimiter
from app.models.user import User
from app.models.chatroom import Chatroom
from app.models.message import Message
from app.schemas.chatroom import ChatroomCreate, ChatroomResponse, ChatroomDetail
from app.schemas.message import MessageCreate, MessageResponse
from app.tasks.gemini_tasks import process_gemini_message
from pydantic import model_validator

router = APIRouter(prefix="/chatroom", tags=["Chatroom"])


@router.post("/", response_model=ChatroomResponse, status_code=status.HTTP_201_CREATED)
async def create_chatroom(
    chatroom_data: ChatroomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatroom = Chatroom(
        name=chatroom_data.name,
        user_id=current_user.id
    )
    db.add(chatroom)
    db.commit()
    db.refresh(chatroom)

    # Invalidate cache
    cache.delete(f"chatrooms:{current_user.id}")

    return chatroom


@router.get("/", response_model=List[ChatroomResponse])
async def get_chatrooms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check cache first
    cache_key = f"chatrooms:{current_user.id}"
    cached_chatrooms = cache.get(cache_key)

    if cached_chatrooms:
        return cached_chatrooms

    # Query database
    chatrooms = db.query(Chatroom).filter(
        Chatroom.user_id == current_user.id).all()

    # Convert to response format
    chatrooms_data = [ChatroomResponse.from_orm(
        chatroom) for chatroom in chatrooms]

    # Cache the result (TTL: 5 minutes)
    cache.set(cache_key, [chatroom.dict()
              for chatroom in chatrooms_data], ttl=300)

    return chatrooms_data


@router.get("/{chatroom_id}", response_model=ChatroomDetail)
async def get_chatroom(
    chatroom_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()

    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )

    return chatroom


@router.post("/{chatroom_id}/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    chatroom_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if chatroom exists and belongs to user
    chatroom = db.query(Chatroom).filter(
        Chatroom.id == chatroom_id,
        Chatroom.user_id == current_user.id
    ).first()

    if not chatroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chatroom not found"
        )

    # Check rate limit
    RateLimiter.check_message_limit(current_user, db)

    # Create message
    message = Message(
        chatroom_id=chatroom_id,
        user_message=message_data.user_message
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    # Increment message count
    RateLimiter.increment_message_count(current_user, db)

    # Process with Gemini API and wait for result
    task_result = process_gemini_message.delay(
        message.id, message_data.user_message)

    # Wait for the task to complete (with timeout)
    try:
        gemini_response = task_result.get(timeout=30)  # 30 second timeout

        # Refresh the message to get updated data
        db.refresh(message)

    except Exception as e:
        print(f"Celery task failed: {e}")
        message.gemini_response = "Failed to process request"
        db.commit()
        db.refresh(message)
    # Process with Gemini API asynchronously
    # process_gemini_message.delay(message.id, message_data.user_message)

    # print(f"Message ID: {message.id}, User Message: {message_data.user_message}, Message: {message}")
    return message
