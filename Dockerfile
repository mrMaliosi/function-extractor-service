FROM python:3.11-slim

WORKDIR /app

# Установить uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Установить зависимости системы для libclang
RUN apt-get update && apt-get install -y \
    libclang-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Скопировать файлы проекта
COPY pyproject.toml ./
COPY uv.lock* ./
COPY src/ ./src/
COPY tests/ ./tests/

# Установить зависимости с помощью uv
# Используем --frozen только если uv.lock существует, иначе синхронизируем без него
RUN if [ -f uv.lock ]; then uv sync --frozen --no-dev; else uv sync --no-dev; fi

# Выставить порт
EXPOSE 8000

# Запустить сервис через uv
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]