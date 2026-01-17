from __future__ import annotations

from src.core.language_detector import Language
from src.parsers.base_parser import BaseParser
from src.parsers.python_parser import PythonParser
from src.parsers.java_parser import JavaParser


class ParserFactory:
    """Фабрика парсеров по Language."""

    _registry: dict[Language, type[BaseParser]] = {
        Language.PYTHON: PythonParser,
        Language.JAVA: JavaParser,
        # Дальше добавим: C/C++/C#/Go/Java/JS
    }

    def get_parser(self, language: Language) -> BaseParser:
        parser_cls = self._registry.get(language)
        if not parser_cls:
            raise NotImplementedError(f"Parser for language '{language.value}' is not implemented")
        return parser_cls()


# from src.parsers import (
#     PythonParser, CppParser, CParser,
#     CSharpParser, GoParser, JavaParser,
#     JavaScriptParser
# )

# class ParserFactory:
#     """Фабрика для создания парсеров"""
    
#     _PARSERS = {
#         Language.PYTHON: PythonParser,
#         Language.C: CParser,
#         Language.CPP: CppParser,
#         Language.CSHARP: CSharpParser,
#         Language.GO: GoParser,
#         Language.JAVA: JavaParser,
#         Language.JAVASCRIPT: JavaScriptParser,
#     }
    
#     @classmethod
#     def create_parser(cls, language: Language) -> BaseParser:
#         """Создать парсер для языка"""
#         parser_class = cls._PARSERS.get(language)
#         if not parser_class:
#             raise ValueError(f"Unsupported language: {language}")
#         return parser_class()
    
#     @classmethod
#     def get_supported_languages(cls) -> list[Language]:
#         """Получить список поддерживаемых языков"""
#         return list(cls._PARSERS.keys())