# frogcom/api/routes/base_routes.py
from fastapi import APIRouter, HTTPException, Request
from src.utils.logger import SimpleLogger

class BaseRoutes:
    """Базовый класс для всех маршрутов API."""

    def __init__(self, logging_service: SimpleLogger):
        self.logging_service = logging_service
        self.router = APIRouter()

    def get_router(self) -> APIRouter:
        """Возвращает настроенный роутер для регистрации в FastAPI."""
        return self.router