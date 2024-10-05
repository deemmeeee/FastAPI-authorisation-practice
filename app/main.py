from fastapi import Depends, FastAPI, HTTPException, status

from .core.config import settings
from app.routes import user_routes, auth_routes, app_info_routes

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
)

app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(app_info_routes.router)
