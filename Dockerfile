# Базовый образ Python 3.11
FROM python:3.11-slim as base

ARG POETRY_HOME=/etc/poetry

# Установка переменных окружения
ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.4.0 \
    POETRY_HOME=$POETRY_HOME \
    PATH="$POETRY_HOME/bin:$PATH"

# Установка зависимостей
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl && \
    curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION && \
    export PATH="$POETRY_HOME/bin:$PATH" && \
    $POETRY_HOME/bin/poetry config virtualenvs.create false && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование файлов для установки зависимостей
COPY pyproject.toml poetry.lock /app/

# Установка зависимостей через Poetry
RUN poetry install --no-interaction --no-ansi --no-dev

# Копирование исходников проекта
COPY . /app

# Открытие порта для FastAPI
EXPOSE 8000

# Команда для запуска приложения
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
