# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
# from src.core.file_processor import FileProcessor
# from src.core.language_detector import LanguageDetector
# from src.core.parser_factory import ParserFactory
# import json

# app = FastAPI(title="Function Extractor Service")

# processor = FileProcessor(ParserFactory())

# @app.post("/extract")
# async def extract_functions(file: UploadFile = File(...)):
#     """Выделить функции из загруженного файла"""
#     try:
#         # Сохранить временно
#         import tempfile
#         with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
#             content = await file.read()
#             tmp.write(content)
#             tmp.flush()
            
#             # Парсить
#             signatures = processor.process_file(tmp.name)
            
#             return {
#                 "file": file.filename,
#                 "language": LanguageDetector.detect_language(file.filename),
#                 "functions": [sig.__dict__ for sig in signatures]
#             }
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.get("/status")
# async def get_status():
#     """Получить статус сервиса"""
#     return {
#         "status": "healthy",
#         "supported_languages": [lang.value for lang in LanguageDetector.supported_languages()]
#     }

# @app.get("/health")
# async def health_check():
#     """Health check"""
#     return {"status": "ok"}