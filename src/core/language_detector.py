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
    PROMPT = "prompt"

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
        # 1. Проверка Python (def + двоеточие, специфичные отступы)
        if 'def ' in code and ':' in code:
            return Language.PYTHON
        
        # 2. Проверка Go (func + специфичные пакеты)
        if 'func ' in code or 'fmt.' in code or ':=' in code:
            return Language.GO
        
        # 3. JavaScript (console.log, function без типов)
        # Важно проверить до Java/C#, так как 'function' может встречаться и там в комментариях
        if 'console.log' in code or 'document.' in code or '===' in code:
            return Language.JAVASCRIPT
        
        # 4. Различие Java и C# (самая сложная пара, так как синтаксис похож)
        if 'using system' in code or 'console.writeline' in code or 'namespace ' in code:
            return Language.CSHARP
            
        if 'system.out.println' in code or 'import java' in code or 'public static void main' in code:
            return Language.JAVA

        # Дополнительная проверка для коротких JS функций (если нет console.log)
        if 'function ' in code and '{' in code:
            return Language.JAVASCRIPT

    @classmethod
    def supported_languages(cls) -> list[Language]:
        """Вернуть список поддерживаемых языков"""
        return sorted(set(cls.FILE_EXTENSIONS.values()), key=lambda x: x.value)