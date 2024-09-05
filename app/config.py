from pydantic_settings import BaseSettings

APP_NAME = "First test API"
APP_VERSION = "0.0.1"
APP_DESCRIPTION = """
First test API, here i'm practicing FastAPI
"""

class AppConfig(BaseSettings):
    database_url: str
