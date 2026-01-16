from __future__ import annotations
from abc import ABC, abstractmethod
from src.models.function_description import FunctionDescription

class BaseParser(ABC):
    """Базовый интерфейс парсера языка."""

    @abstractmethod
    def parse_content(self, content: str) -> list[FunctionDescription]:
        """Вернуть список строк (каждая строка — выделенная функция/метод)."""
        raise NotImplementedError



# from abc import ABC, abstractmethod
# from dataclasses import dataclass



# class BaseParser(ABC):
#     """Абстрактный класс для парсеров"""
    
#     @abstractmethod
#     def parse(self, file_path: str) -> list[FunctionSignature]:
#         """
#         Парсить файл и выделить функции
        
#         Args:
#             file_path: Путь к файлу
            
#         Returns:
#             Список сигнатур функций
#         """
#         pass
    
#     @abstractmethod
#     def parse_content(self, content: str) -> list[FunctionSignature]:
#         """Парсить содержимое (строка)"""
#         pass