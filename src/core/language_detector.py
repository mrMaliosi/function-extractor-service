from __future__ import annotations
import re

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from src.models import Language, LANGUAGE_PATTERNS
from src.utils.logger import process_logger

@dataclass(frozen=True)
class LanguageDetector:
    """
    Определяет язык программирования по расширению файла.
    [ПРИМЕЧАНИЕ]: расширение .h неоднозначно (C/C++). На этом шаге считаем .h -> C.
    """
    
    FILE_EXTENSIONS = {
        ".py": Language.PYTHON,
        ".c": Language.C,
        ".h": Language.C,
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".cxx": Language.CPP,
        ".hpp": Language.CPP,
        ".hh": Language.CPP,
        ".hxx": Language.CPP,
        ".cs": Language.CSHARP,
        ".go": Language.GO,
        ".java": Language.JAVA,
        ".js": Language.JAVASCRIPT,
        ".mjs": Language.JAVASCRIPT,
        ".cjs": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.JAVASCRIPT,
        ".tsx": Language.JAVASCRIPT,
        ".prompt": Language.PROMPT,
    }
    
    @classmethod
    def detect_language(cls, file_path: str) -> Optional[Language]:
        """Определить язык по расширению файла"""
        ext = Path(file_path).suffix.lower()
        return cls.FILE_EXTENSIONS.get(ext)
    
    @classmethod
    def detect_language_patterns(cls, code: str) -> Optional[Language]:
        """Определить язык по языковому паттерну"""
        scores: dict[Language, int] = {lang: 0 for lang in Language}

        for lang, patterns in LANGUAGE_PATTERNS.items():
            for pattern, weight in patterns:
                if re.search(pattern, code, re.MULTILINE):
                    scores[lang] += weight

        best_lang = max(scores, key=scores.get)

        if scores[best_lang] == 0:
            return None
        
        process_logger.debug(f"Detected language={best_lang.value}, scores={scores}")

        return best_lang


    @classmethod
    def supported_languages(cls) -> list[Language]:
        """Вернуть список поддерживаемых языков"""
        return sorted(set(cls.FILE_EXTENSIONS.values()), key=lambda x: x.value)