from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class FunctionDescription:
    """Унифицированное описание функции/метода для всех парсеров."""
    language: str

    # Тексты и длины текстов
    full_function_text: str = None         # полный текст самой функции и комментарий к ней
    function_text: str = None              # сама функция без комментария
    docstring: Optional[str] = None        # комментарий к функции
    full_function_lines_length: int = 0    # число строк в коде, из которых состоит вся функция
    function_lines_length: int = 0         # число строк в коде, из которых состоит сама функция
    docstring_lines_length: Optional[int] = 0  # число строк в коде, из которых состоит комментарий
    
    # Идентификация
    name: str = None                    # имя функции
    qualified_name: str = None          # например: "A.m" или "foo"
    namespace: Optional[str] = None     # C++ namespace / Java package / C# namespace

    # Сигнатура
    signature_text: str = ""               # "def f(a: int) -> int"
    return_type: Optional[str] = None
    parameters: list[str] = field(default_factory=list)        # список строк-параметров
    
    # Позиция
    start_line: int = -1                     # номер строки в исходном файле с которого начинается функция
    end_line: int = -1
    
    # Контекст
    is_method: bool = False
    class_name: Optional[str] = None
    class_description: Optional[str] = None    # комментарий к классу, если есть

    # Доп. атрибуты (универсальные)
    decorators: list[str] = field(default_factory=list)        # Python decorators / Java annotations
    modifiers: list[str] = field(default_factory=list)         # public/private/static/virtual/async/...
    visibility: Optional[str] = None    # public/private/protected/internal/...
    has_body: bool = True                                 # для прототипов/abstract/interface
    is_constructor: bool = False

    def to_string(self) -> str:
        """Сигнатура как строка"""
        params = ", ".join(self.parameters)
        if self.return_type:
            return f"{self.return_type} {self.name}({params})"
        return f"{self.name}({params})"