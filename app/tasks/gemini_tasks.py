from celery import Celery
from app.services.gemini_service import GeminiService
from app.config import settings

celery_app = Celery(
    'gemini_tasks',
    broker=settings.redis_url,
    backend=settings.redis_url
)


@celery_app.task
def process_gemini_message(message_id: int, user_message: str):
    from app.database import SessionLocal
    from app.models.message import Message
    from app.models.chatroom import Chatroom
    from app.models.user import User
    from app.models.otp import OTP

    db = SessionLocal()
    try:
        gemini_service = GeminiService()
        response = gemini_service.generate_response(user_message)

        message = db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.gemini_response = response
            db.commit()

        print(
            f"Message ID: {message_id}, User Message: {user_message}, Response: {response}")
        return response
    finally:
        db.close()
