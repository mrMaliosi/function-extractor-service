# frogcom/api/routes/base_routes.py
from fastapi import APIRouter, HTTPException, Request

class BaseRoutes:
    """Базовый класс для всех маршрутов API."""

    def __init__(self):
        self.router = APIRouter()

    def get_router(self) -> APIRouter:
        """Возвращает настроенный роутер для регистрации в FastAPI."""
        return self.router