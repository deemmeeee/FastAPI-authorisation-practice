from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from .models import User as UserModel
from .database import get_db

SECRET_KEY = "3c59c096d98638d670db50551e2bb50ec377300d37f118f0f00eafd3880418af"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


# хэширование пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)


def get_user_by_email(db: Session, email:str):
    return db.query(UserModel).filter(UserModel.email == email).first()


# создание экземпляра модели пользователя
def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = UserModel(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# проверка на соответствие хэша полученного пароля хэшу сохраненного пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# хэширование полученного пароля
def get_password_hash(password):
    return pwd_context.hash(password)


# принимает введенный username возвращает все данные юзера если он есть
def get_user(db, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()


# аутентификация пользователя
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# генерация нового аксес токена
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# извлекает токен, декодирует его с помощью библиотеки 
# jwt и проверяет есть ли пользователь с таким токеном
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate data",
        headers = {"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data=TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# проверяет активен ли пользователь 
async def get_current_active_user(current_user: Annotated[UserBase, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ручка для регистрации 
@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Проверяем, существует ли пользователь с таким же username
    existing_user_by_username = get_user(db, user.username)
    if existing_user_by_username:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = create_user(db, username=user.username, email=user.email, password=user.password)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user.email}, expires_delta=access_token_expires)
    
    return Token(access_token=access_token, token_type="bearer")


# ручка передает пользователю токен
@app.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


# ручка для получения информации о своем аккаунте(доступна только владельцу)
@app.get("/secure-endpoint", response_model=UserBase)
async def read_users_me(current_user: Annotated[UserBase, Depends(get_current_user)]):
    return current_user


# ручка для получения информации о приложении
@app.get("/status")
def read_status():
    return {"title": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION}
