from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.repositories.user_repo import (
    get_user_by_email, 
    get_user_by_username, 
    add_user_to_db,
    get_user_by_id, 
    delete_user_in_db, 
    update_user_in_db
)
from app.models.postgres.user_models import UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password) -> str:
    """
    Хэширование полученного пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    """
    Проверка на соответствие хэша полученного пароля хэшу сохраненного пароля
    """
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> UserModel | None:
    """
    Аутентификация пользователя
    """
    user = await get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def create_user(db: AsyncSession, username: str, email: str, password: str) -> UserModel:
    """
    Создание экземпляра модели пользователя

    Здесь также бизнес-логика связанная с созданием аккаунта
    """
    hashed_password = get_password_hash(password)
    return await add_user_to_db(db, username, email, hashed_password)


async def delete_user_by_id(db: AsyncSession, user_id: int) -> None:
    """
    Удаляет пользователя по его ID.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await delete_user_in_db(db, user)


async def update_user(db: AsyncSession, user_id: int, update_data: dict) -> UserModel:
    """
    Обновляет данные пользователя.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await update_user_in_db(db, user, update_data)