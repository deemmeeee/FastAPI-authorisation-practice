from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.postgres.user_models import UserModel


async def get_user_by_email(db: AsyncSession, email: str) -> UserModel | None:
    """
    Принимает введенный email возвращает все данные юзера если он есть
    """
    result = await db.execute(select(UserModel).filter(UserModel.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> UserModel | None:
    """
    Принимает введенный username возвращает все данные юзера если он есть
    """
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    return result.scalars().first()


async def add_user_to_db(db: AsyncSession, username: str, email: str, hashed_password: str) -> UserModel:
    """
    Создание экземпляра модели пользователя
    """
    db_user = UserModel(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    """
    Получает пользователя по его ID.
    """
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    return result.scalars().first()


async def delete_user_in_db(db: AsyncSession, user: UserModel) -> None:
    """
    Удаление экземпляра модели пользователя
    """
    await db.delete(user)
    await db.commit() 


async def update_user_in_db(db: AsyncSession, user: UserModel, update_data: dict) -> UserModel:
    """
    Обновление пользователя
    """
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)  # обновляет значение user, исходя из актуального значения в БД
    return user
