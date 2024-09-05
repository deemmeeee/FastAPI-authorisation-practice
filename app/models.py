from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str


# модель добавляет пароль к базовой модели для регистрации
class UserCreate(UserBase):
    password: str


# модель добавляет хэшированный пароль к базовой модели для регистрации
class UserInDB(UserBase):
    hashed_password: str
