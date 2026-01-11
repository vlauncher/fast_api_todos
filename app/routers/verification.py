from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import app.models as models, app.schemas as schemas, app.database as database, app.auth as auth
import datetime

router = APIRouter(tags=["verification"])

@router.post("/verify-otp")
def verify_otp(verification: schemas.UserVerify, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == verification.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "User already verified"}
    
    if user.otp_code != verification.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Check if OTP is expired (5 minutes timeout)
    if datetime.datetime.now(datetime.timezone.utc) > user.otp_created_at + datetime.timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="OTP expired")
    
    user.is_verified = True
    user.otp_code = None
    db.commit()
    
    return {"message": "Account verified successfully"}

@router.post("/resend-otp")
def resend_otp(email: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": "User already verified"}
    
    otp = auth.generate_otp()
    user.otp_code = otp
    user.otp_created_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    # Simulation: In a real app, send OTP via email/SMS here
    print(f"DEBUG: Resent OTP for {user.email} is {otp}")
    
    return {"message": "OTP resent successfully"}
