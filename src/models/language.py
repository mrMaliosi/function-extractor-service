import re
from enum import Enum
from typing import Optional


class Language(str, Enum):
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    PROMPT = "prompt"
    
    def __str__(self) -> str:
        """Возвращает строковое представление языка программирования."""
        return str(self.value)


LANGUAGE_PATTERNS: dict[Language, list[tuple[str, int]]] = {
    Language.PYTHON: [
        (r'^\s*def\s+\w+\(.*\):', 5),
        (r'^\s*class\s+\w+\(?.*\)?:', 3),
        (r'import\s+\w+', 1),
    ],

    Language.GO: [
        (r'^\s*func\s+\w+\(.*\)', 5),
        (r':=', 2),
        (r'\bpackage\s+\w+', 2),
    ],

    Language.JAVA: [
        (r'\b(public|private|protected)\s+[\w<>]+\s+\w+\s*\(', 5),
        (r'\bthrow new\b', 3),
        (r'\bnew\s+\w+\(', 2),
        (r'<[A-Z]>', 2),  # generics
    ],

    Language.CSHARP: [
        (r'\busing\s+system\b', 4),
        (r'\bnamespace\s+\w+', 3),
        (r'\bConsole\.WriteLine\b', 3),
    ],

    Language.JAVASCRIPT: [
        (r'\bfunction\s+\w+\s*\(', 4),
        (r'\bconst\s+\w+\s*=', 2),
        (r'\bconsole\.log\b', 3),
        (r'=>', 2),
    ],
}
