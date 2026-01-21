from fastapi import HTTPException

from src.core.language_detector import LanguageDetector, Language
from src.dto.commenters import CommentResponse, CommentRequest

from src.core.language_detector import LanguageDetector, Language
from src.core.parser_factory import ParserFactory
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from src.utils.logger import SimpleLogger
from src.api.base import BaseRoutes
from src.models.function_description import FunctionDescription
class CommentersRoutes(BaseRoutes):
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

    async def prompt(self, file: UploadFile = File(...)) -> CommentResponse:
        detector = LanguageDetector()
        factory = ParserFactory()

        # Парсим .prompt на задачу и функцию.
        language = detector.detect_language(file.filename)      
        if language is not Language.PROMPT:
            raise HTTPException(status_code=400, detail="It is not prompt file extension.")
        try:
            prompt_parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        content_bytes = await file.read()
        content = content_bytes.decode("utf-8", errors="replace")
        functions : list[FunctionDescription] = prompt_parser.parse_content(content)
        if len(functions) != 1:
            my_log: SimpleLogger = SimpleLogger("PromptRoute").get_logger()
            my_log.debug("Неправильно распаршенный промпт:\n" + str(content) + "\n[СТАЛО]:\n" + str(functions))
            raise HTTPException(status_code=400, detail="Invalid prompt format")
        
        function : FunctionDescription = functions[0]
        prompt : str = function.docstring
        code : str = function.full_function_text

        # Парсим функцию.
        language = detector.detect_language_patterns(code)
        if language is None:
            raise HTTPException(status_code=400, detail="Unnown language exception")
        try:
            language_parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        functions = language_parser.parse_content(code)
        if len(functions) != 1:
            my_log: SimpleLogger = SimpleLogger("PromptRoute").get_logger()
            my_log.debug("Неправильно распаршенный запрос:\n" + str(code) + "\n[СТАЛО]:\n" + str(functions))
            raise HTTPException(status_code=400, detail="Invalid parse")
        function = functions[0]
        
        request: CommentRequest = CommentRequest(prompt, code, str(function))

        try:
            async def generate_comment(request : CommentRequest) -> CommentResponse:
                BACKEND_URL = "http://localhost:8888"
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{BACKEND_URL}/prompt",
                        json=request.model_dump(),
                        timeout=30.0
                    )
                    response.raise_for_status()
                    return CommentResponse.model_validate(response.json())

            llm_response: CommentResponse = await generate_comment(request)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"LLM Service unavailable: {e}")

        return llm_response

    async def extract(self, files: list[UploadFile] = File(...)) -> CommentResponse:
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