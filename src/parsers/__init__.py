"""
Parsers module - парсеры для разных языков программирования
"""

from src.parsers.base_parser import BaseParser
from src.parsers.python_parser import PythonParser

try:
    from src.parsers.csharp_parser import CSharpParser
except ImportError:
    CSharpParser = None

try:
    from src.parsers.c_parser import CParser
except ImportError:
    CSharpParser = None

try:
    from src.parsers.cpp_parser import CppParser
except ImportError:
    CSharpParser = None

try:
    from src.parsers.go_parser import GoParser
except ImportError:
    GoParser = None

try:
    from src.parsers.java_parser import JavaParser
except ImportError:
    JavaParser = None

try:
    from src.parsers.javascript_parser import JavaScriptParser
except ImportError:
    JavaScriptParser = None

try:
    from src.parsers.prompt_parser import PromptParser
except ImportError:
    PromptParser = None

__all__ = [
    "BaseParser",
    "FunctionSignature",
    "PythonParser",
    "CppParser",
    "CParser",
    "CSharpParser",
    "GoParser",
    "JavaParser",
    "JavaScriptParser",
    "PromptParser",
]