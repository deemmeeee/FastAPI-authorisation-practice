# ручка для регистрации 

from fastapi import  APIRouter
router = APIRouter()


@router.post("/register", response_model=Token)
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
    access_token = create_access_token(data={"sub": db_user.email},
                                       expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")


# ручка передает пользователю токен
@router.post("/login")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


# ручка для получения информации о своем аккаунте(доступна только владельцу)
@router.get("/secure-endpoint", response_model=UserBase)
async def read_users_me(current_user: Annotated[UserBase, Depends(get_current_user)]):
    return current_user


# ручка для получения информации о приложении
@router.get("/status")
def read_status():
    return {"title": APP_NAME,
            "version": APP_VERSION,
            "description": APP_DESCRIPTION}