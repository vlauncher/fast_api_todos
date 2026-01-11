from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.database import get_db
from app.core.config import SECRET_KEY, ALGORITHM
from app.api.deps import get_current_user
from app.models import User
from app.schemas import Token, PasswordChange, PasswordResetRequest, PasswordResetConfirm, User, UserCreate, UserVerify, LoginRequest
from app.services import authenticate_user, create_tokens, verify_otp, regenerate_otp, change_password, reset_password, create_user, get_user_by_email

router = APIRouter(tags=["Auth"])

@router.post("/register", response_model=User, summary="Register new user")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = create_user(db, user)
        print(f"DEBUG: OTP for {new_user.email} is {new_user.otp_code}")
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token, summary="Login with email and password")
def login(
    login_data: LoginRequest, 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email=login_data.email, password=login_data.password)
    if not user:
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
    
    return create_tokens(user)

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

@router.post("/refresh", response_model=Token, summary="Refresh access token")
def refresh_token(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    from app.services import get_user_by_email
    user = get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return create_tokens(user)

@router.post("/change-password", summary="Change password")
async def change_password_endpoint(
    password_data: PasswordChange, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        change_password(db, current_user, password_data.old_password, password_data.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forgot-password", summary="Request password reset")
async def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    from app.services import get_user_by_email
    user = get_user_by_email(db, email=request.email)
    if not user:
        return {"message": "If this email exists, an OTP has been sent."}
    
    otp = regenerate_otp(db, email=request.email)
    print(f"DEBUG: Password Reset OTP for {user.email} is {otp}")
    return {"message": "If this email exists, an OTP has been sent."}

@router.post("/reset-password", summary="Reset password with OTP")
async def reset_password_endpoint(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    try:
        reset_password(db, email=reset_data.email, otp=reset_data.otp, new_password=reset_data.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
