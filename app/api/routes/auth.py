from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import *
from app.services.user_service import *
from app.core.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user_in, db)

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    return await login_user(user_in, db)

@router.get("/verify")
async def verify_email_token(token: str, db: AsyncSession = Depends(get_db)):
    await verify_email(token, db)
    return {"msg": "Email verified"}

@router.post("/forgot-password")
async def forgot(email_req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    await forgot_password(email_req.email, db)
    return {"msg": "Reset email sent"}

@router.post("/reset-password")
async def reset(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    await reset_password(req.reset_token, req.old_password, req.new_password, db)
    return {"msg": "Password reset successful. You may now log in with your new password."}


@router.post("/refresh", response_model=Token)
async def refresh(payload: TokenPayload):
    return await refresh_token(payload.dict())
