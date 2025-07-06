from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from app.models.user import User
from uuid import UUID
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password
from app.core.token import create_access_token, create_refresh_token
from app.core.email import send_email

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

    send_email(
        to=user.email,
        subject="Verify your email",
        template_name="verify_email.html",
        context={"first_name": user.first_name, "token": str(user.id)}
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
    user_id = token
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.add(user)
    await db.commit()

async def forgot_password(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        # For security, don’t reveal whether the email exists
        return
    # Send only a confirmation email
    send_email(
        to=user.email,
        subject="Password Reset Request Received",
        template_name="forgot_password.html",
        context={"first_name": user.first_name}
    )

async def reset_password(token: str, new_password: str, db: AsyncSession):
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

    user.password = hash_password(new_password)
    db.add(user)
    await db.commit()

async def refresh_token(payload: dict):
    user_id = payload.get("sub")
    return {
        "access_token": create_access_token({"sub": user_id}),
        "refresh_token": create_refresh_token({"sub": user_id}),
    }
