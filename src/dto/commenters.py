from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class CommentResponse(BaseModel):
    """Модель ответа для возврата комментария к функции."""

    comment: str = Field(..., description="Комментарий к функции")


class CommentRequest(BaseModel):
    """Модель запроса для создания комментариев к списку функций."""

    task: str = Field(..., description="Задача к функции")
    code: str = Field(..., description="Сама функций")
    function: str = Field(..., description="Распаршенная функция")

class Message(BaseModel):
    """Модель сообщения в чате."""
    
    role: str = Field(..., description="Роль отправителя (user, assistant, system)")
    content: str = Field(..., description="Содержимое сообщения")

class Choice(BaseModel):
    """Модель выбора в ответе."""
    
    index: int = Field(..., description="Индекс выбора")
    message: Message = Field(..., description="Сообщение ассистента")
    finish_reason: str = Field(..., description="Причина завершения генерации")

class GenerateResponse(BaseModel):
    """Модель ответа на запрос генерации."""
    
    id: str = Field(..., description="Уникальный идентификатор запроса")
    object: str = Field(default="text_completion", description="Тип объекта")
    created: int = Field(..., description="Время создания в Unix timestamp")
    model: str = Field(..., description="Использованная модель")
    choices: List[Choice] = Field(..., description="Список сгенерированных вариантов")

class GenerateRequest(BaseModel):
    """Модель запроса на генерацию текста."""
    
    prompt: Optional[str] = Field(None, description="Прямой промпт для генерации")
    messages: Optional[List[Message]] = Field(None, description="Список сообщений в формате чата")
    max_tokens: Optional[int] = Field(None, ge=1, le=4096, description="Максимальное количество токенов")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Температура для генерации")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p параметр")
    stop: Optional[List[str]] = Field(None, description="Список стоп-слов")
    seed: Optional[int] = Field(None, description="Сид для воспроизводимости")
    model: Optional[str] = Field(None, description="Название модели (игнорируется, используется текущая)")
