from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

class CommentResponse(BaseModel):
    """Модель Ответа для списка комментариев к функциям."""

    comments: List[str] = Field(..., description="Список комментариев к функциям")
    functions: List[str] = Field(..., description="Сами функции (список дат?)")


class CommentRequest(BaseModel):
    """Модель запроса для создания комментариев к списку функций."""

    tasks: List[str] = Field(..., description="Список задач/комментариев к функциям")
    functions: List[str] = Field(..., description="Список самих функций")

