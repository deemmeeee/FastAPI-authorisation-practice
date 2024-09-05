from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.models import UserBase
from app.routes import router
from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from .database import get_db
from .models import User as UserModel

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)
app.include_router(router)


def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def create_user(db: Session, username: str, email: str, password: str) -> UserModel:
    """
    Создание экземпляра модели пользователя
    """
    hashed_password = get_password_hash(password)
    db_user = UserModel(username=username, email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# извлекает токен, декодирует его с помощью библиотеки
# jwt и проверяет есть ли пользователь с таким токеном
async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate data",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


# проверяет активен ли пользователь 
async def get_current_active_user(current_user: Annotated[UserBase, Depends(get_current_user)], ):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
