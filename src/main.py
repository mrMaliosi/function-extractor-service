# src/main.py
from typing import List
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
import uvicorn

from src.api.health import HealthRoutes
from src.api.commenters import CommentersRoutes
from fastapi.responses import JSONResponse
import traceback

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

    @app.exception_handler(400)
    async def bad_request_handler(request: Request, exc: Exception):
        print(f"🔴 400 ERROR DETAILS: {exc}")
        print(f"🔴 Full traceback:\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "traceback": traceback.format_exc()}
        )

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
