# src/main.py
from typing import List
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
import uvicorn

from src.api.health import HealthRoutes
from src.api.commenters import CommentersRoutes

def register_routes(app: FastAPI) -> None:
    """Создаёт инстансы роутов и регистрирует их в приложении."""
    routes = [
        HealthRoutes(),
        CommentersRoutes(),
    ]
    for route in routes:
        app.include_router(route.get_router())

def create_app() -> FastAPI:
    app = FastAPI(title="Function Extractor Service", version="0.1.0")

    register_routes(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
