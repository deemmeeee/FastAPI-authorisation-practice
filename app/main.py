from datetime import datetime, timedelta, timezone
from typing import Union, Annotated

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext

from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION

SECRET_KEY = "3c59c096d98638d670db50551e2bb50ec377300d37f118f0f00eafd3880418af"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


# хэширование пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)


# проверка на соответствие хэша полученного пароля хэшу сохраненного пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# хэширование полученного пароля
def get_password_hash(password):
    return pwd_context.hash(password)


# принимает введенный username возвращает все данные юзера если он есть
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


# аутентификация пользователя
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
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


# извлекает токен, декодирует его с помощью библиотеки jwt и проверяет есть ли пользователь 
# с таким токеном
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# проверяет активен ли пользователь 
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ручка передает пользователю токен
@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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
@app.get("/secure-endpoint")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


# ручка для получения информации о приложении
@app.get("/status")
def read_status():
    return {"title": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION}
