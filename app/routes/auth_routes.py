from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user_schema import Token
from app.schemas.user_schema import UserCreate
from app.services.auth_service import create_access_token
from app.services.user_service import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    authenticate_user
)
from app.core.database import get_db
from app.core.config import settings



router = APIRouter()


@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)) -> Token:
    """
    Ручка для регистрации
    """
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Проверяем, существует ли пользователь с таким же username
    existing_user_by_username = get_user_by_username(db, user.username)
    if existing_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = await create_user(db, username=user.username, email=user.email, password=user.password)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": db_user.email},
                                       expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db)
) -> Token:
    """
    Ручка передает пользователю токен
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
