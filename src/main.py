# src/main.py
from typing import List
from fastapi.responses import HTMLResponse
import uvicorn


def create_app() -> FastAPI:
    app = FastAPI(title="Function Extractor Service", version="0.1.0")

    
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
