from sqlalchemy.orm import Session
from app.models import User
from app.schemas import Token
from app.core.security import verify_password, create_access_token, create_refresh_token, generate_otp
import datetime

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_tokens(user: User) -> Token:
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def verify_otp(db: Session, email: str, otp: str) -> bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    
    if user.otp_code != otp:
        return False
    
    if datetime.datetime.utcnow() > user.otp_created_at + datetime.timedelta(minutes=5):
        return False
    
    user.is_verified = True
    user.otp_code = None
    db.commit()
    
    return True

def regenerate_otp(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("User not found")
    
    otp = generate_otp()
    user.otp_code = otp
    user.otp_created_at = datetime.datetime.utcnow()
    db.commit()
    
    return otp

def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.hashed_password):
        raise ValueError("Incorrect old password")
    
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash(new_password)
    db.commit()

def reset_password(db: Session, email: str, otp: str, new_password: str) -> None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("User not found")
    
    if user.otp_code != otp:
        raise ValueError("Invalid OTP")
    
    if datetime.datetime.utcnow() > user.otp_created_at + datetime.timedelta(minutes=5):
        raise ValueError("OTP expired")
    
    from app.core.security import get_password_hash
    user.hashed_password = get_password_hash(new_password)
    user.otp_code = None
    db.commit()
