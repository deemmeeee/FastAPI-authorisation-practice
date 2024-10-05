from typing import Annotated

from fastapi import APIRouter
from fastapi import Depends

from app.schemas.user_schema import UserBase
from app.services.auth_service import get_current_user


router = APIRouter()


@router.get("/secure-endpoint", response_model=UserBase)
async def read_users_me(current_user: Annotated[UserBase, Depends(get_current_user)]) -> UserBase:
    """
    Ручка для получения информации о своем аккаунте(доступна только владельцу)
    """
    return current_user
