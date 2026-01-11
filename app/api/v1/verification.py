from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UserVerify
from app.services import verify_otp, regenerate_otp, get_user_by_email

router = APIRouter(tags=["Verification"])

@router.post("/verify-otp", summary="Verify email with OTP")
def verify_otp_endpoint(verification: UserVerify, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=verification.email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "User already verified"}
    
    if verify_otp(db, email=verification.email, otp=verification.otp):
        return {"message": "Account verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

@router.post("/resend-otp", summary="Resend verification OTP")
def resend_otp(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "User already verified"}
    
    otp = regenerate_otp(db, email=email)
    print(f"DEBUG: Resent OTP for {user.email} is {otp}")
    
    return {"message": "OTP resent successfully"}
