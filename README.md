# Function Extractor Service

Сервис для извлечения сигнатур функций из исходного кода различных языков программирования.

## Поддерживаемые языки

- Python
- C/C++
- C#
- Go
- Java
- JavaScript

## Требования

- Python 3.11 или выше
- `uv` - современный пакетный менеджер для Python
- Docker и Docker Compose (для запуска в контейнере)
- libclang-dev (для парсинга C/C++ кода)

## Установка uv

### Linux/macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Или через pip:

```bash
pip install uv
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Подробнее: https://github.com/astral-sh/uv

## Быстрый старт

```bash
# Установка uv (если еще не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Клонирование репозитория
git clone <repository-url>
cd function-extractor-service

# Установка зависимостей и создание виртуального окружения
uv sync

# Запуск сервиса
uv run python -m src.main

#uv run python -m src.main --reload --log-level debug

#uvicorn src.main:app --reload --log-level debug


# Запуск тестов
uv run pytest -s -v
```

## Установка зависимостей

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd function-extractor-service
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
uv sync
```

Если возникают проблемы с установкой проекта как пакета, можно использовать:
```bash
uv sync --no-install-project
```

Это установит только зависимости, не пытаясь установить сам проект.

Эта команда автоматически:
- Создаст виртуальное окружение `.venv`
- Установит все зависимости из `pyproject.toml`
- Создаст файл `uv.lock` с зафиксированными версиями

> **Примечание:** Проект был переведен на использование `uv` вместо `pip`. Старый файл `requirements.txt` сохранен для справки, но рекомендуется использовать `pyproject.toml` и `uv sync` для установки зависимостей.

### Установка зависимостей разработки

Для установки с инструментами разработки (pytest, black, flake8, mypy):

```bash
uv sync --group dev
```

## Запуск проекта

### Локальный запуск

1. Активируйте виртуальное окружение (если не активировано автоматически):
```bash
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate     # Windows
```

2. Запустите сервис:
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Или используйте прямой запуск через uv:
```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Сервис будет доступен по адресу: http://localhost:8000

### Запуск через Docker

1. Соберите образ:
```bash
docker build -t function-extractor-service .
```

2. Запустите контейнер:
```bash
docker run -p 8000:8000 function-extractor-service
```

### Запуск через Docker Compose

Запустите все сервисы (backend + frontend):

```bash
docker-compose up
```

Для запуска в фоновом режиме:
```bash
docker-compose up -d
```

Остановка:
```bash
docker-compose down
```

## Структура проекта

```
function-extractor-service/
├── src/                    # Исходный код приложения
│   ├── api/               # API endpoints и WebSocket обработчики
│   ├── core/              # Основная логика (парсеры, процессоры)
│   ├── models/            # Модели данных
│   ├── parsers/           # Парсеры для различных языков
│   └── main.py            # Точка входа приложения
├── tests/                 # Тесты
│   ├── unit/              # Unit тесты
│   └── integration/       # Интеграционные тесты
├── frontend/              # Веб-интерфейс
├── pyproject.toml         # Конфигурация проекта и зависимости (uv)
├── Dockerfile             # Конфигурация Docker образа
└── docker-compose.yml     # Конфигурация Docker Compose
```

## API Endpoints

### POST /api/extract
Извлечение функций из загруженного файла

**Request:**
- Content-Type: multipart/form-data
- file: файл с исходным кодом

**Response:**
```json
{
  "language": "python",
  "functions": [
    {
      "name": "function_name",
      "return_type": "str",
      "parameters": ["param1", "param2"],
      "line_number": 10,
      "is_method": false
    }
  ]
}
```

### GET /api/health
Проверка здоровья сервиса

### WebSocket /ws
WebSocket соединение для получения обновлений в реальном времени

## Тестирование

Запуск всех тестов:
```bash
uv run pytest
```

Запуск с покрытием кода:
```bash
uv run pytest --cov=src --cov-report=html
```

Запуск только unit тестов:
```bash
uv run pytest tests/unit/
```

Запуск только интеграционных тестов:
```bash
uv run pytest tests/integration/
```

## Разработка

### Форматирование кода

```bash
uv run black src/ tests/
```

### Линтинг

```bash
uv run flake8 src/ tests/
```

### Проверка типов

```bash
uv run mypy src/
```

### Добавление новых зависимостей

```bash
# Добавить зависимость для продакшена
uv add package-name

# Добавить зависимость для разработки
uv add --group dev package-name

# Удалить зависимость
uv remove package-name
```

Зависимости автоматически обновятся в `pyproject.toml` и `uv.lock`.

## Обновление зависимостей

Обновить все зависимости до последних совместимых версий:
```bash
uv lock --upgrade
```

Затем переустановить:
```bash
uv sync
```

## Устранение неполадок

### Ошибка при установке libclang

На Linux необходимо установить системные зависимости:
```bash
sudo apt-get update
sudo apt-get install libclang-dev build-essential
```

На macOS:
```bash
brew install llvm
```

На Windows обычно устанавливается автоматически через pip.

### Проблемы с uv

Если `uv` не найден в PATH, убедитесь, что он установлен:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

После установки может потребоваться перезапустить терминал или выполнить:
```bash
source ~/.bashrc  # или ~/.zshrc
```

### Ошибки при сборке Docker образа

Убедитесь, что Docker запущен и у вас есть права на его использование. Также проверьте, что образ `ghcr.io/astral-sh/uv:latest` доступен.

## Лицензия

MIT

## Авторы

Function Extractor Service Team
