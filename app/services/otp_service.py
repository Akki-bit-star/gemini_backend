import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.otp import OTP
from app.models.user import User


class OTPService:
    @staticmethod
    def generate_otp() -> str:
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def create_otp(mobile_number: str, db: Session) -> str:
        # Invalidate any existing OTPs for this mobile number
        db.query(OTP).filter(OTP.mobile_number ==
                             mobile_number).update({"is_used": True})

        otp_code = OTPService.generate_otp()
        expires_at = datetime.now() + timedelta(minutes=10)

        otp = OTP(
            mobile_number=mobile_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(otp)
        db.commit()

        return otp_code

    @staticmethod
    def verify_otp(mobile_number: str, otp_code: str, db: Session) -> bool:
        otp = db.query(OTP).filter(
            OTP.mobile_number == mobile_number,
            OTP.otp_code == otp_code,
            OTP.is_used == False,
            OTP.expires_at > datetime.now()
        ).first()

        if otp:
            otp.is_used = True
            db.commit()
            return True
        return False
