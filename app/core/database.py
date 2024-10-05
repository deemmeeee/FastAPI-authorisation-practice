from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import Settings

# Импорт настроек из config
settings = Settings()

# Создаем асинхронный движок БД
engine = create_async_engine(settings.database_url, echo=True)

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем асинхронную сессию
async_session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Генератор для получения сессии БД
async def get_db():
    async with async_session() as db:
        yield db
