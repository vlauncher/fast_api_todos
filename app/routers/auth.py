from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta, timezone
import datetime
from app import models, schemas, auth, database
from jose import JWTError, jwt

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account not verified. Please verify your OTP."
        )
    
    access_token = auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(token: str, db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    new_refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "refresh_token": new_refresh_token, 
        "token_type": "bearer"
    }

@router.post("/change-password")
async def change_password(
    password_data: schemas.PasswordChange, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not auth.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.hashed_password = auth.get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}

@router.post("/forgot-password")
async def forgot_password(
    request: schemas.PasswordResetRequest,
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        # We return 200 even if user not found for security reasons
        return {"message": "If this email exists, an OTP has been sent."}
    
    otp = auth.generate_otp()
    user.otp_code = otp
    user.otp_created_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    
    # Simulation
    print(f"DEBUG: Password Reset OTP for {user.email} is {otp}")
    return {"message": "If this email exists, an OTP has been sent."}

@router.post("/reset-password")
async def reset_password(
    reset_data: schemas.PasswordResetConfirm,
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == reset_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.otp_code != reset_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    if datetime.datetime.now(datetime.timezone.utc) > user.otp_created_at + datetime.timedelta(minutes=5):
        raise HTTPException(status_code=400, detail="OTP expired")
    
    user.hashed_password = auth.get_password_hash(reset_data.new_password)
    user.otp_code = None
    db.commit()
    return {"message": "Password reset successfully"}
