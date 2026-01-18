from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class HealthResponse(BaseModel):
    """Модель ответа для проверки здоровья сервиса."""

    status: str = Field(..., description="Статус сервиса")
    timestamp: datetime = Field(..., description="Время проверки")

class StatusResponse(BaseModel):
    """Модель ответа для проверки здоровья сервиса."""

    status: str = Field(..., description="Статус сервиса")
    timestamp: datetime = Field(..., description="Время проверки")
    supported_languages: List[str] = Field(..., description="Список поддерживаемых языков")

