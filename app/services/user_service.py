from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from uuid import UUID
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password
from app.core.token import create_access_token, create_refresh_token, create_token
from app.core.email import send_email
from app.core.config import settings
from datetime import timedelta
from jose import jwt, JWTError


async def register_user(user_in: UserCreate, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        password=hash_password(user_in.password),
        is_verified=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token({"sub": str(user.id)}, timedelta(days=1))
    verify_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    send_email(
        to=user.email,
        subject="Verify your email",
        template_name="verify_email.html",
        context={"first_name": user.first_name, "url": verify_link}
    )
    return user


async def login_user(user_in: UserLogin, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar()
    if not user or not verify_password(user_in.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
    }


async def verify_email(token: str, db: AsyncSession):
    from jose import jwt
    from app.core.config import settings

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except:
        raise HTTPException(status_code=400, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.add(user)
    await db.commit()

    send_email(
        to=user.email,
        subject="Email Verified Successfully",
        template_name="email_verified_success.html",
        context={"first_name": user.first_name}
    )


async def forgot_password(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        return

    token = create_token({"sub": str(user.id)}, timedelta(days=1))
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    send_email(
        to=user.email,
        subject="Password Reset Request",
        template_name="forgot_password.html",
        context={"first_name": user.first_name, "url": reset_link}
    )


async def reset_password(reset_token: str, old_password: str, new_password: str, db: AsyncSession):
    try:
        payload = jwt.decode(reset_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=403, detail="Old password is incorrect")

    if verify_password(new_password, user.password):
        raise HTTPException(status_code=400, detail="New password cannot be the same as old password")

    user.password = hash_password(new_password)
    db.add(user)
    await db.commit()

    # ✅ Optional: send success email
    send_email(
        to=user.email,
        subject="Password Reset Successful",
        template_name="password_reset_success.html",
        context={"first_name": user.first_name}
    )


async def refresh_token(payload: dict):
    user_id = payload.get("sub")
    return {
        "access_token": create_access_token({"sub": user_id}),
        "refresh_token": create_refresh_token({"sub": user_id}),
    }
