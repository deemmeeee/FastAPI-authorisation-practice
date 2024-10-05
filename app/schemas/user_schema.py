from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """
    Модель добавляет пароль к базовой модели для регистрации
    """
    password: str


class UserInDB(UserBase):
    """
    Модель добавляет хэшированный пароль к базовой модели для регистрации
    """
    hashed_password: str
