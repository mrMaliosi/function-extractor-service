from datetime import datetime
from fastapi import HTTPException

from src.core.language_detector import LanguageDetector
from src.dto.health import HealthResponse, StatusResponse
from src.api.base import BaseRoutes

class HealthRoutes(BaseRoutes):
    """Маршруты проверки состояния сервиса."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            response_model=HealthResponse,
            summary="Проверка состояния основной модели",
            description="Возвращает статус основной модели"
        )

        self.router.add_api_route(
            "/status",
            self.status_check,
            methods=["GET"],
            response_model=StatusResponse,
            summary="Проверка состояния вспомогательной модели",
            description="Возвращает статус вспомогательной модели"
        )

    async def health_check(self) -> HealthResponse:
        """Проверка состояния сервиса."""
        try:
            return HealthResponse(
                status="ok",
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logging_service.log_error(e)
            raise HTTPException(status_code=500, detail=f"Ошибка проверки: {str(e)}")

    async def status_check(self) -> StatusResponse:
        """Проверка состояния сервиса."""
        try:
            detector = LanguageDetector()
            return StatusResponse(
                status="ok",
                timestamp=datetime.now(),
                supported_languages=[lang.value for lang in detector.supported_languages()]
            )
        except Exception as e:
            self.logging_service.log_error(e)
            raise HTTPException(status_code=500, detail=f"Ошибка проверки: {str(e)}")