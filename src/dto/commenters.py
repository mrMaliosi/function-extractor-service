from typing import List
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

