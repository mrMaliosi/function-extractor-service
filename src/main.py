# src/main.py
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

from src.core.language_detector import LanguageDetector
from src.core.parser_factory import ParserFactory


def create_app() -> FastAPI:
    app = FastAPI(title="Function Extractor Service", version="0.1.0")

    detector = LanguageDetector()
    factory = ParserFactory()

    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    @app.get("/status")
    async def status():
        return {
            "status": "ok",
            "supported_languages": [lang.value for lang in detector.supported_languages()],
        }
    
    @app.post("/prompt")
    async def prompt(file: UploadFile = File(...)):
        language = detector.detect_language(file.filename)
        if language is None:
            raise HTTPException(status_code=400, detail="Unsupported file extension")

        try:
            parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))

        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="replace")

        functions = parser.parse_content(content)

        # Временно возвращаем как dict (позже можно сделать Pydantic-модели)
        return {
            "file": file.filename,
            "language": language.value,
            "count": len(functions),
            "functions": [f.__dict__ for f in functions],
        }

    @app.post("/extract")
    async def extract(files: list[UploadFile] = File(...)):
        results = []
        for f in files:
            language = detector.detect_language(f.filename)
            if language is None:
                results.append({"file": f.filename, "error": "Unsupported file extension"})
                continue

            try:
                parser = factory.get_parser(language)
            except NotImplementedError as e:
                results.append({"file": f.filename, "error": str(e)})
                continue

            content = (await f.read()).decode("utf-8", errors="replace")
            functions = parser.parse_content(content)

            results.append({
                "file": f.filename,
                "language": language.value,
                "count": len(functions),
                "functions": [fd.__dict__ for fd in functions],
            })

        return {"results": results}
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
