from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Настройки приложения
    app_name: str = "First test API"
    app_version: str = "0.0.1"
    app_description: str = "First test API, here I'm practicing FastAPI"

    # Настройки безопасности
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Настройки postgres БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    class Config:   
        env_file = ".env"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
