from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import settings


router = APIRouter()


@router.get("/status", response_model=dict)
def read_status() -> JSONResponse:
    """
    Ручка для получения информации о приложении
    """
    return {"title": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description}
