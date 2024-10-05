from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


# модель добавляет пароль к базовой модели для регистрации
class UserCreate(UserBase):
    password: str


# модель добавляет хэшированный пароль к базовой модели для регистрации
class UserInDB(UserBase):
    hashed_password: str
