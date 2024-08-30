from typing import Union, Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from .config import APP_NAME, APP_VERSION, APP_DESCRIPTION


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# фейковое хэширование
def fake_hash_password(password: str):
    return "fakehashed" + password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


# принимает введенный username возвращает все данные юзера если он есть
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


#  Фейковая функция для декодирования токена, на входе токен, на выходе
# экземпляр класса User с данными пользователя
# В реальной системе использовали бы библиотеку для обработки и проверки токенов, 
# pyjwt для JWT, и делали бы запросы к бд для получения информации о пользователе.
# def fake_decode_token(token):
#     return User(
#         username=token + "fakedecoded", email="fake@example.com", full_name="Joe", 
#     )
def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


# извлекает токен и с помощью функции fake_decode_token проверяет есть ли пользователь 
# с таким токеном
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


# проверяет активен ли пользователь 
async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)],):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ручка передает пользователю токен
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect data")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}


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
