from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.schemas.user import UserResponse
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
