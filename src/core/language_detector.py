from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

class Language(str, Enum):
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"

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
    }
    
    @classmethod
    def detect_language(cls, file_path: str) -> Optional[Language]:
        """Определить язык по расширению файла"""
        ext = Path(file_path).suffix.lower()
        return cls.FILE_EXTENSIONS.get(ext)
    
    @classmethod
    def supported_languages(cls) -> list[Language]:
        """Вернуть список поддерживаемых языков"""
        return sorted(set(cls.FILE_EXTENSIONS.values()), key=lambda x: x.value)