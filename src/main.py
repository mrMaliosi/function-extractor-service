# src/main.py
from fastapi import FastAPI
import uvicorn
from src.core.language_detector import LanguageDetector

def create_app() -> FastAPI:
    app = FastAPI(title="Function Extractor Service", version="0.1.0")

    detector = LanguageDetector()

    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    @app.get("/status")
    async def status():
        return {
            "status": "ok",
            "supported_languages": [lang.value for lang in detector.supported_languages()],
        }

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
