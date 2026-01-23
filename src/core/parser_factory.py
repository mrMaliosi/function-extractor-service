from __future__ import annotations

from src.core.language_detector import Language
from src.parsers.base_parser import BaseParser
from src.parsers import *


class ParserFactory:
    """Фабрика парсеров по Language."""

    _registry: dict[Language, type[BaseParser]] = {
        Language.PYTHON: PythonParser,
        Language.JAVA: JavaParser,
        Language.PROMPT: PromptParser,
        # Дальше добавим: C/C++/C#/Go/Java/JS
    }

    def get_parser(self, language: Language) -> BaseParser:
        parser_cls = self._registry.get(language)
        if not parser_cls:
            raise NotImplementedError(f"Parser for language '{language.value}' is not implemented")
        return parser_cls()