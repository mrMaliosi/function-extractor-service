# """
# API Response Models - Pydantic модели для ответов API
# """

# from pydantic import BaseModel, Field
# from typing import Optional, List
# from src.models.function_signature import FunctionSignatureModel


# class HealthResponseModel(BaseModel):
#     """Ответ на проверку здоровья"""
#     status: str = Field(..., description="Статус сервиса: 'ok'")
    
#     class Config:
#         json_schema_extra = {
#             "example": {"status": "ok"}
#         }


# class StatusResponseModel(BaseModel):
#     """Ответ со статусом сервиса"""
#     status: str = Field(..., description="Статус: 'healthy' или 'unhealthy'")
#     uptime_seconds: float = Field(..., description="Время работы сервиса в секундах")
#     supported_languages: List[str] = Field(..., description="Список поддерживаемых языков")
#     total_requests: int = Field(..., description="Всего обработано запросов")
#     successful_extractions: int = Field(..., description="Успешных обработок")
#     failed_extractions: int = Field(..., description="Неудачных обработок")
#     total_functions_extracted: int = Field(..., description="Всего выделено функций")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "status": "healthy",
#                 "uptime_seconds": 3600.5,
#                 "supported_languages": ["python", "cpp", "c", "go", "java", "javascript", "csharp"],
#                 "total_requests": 150,
#                 "successful_extractions": 145,
#                 "failed_extractions": 5,
#                 "total_functions_extracted": 2500,
#             }
#         }


# class ExtractionResultModel(BaseModel):
#     """Результат выделения функций"""
#     file: str = Field(..., description="Имя файла")
#     language: str = Field(..., description="Язык программирования")
#     functions: List[FunctionSignatureModel] = Field(..., description="Массив сигнатур функций")
#     total_count: int = Field(..., description="Количество найденных функций")
#     processing_time_ms: float = Field(..., description="Время обработки в миллисекундах")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "file": "example.py",
#                 "language": "python",
#                 "functions": [
#                     {
#                         "name": "calculate_sum",
#                         "return_type": "int",
#                         "parameters": ["a: int", "b: int"],
#                         "line_number": 1,
#                         "is_method": False,
#                         "class_name": None,
#                     }
#                 ],
#                 "total_count": 1,
#                 "processing_time_ms": 15.5,
#             }
#         }


# class ErrorResponseModel(BaseModel):
#     """Ошибка API"""
#     error: str = Field(..., description="Описание ошибки")
#     file: Optional[str] = Field(None, description="Имя файла (если применимо)")
#     details: Optional[str] = Field(None, description="Дополнительные детали")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "error": "Unsupported file format: .xyz",
#                 "file": "unknown.xyz",
#                 "details": "Please use one of: .py, .cpp, .c, .cs, .go, .java, .js",
#             }
#         }
