from fastapi import HTTPException

from src.core.language_detector import LanguageDetector, Language
from src.dto.commenters import CommentResponse

from src.core.language_detector import LanguageDetector, Language
from src.core.parser_factory import ParserFactory
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException

class CommentersRoutes():
    """Маршруты генерации комментариев."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_routes()

    def _setup_routes(self):
        self.router.add_api_route(
            "/prompt",
            self.prompt,
            methods=["POST"],
            response_model=CommentResponse,
            summary="Генерация комментария к функции по промпту",
            description="Генерирует текст на основе промпта или сообщений"
        )

        self.router.add_api_route(
            "/extract",
            self.extract,
            methods=["POST"],
            response_model=CommentResponse,
            summary="Генерация комментария к функциям из файла",
            description="Генерирует текст на основе файла с кодом"
        )

    async def generate_comment(functions):
        BACKEND_URL = "http://localhost:8888"
        response = requests.post(
            f"{BACKEND_URL}/prompt",
            functions=functions,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
    
    async def prompt(file: UploadFile = File(...)) -> CommentResponse:
        detector = LanguageDetector()
        factory = ParserFactory()

        language = detector.detect_language(file.filename)
        if language is None:
            raise HTTPException(status_code=400, detail="Unsupported file extension")
        
        if language is not Language.PROMPT:
            raise HTTPException(status_code=400, detail="It is not prompt.")

        try:
            prompt_parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))

        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="replace")

        functions = prompt_parser.parse_content(content)
        prompt : str = functions.docstring
        code : str = functions.full_function_text

        language = detector.detect_language_patterns(code)
        if language is None:
            raise HTTPException(status_code=400, detail="Unnown language exception")
        
        try:
            language_parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        
        functions = language_parser.parse_content(code)
        if len(functions) != 1:
            

        generate_comment()

        response = CommentResponse(
            comment=result
            function=
        )

        return {
            "file": file.filename,
            "language": language.value,
            "count": len(functions),
            "functions": [f.__dict__ for f in functions],
        }

    async def extract(files: list[UploadFile] = File(...)) -> CommentResponse:
        detector = LanguageDetector()
        factory = ParserFactory()

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

        return None