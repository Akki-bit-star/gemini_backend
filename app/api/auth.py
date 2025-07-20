from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.auth import UserSignup, SendOTP, VerifyOTP, ChangePassword, Token
from app.models.user import User
from app.services.otp_service import OTPService
from app.core.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.mobile_number == user_data.mobile_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists"
        )

    # Create new user
    hashed_password = get_password_hash(
        user_data.password) if user_data.password else None
    user = User(
        mobile_number=user_data.mobile_number,
        password_hash=hashed_password
    )
    db.add(user)
    db.commit()

    return {"message": "User created successfully"}


@router.post("/send-otp")
async def send_otp(otp_data: SendOTP, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.mobile_number ==
                                 otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    otp_code = OTPService.create_otp(otp_data.mobile_number, db)

    return {
        "message": "OTP sent successfully",
        "otp": otp_code  # In production, this should be sent via SMS
    }


@router.post("/verify-otp", response_model=Token)
async def verify_otp(otp_data: VerifyOTP, db: Session = Depends(get_db)):
    # Verify OTP
    if not OTPService.verify_otp(otp_data.mobile_number, otp_data.otp_code, db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # Create access token
    access_token_expires = timedelta(
        minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": otp_data.mobile_number},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(otp_data: SendOTP, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.mobile_number ==
                                 otp_data.mobile_number).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    otp_code = OTPService.create_otp(otp_data.mobile_number, db)

    return {
        "message": "Password reset OTP sent successfully",
        "otp": otp_code  # In production, this should be sent via SMS
    }


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify current password
    if not current_user.password_hash or not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )

    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}
