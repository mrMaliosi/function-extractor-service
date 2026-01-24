import json
from fastapi import HTTPException
from datetime import datetime
from src.core.language_detector import LanguageDetector, Language
from src.dto.commenters import CommentResponse, CommentRequest, GenerateRequest, GenerateResponse, Message, Choice

from src.core.language_detector import LanguageDetector, Language
from src.core.parser_factory import ParserFactory
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from src.api.base import BaseRoutes
from src.models.function_description import FunctionDescription
from src.utils.logger import SimpleLogger
from src.utils.prompt_extractor import PromptExtractorService

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

    async def prompt(self, request: Request, req: GenerateRequest) -> GenerateResponse:
        detector = LanguageDetector()
        factory = ParserFactory()
        prompt_extractor = PromptExtractorService()
        
        request_id : str = f"frogcom-{datetime.now().timestamp()}"

        data = req.model_dump(exclude_unset=True)
        try:
            prompt = prompt_extractor.extract_prompt(data)
        except Exception as e:
            self.logging_service.log_error(e, context={"Extraction error."})
            raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")
        
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Не предоставлен промпт")

        # Парсим .prompt на задачу и функцию.   
        try:
            prompt_parser = factory.get_parser(Language.PROMPT)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))

        functions : list[FunctionDescription] = prompt_parser.parse_content(prompt)
        if len(functions) != 1:
            error = "Invalid prompt format"
            self.logging_service.log_error(error, context={
                    "prompt": prompt,
                    "parsed_functions": functions,
                    "expected_functions": 1,
                    "functions_count": len(functions),
                }
            )
            raise HTTPException(status_code=400, detail=error)
        
        function : FunctionDescription = functions[0]
        prompt_task : str = function.docstring
        code : str = function.full_function_text

        # Парсим функцию.
        language = detector.detect_language_patterns(code)
        if language is None:
            error = "Unknown language"
            self.logging_service.log_error(error, context={
                    "code": code,
                    "parsed_functions": str(functions),
                })
            raise HTTPException(status_code=400, detail="Unknown language exception")

        try:
            language_parser = factory.get_parser(language)
        except NotImplementedError as e:
            raise HTTPException(status_code=501, detail=str(e))
        functions = language_parser.parse_content(code)
        if len(functions) != 1:
            error = "Неправильно распаршенный код"
            self.logging_service.log_error(error, context={
                    "code": code,
                    "parsed_functions": functions,
                    "expected_functions": 1,
                    "functions_count": len(functions),
                }
            )
            raise HTTPException(status_code=400, detail="Invalid parse")
        function = functions[0]
        
        request : CommentRequest = CommentRequest(
            task=prompt_task,
            code=code,
            function=str(function)
        )

        try:
            async def generate_comment(request : CommentRequest) -> CommentResponse:
                BACKEND_URL = "http://localhost:8888"
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{BACKEND_URL}/generate",
                        json=request.model_dump(),
                        timeout=600
                    )
                    response.raise_for_status()
                    return CommentResponse.model_validate(response.json())

            llm_response: CommentResponse = await generate_comment(request)
        except httpx.HTTPError as e:
            raise HTTPException(status_code=503, detail=f"LLM Service unavailable: {e}")
        
        # Add merge comment and code
        #answer = f"{llm_response.comment}\n{request.code}"
        answer = llm_response.comment

        response = GenerateResponse(
                id=request_id,
                created=int(datetime.now().timestamp()),
                model="frogcom",
                choices=[
                    Choice(
                        index=0,
                        message=Message(role="assistant", content=answer),
                        finish_reason="Generation success.",
                    )
                ],
            )

        return response

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