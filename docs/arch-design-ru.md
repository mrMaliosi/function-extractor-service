# Архитектура микросервиса для выделения функций из исходного кода

## 1. Обзор системы

**Назначение:** Микросервис, извлекающий сигнатуры функций/методов из исходного кода на нескольких языках программирования.

**Поддерживаемые языки:** C, C++, C#, Go, Java, Python, JavaScript

**Результат:** Массив строк с сигнатурами функций в формате JSON

---

## 2. Выбор технологии: Python vs C++

### Сравнительный анализ

| Критерий | Python | C++ |
|----------|--------|-----|
| **Скорость разработки** | ✅✅✅ Отличная | ✅✅ Хорошая |
| **Производительность парсинга** | ✅ Приемлемая | ✅✅✅ Отличная |
| **Инструменты парсинга** | ✅✅✅ AST, libclang, tree-sitter | ✅✅ Clang API, ANTLR |
| **Простота кроссплатформенности** | ✅✅✅ Встроенная | ✅✅ Требует CMake |
| **Экосистема тестирования** | ✅✅✅ pytest, unittest | ✅✅ gtest, catch2 |
| **REST API фреймворки** | ✅✅✅ FastAPI, Flask | ✅ Crow, cpp-httplib |
| **Docker готовность** | ✅✅✅ Легко | ✅✅ Требует компиляции |

### **Рекомендация: Python**

**Обоснование:**
1. **AST встроена в стандартную библиотеку** — парсинг Python без доп. зависимостей
2. **libclang-py** — отличная поддержка C/C++/C#
3. **Tree-sitter** — универсальный парсер для Go, Java, JavaScript
4. **FastAPI** — асинхронный REST API за минуты
5. **pytest** — мощная система тестирования
6. **Быстрая итерация** при разработке
7. **Меньше кода** → меньше ошибок и проще поддержка

**Минусы Python:** Немного медленнее на CPU-bound операциях, но для парсинга файлов это некритично.

---

## 3. Архитектура микросервиса

```
┌─────────────────────────────────────────────────────────────┐
│                   GUI (Веб интерфейс)                      │
│                  React/Vue + Tailwind CSS                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────────┐
│              FastAPI Microservice                            │
├─────────────────────────────────────────────────────────────┤
│  API Routes:                                                 │
│  ├─ POST /extract      → extract_functions(file/folder)    │
│  ├─ GET  /status       → service status & statistics       │
│  ├─ POST /batch        → batch processing queue            │
│  └─ WS   /progress     → WebSocket для live updates        │
├─────────────────────────────────────────────────────────────┤
│              Core Processing Layer                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ LanguageDetector                                       │ │
│  │ ├─ detect_language(file_path) → Language             │ │
│  │ └─ supported_languages() → List[Language]            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ParserFactory                                          │ │
│  │ ├─ create_parser(Language) → Parser                   │ │
│  │ └─ get_parser(lang_name) → Parser                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Language-Specific Parsers (Abstract Base)            │   │
│  ├─ PythonParser (ast)                                  │   │
│  ├─ CppParser (libclang)                                │   │
│  ├─ CParser (libclang)                                  │   │
│  ├─ CSharpParser (tree-sitter)                          │   │
│  ├─ GoParser (tree-sitter)                              │   │
│  ├─ JavaParser (tree-sitter)                            │   │
│  └─ JavaScriptParser (tree-sitter)                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FileProcessor                                          │ │
│  │ ├─ process_file(file_path) → List[FunctionSignature] │ │
│  │ ├─ process_directory(dir) → Dict[file, signatures]   │ │
│  │ └─ validate_file(file_path) → bool                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FunctionExtractor                                      │ │
│  │ ├─ extract_signatures(ast_tree) → List[FunctionSig]  │ │
│  │ └─ format_signature(func_def) → str                  │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│              Data Models (Pydantic)                          │
│  ├─ FunctionSignature                                       │
│  ├─ ExtractionResult                                        │
│  ├─ ProcessingStatus                                        │
│  └─ ErrorResponse                                           │
├─────────────────────────────────────────────────────────────┤
│              Logging & Error Handling                        │
│  ├─ Logger (Python logging module)                          │
│  ├─ Exception handlers                                      │
│  └─ Health checks                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Структура проекта

```
function-extractor-service/
├── requirements.txt
├── pytest.ini
├── Dockerfile
├── docker-compose.yml
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI приложение
│   ├── config.py                  # Конфиг параметры
│   │
│   ├── models/                    # Pydantic модели
│   │   ├── __init__.py
│   │   ├── function_signature.py
│   │   ├── extraction_result.py
│   │   └── api_responses.py
│   │
│   ├── parsers/                   # Парсеры по языкам
│   │   ├── __init__.py
│   │   ├── base_parser.py         # Абстрактный класс
│   │   ├── python_parser.py
│   │   ├── cpp_parser.py
│   │   ├── c_parser.py
│   │   ├── csharp_parser.py
│   │   ├── go_parser.py
│   │   ├── java_parser.py
│   │   └── javascript_parser.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── language_detector.py
│   │   ├── parser_factory.py
│   │   ├── file_processor.py
│   │   └── function_extractor.py
│   │
│   ├── api/                       # API маршруты
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── websocket_handler.py
│   │   └── health.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # pytest fixtures
│   │
│   ├── unit/
│   │   ├── test_language_detector.py
│   │   ├── test_python_parser.py
│   │   ├── test_cpp_parser.py
│   │   ├── test_csharp_parser.py
│   │   ├── test_go_parser.py
│   │   ├── test_java_parser.py
│   │   └── test_javascript_parser.py
│   │
│   ├── integration/
│   │   ├── test_file_processor.py
│   │   ├── test_api_endpoints.py
│   │   └── test_batch_processing.py
│   │
│   └── fixtures/
│       ├── sample_c.c
│       ├── sample_cpp.cpp
│       ├── sample_csharp.cs
│       ├── sample_go.go
│       ├── sample_java.java
│       ├── sample_python.py
│       └── sample_javascript.js
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── app.js
│   │   ├── api.js
│   │   └── ui.js
│   └── assets/
│
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    └── INSTALLATION.md
```

---

## 5. Детальное описание компонентов

### 5.1 Language Detector

```python
from enum import Enum
from pathlib import Path

class Language(str, Enum):
    PYTHON = "python"
    C = "c"
    CPP = "cpp"
    CSHARP = "csharp"
    GO = "go"
    JAVA = "java"
    JAVASCRIPT = "javascript"

class LanguageDetector:
    """Определяет язык программирования по расширению файла"""
    
    FILE_EXTENSIONS = {
        ".py": Language.PYTHON,
        ".c": Language.C,
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".cxx": Language.CPP,
        ".h": Language.C,
        ".hpp": Language.CPP,
        ".cs": Language.CSHARP,
        ".go": Language.GO,
        ".java": Language.JAVA,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.JAVASCRIPT,
        ".tsx": Language.JAVASCRIPT,
    }
    
    @classmethod
    def detect_language(cls, file_path: str) -> Language:
        """Определить язык по расширению файла"""
        ext = Path(file_path).suffix.lower()
        return cls.FILE_EXTENSIONS.get(ext)
    
    @classmethod
    def supported_languages(cls) -> list[Language]:
        """Вернуть список поддерживаемых языков"""
        return list(set(cls.FILE_EXTENSIONS.values()))
```

### 5.2 Base Parser (Abstract Class)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class FunctionSignature:
    """Сигнатура функции"""
    name: str
    return_type: str | None
    parameters: list[str]
    line_number: int
    is_method: bool = False
    class_name: str | None = None
    
    def to_string(self) -> str:
        """Сигнатура как строка"""
        params = ", ".join(self.parameters)
        if self.return_type:
            return f"{self.return_type} {self.name}({params})"
        return f"{self.name}({params})"

class BaseParser(ABC):
    """Абстрактный класс для парсеров"""
    
    @abstractmethod
    def parse(self, file_path: str) -> list[FunctionSignature]:
        """
        Парсить файл и выделить функции
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Список сигнатур функций
        """
        pass
    
    @abstractmethod
    def parse_content(self, content: str) -> list[FunctionSignature]:
        """Парсить содержимое (строка)"""
        pass
```

### 5.3 Parser Factory

```python
from .parsers import (
    PythonParser, CppParser, CParser,
    CSharpParser, GoParser, JavaParser,
    JavaScriptParser
)

class ParserFactory:
    """Фабрика для создания парсеров"""
    
    _PARSERS = {
        Language.PYTHON: PythonParser,
        Language.C: CParser,
        Language.CPP: CppParser,
        Language.CSHARP: CSharpParser,
        Language.GO: GoParser,
        Language.JAVA: JavaParser,
        Language.JAVASCRIPT: JavaScriptParser,
    }
    
    @classmethod
    def create_parser(cls, language: Language) -> BaseParser:
        """Создать парсер для языка"""
        parser_class = cls._PARSERS.get(language)
        if not parser_class:
            raise ValueError(f"Unsupported language: {language}")
        return parser_class()
    
    @classmethod
    def get_supported_languages(cls) -> list[Language]:
        """Получить список поддерживаемых языков"""
        return list(cls._PARSERS.keys())
```

### 5.4 Python Parser (встроенный AST)

```python
import ast
from typing import Optional

class PythonParser(BaseParser):
    """Парсер для Python с использованием встроенного ast модуля"""
    
    def parse(self, file_path: str) -> list[FunctionSignature]:
        """Парсить Python файл"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> list[FunctionSignature]:
        """Парсить Python код"""
        signatures = []
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return signatures
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                sig = self._extract_function(node)
                signatures.append(sig)
            elif isinstance(node, ast.AsyncFunctionDef):
                sig = self._extract_function(node, is_async=True)
                signatures.append(sig)
        
        return signatures
    
    def _extract_function(self, node, is_async=False) -> FunctionSignature:
        """Извлечь сигнатуру функции из узла AST"""
        params = []
        for arg in node.args.args:
            params.append(arg.arg)
        
        name = f"async {node.name}" if is_async else node.name
        
        return FunctionSignature(
            name=node.name,
            return_type="async" if is_async else None,
            parameters=params,
            line_number=node.lineno,
            is_method=False  # Определяется контекстом
        )
```

### 5.5 C/C++ Parser (libclang)

```python
try:
    from clang.cindex import Index, CursorKind
    LIBCLANG_AVAILABLE = True
except ImportError:
    LIBCLANG_AVAILABLE = False

class CppParser(BaseParser):
    """Парсер для C++ с использованием libclang"""
    
    def __init__(self):
        if not LIBCLANG_AVAILABLE:
            raise RuntimeError("libclang-py не установлен")
    
    def parse(self, file_path: str) -> list[FunctionSignature]:
        """Парсить C++ файл"""
        index = Index.create()
        translation_unit = index.parse(file_path)
        return self._extract_functions(translation_unit.cursor)
    
    def parse_content(self, content: str) -> list[FunctionSignature]:
        """Парсить C++ код (требует временный файл)"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.cpp', mode='w', delete=False) as f:
            f.write(content)
            f.flush()
            return self.parse(f.name)
    
    def _extract_functions(self, cursor) -> list[FunctionSignature]:
        """Рекурсивно извлечь функции из AST"""
        signatures = []
        
        for child in cursor.get_children():
            if child.kind == CursorKind.FUNCTION_DECL:
                sig = self._create_signature(child)
                signatures.append(sig)
            elif child.kind == CursorKind.CXX_METHOD:
                sig = self._create_signature(child, is_method=True)
                signatures.append(sig)
            else:
                signatures.extend(self._extract_functions(child))
        
        return signatures
    
    def _create_signature(self, cursor, is_method=False) -> FunctionSignature:
        """Создать сигнатуру функции из курсора Clang"""
        params = []
        for token in cursor.get_tokens():
            if token.kind.name == 'IDENTIFIER':
                # Упрощенная обработка параметров
                pass
        
        return FunctionSignature(
            name=cursor.spelling,
            return_type=cursor.result_type.spelling,
            parameters=params,
            line_number=cursor.location.line,
            is_method=is_method
        )

class CParser(CppParser):
    """Парсер для C (наследует от CppParser)"""
    pass
```

### 5.6 Tree-Sitter Parsers (для Go, Java, JavaScript, C#)

```python
try:
    import tree_sitter
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

class TreeSitterParser(BaseParser):
    """Базовый класс для парсеров на Tree-Sitter"""
    
    LANGUAGE_LIB = None  # Переопределить в подклассе
    
    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise RuntimeError("tree-sitter не установлен")
        self.parser = Parser()
        self.language = Language(self.LANGUAGE_LIB)
        self.parser.set_language(self.language)
    
    def parse(self, file_path: str) -> list[FunctionSignature]:
        """Парсить файл"""
        with open(file_path, 'rb') as f:
            content = f.read()
        return self.parse_content(content.decode('utf-8'))
    
    def parse_content(self, content: str) -> list[FunctionSignature]:
        """Парсить содержимое"""
        tree = self.parser.parse(content.encode('utf-8'))
        return self._extract_functions(tree.root_node)
    
    def _extract_functions(self, node) -> list[FunctionSignature]:
        """Переопределить в подклассах"""
        return []

class GoParser(TreeSitterParser):
    """Парсер для Go"""
    LANGUAGE_LIB = "build/my-languages.so"  # Путь к скомпилированной библиотеке

class JavaParser(TreeSitterParser):
    """Парсер для Java"""
    LANGUAGE_LIB = "build/my-languages.so"

class JavaScriptParser(TreeSitterParser):
    """Парсер для JavaScript"""
    LANGUAGE_LIB = "build/my-languages.so"

class CSharpParser(TreeSitterParser):
    """Парсер для C#"""
    LANGUAGE_LIB = "build/my-languages.so"
```

### 5.7 File Processor

```python
from pathlib import Path

class FileProcessor:
    """Обработчик файлов и директорий"""
    
    SUPPORTED_EXTENSIONS = {'.py', '.c', '.cpp', '.cc', '.cxx', 
                            '.cs', '.go', '.java', '.js', '.ts'}
    
    def __init__(self, parser_factory: ParserFactory):
        self.parser_factory = parser_factory
        self.detector = LanguageDetector()
    
    def process_file(self, file_path: str) -> list[FunctionSignature]:
        """Обработать один файл"""
        path = Path(file_path)
        
        if not self._is_supported(path):
            raise ValueError(f"Unsupported file: {file_path}")
        
        language = self.detector.detect_language(file_path)
        if language is None:
            return []
        
        parser = self.parser_factory.create_parser(language)
        return parser.parse(file_path)
    
    def process_directory(self, dir_path: str, recursive=True) -> dict:
        """Обработать директорию"""
        path = Path(dir_path)
        results = {}
        
        pattern = "**/*" if recursive else "*"
        
        for file_path in path.glob(pattern):
            if file_path.is_file() and self._is_supported(file_path):
                try:
                    sigs = self.process_file(str(file_path))
                    results[str(file_path.relative_to(path))] = sigs
                except Exception as e:
                    results[str(file_path.relative_to(path))] = {"error": str(e)}
        
        return results
    
    def _is_supported(self, file_path: Path) -> bool:
        """Проверить, поддерживается ли файл"""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
```

### 5.8 FastAPI Routes

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import json

app = FastAPI(title="Function Extractor Service")

processor = FileProcessor(ParserFactory())

@app.post("/extract")
async def extract_functions(file: UploadFile = File(...)):
    """Выделить функции из загруженного файла"""
    try:
        # Сохранить временно
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp.flush()
            
            # Парсить
            signatures = processor.process_file(tmp.name)
            
            return {
                "file": file.filename,
                "language": LanguageDetector.detect_language(file.filename),
                "functions": [sig.__dict__ for sig in signatures]
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status")
async def get_status():
    """Получить статус сервиса"""
    return {
        "status": "healthy",
        "supported_languages": [lang.value for lang in LanguageDetector.supported_languages()]
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok"}
```

---

## 6. Модели данных (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, List

class FunctionSignatureModel(BaseModel):
    """Модель сигнатуры функции для API"""
    name: str
    return_type: Optional[str] = None
    parameters: List[str] = []
    line_number: int
    is_method: bool = False
    class_name: Optional[str] = None

class ExtractionResultModel(BaseModel):
    """Результат выделения функций"""
    file: str
    language: str
    functions: List[FunctionSignatureModel]
    total_count: int
    processing_time_ms: float

class ErrorResponseModel(BaseModel):
    """Ошибка обработки"""
    error: str
    file: Optional[str] = None
    details: Optional[str] = None
```

---

## 7. Автотесты

### 7.1 Unit тесты для Python парсера

```python
import pytest
from src.parsers.python_parser import PythonParser

@pytest.fixture
def parser():
    return PythonParser()

def test_simple_function(parser):
    """Тест выделения простой функции"""
    code = """
def hello(name, age):
    return f"Hello {name}"
"""
    sigs = parser.parse_content(code)
    assert len(sigs) == 1
    assert sigs[0].name == "hello"
    assert sigs[0].parameters == ["name", "age"]

def test_class_methods(parser):
    """Тест выделения методов класса"""
    code = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
"""
    sigs = parser.parse_content(code)
    assert len(sigs) == 2
    assert sigs[0].name == "add"
    assert sigs[1].name == "subtract"

def test_async_function(parser):
    """Тест выделения async функции"""
    code = """
async def fetch_data(url):
    pass
"""
    sigs = parser.parse_content(code)
    assert len(sigs) == 1
    assert sigs[0].name == "fetch_data"

def test_syntax_error_handling(parser):
    """Тест обработки ошибок синтаксиса"""
    code = "def broken("
    sigs = parser.parse_content(code)
    assert len(sigs) == 0
```

### 7.2 Unit тесты для Language Detector

```python
import pytest
from src.core.language_detector import LanguageDetector, Language

def test_detect_python():
    assert LanguageDetector.detect_language("script.py") == Language.PYTHON

def test_detect_cpp():
    assert LanguageDetector.detect_language("main.cpp") == Language.CPP
    assert LanguageDetector.detect_language("header.hpp") == Language.CPP
    assert LanguageDetector.detect_language("code.cc") == Language.CPP

def test_detect_java():
    assert LanguageDetector.detect_language("Main.java") == Language.JAVA

def test_detect_javascript():
    assert LanguageDetector.detect_language("app.js") == Language.JAVASCRIPT
    assert LanguageDetector.detect_language("types.ts") == Language.JAVASCRIPT

def test_unknown_extension():
    assert LanguageDetector.detect_language("file.xyz") is None

def test_case_insensitive():
    assert LanguageDetector.detect_language("Script.PY") == Language.PYTHON
```

### 7.3 Integration тесты для API

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    """Тест здоровья сервиса"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_status_endpoint(client):
    """Тест информации о статусе"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "supported_languages" in data
    assert len(data["supported_languages"]) > 0

def test_extract_python_file(client):
    """Тест выделения функций из Python"""
    python_code = b"""
def greet(name):
    return f"Hello {name}"
"""
    response = client.post(
        "/extract",
        files={"file": ("test.py", python_code)}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "python"
    assert len(data["functions"]) == 1
    assert data["functions"][0]["name"] == "greet"
```

### 7.4 Тесты для File Processor

```python
import pytest
from pathlib import Path
from src.core.file_processor import FileProcessor
from src.core.parser_factory import ParserFactory

@pytest.fixture
def processor():
    return FileProcessor(ParserFactory())

def test_process_single_file(processor, tmp_path):
    """Тест обработки одного файла"""
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def test_func(x, y):
    return x + y
""")
    
    sigs = processor.process_file(str(test_file))
    assert len(sigs) == 1
    assert sigs[0].name == "test_func"

def test_process_directory(processor, tmp_path):
    """Тест обработки директории"""
    # Создать тестовые файлы
    (tmp_path / "file1.py").write_text("def func1(): pass")
    (tmp_path / "file2.py").write_text("def func2(): pass")
    
    results = processor.process_directory(str(tmp_path))
    assert len(results) == 2

def test_unsupported_file(processor):
    """Тест обработки неподдерживаемого файла"""
    with pytest.raises(ValueError):
        processor.process_file("file.xyz")
```

---

## 8. Requirements.txt

```
fastapi==0.104.0
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# Парсинг
clang==15.0
tree-sitter==0.20.1
tree-sitter-python==0.20.0
tree-sitter-cpp==0.20.1
tree-sitter-java==0.20.0
tree-sitter-go==0.20.0
tree-sitter-javascript==0.20.0
tree-sitter-c-sharp==0.20.0

# Тестирование
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
httpx==0.25.0

# Разработка
black==23.12.0
flake8==6.1.0
mypy==1.7.0
```

---

## 9. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установить зависимости системы
RUN apt-get update && apt-get install -y \
    libclang-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Скопировать requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопировать код
COPY src/ ./src/
COPY tests/ ./tests/

# Выставить порт
EXPOSE 8000

# Запустить сервис
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 10. Docker Compose

```yaml
version: '3.8'

services:
  extractor-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
    volumes:
      - ./src:/app/src
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  # Опционально: веб интерфейс
  frontend:
    image: node:18-alpine
    working_dir: /app
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    command: npm start

volumes:
  logs:
```

---

## 11. GUI (Веб интерфейс)

### 11.1 HTML

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Function Extractor</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 Function Extractor</h1>
            <p>Выделите функции из исходного кода</p>
        </header>

        <main>
            <section class="upload-section">
                <div class="upload-area" id="uploadArea">
                    <svg class="upload-icon" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                    </svg>
                    <h2>Загрузите файл</h2>
                    <p>или перетащите его сюда</p>
                    <input type="file" id="fileInput" style="display:none">
                </div>
            </section>

            <section class="controls-section">
                <div class="buttons">
                    <button class="btn btn-primary" id="selectBtn">Выбрать файл</button>
                    <button class="btn btn-secondary" id="clearBtn">Очистить</button>
                </div>
            </section>

            <section class="results-section" id="resultsSection" style="display:none;">
                <h2>Результаты</h2>
                <div class="file-info">
                    <span class="file-name" id="fileName"></span>
                    <span class="language-tag" id="languageTag"></span>
                    <span class="function-count" id="functionCount"></span>
                </div>
                
                <div class="functions-list" id="functionsList"></div>
                
                <div class="export-buttons">
                    <button class="btn btn-outline" id="exportJson">📥 JSON</button>
                    <button class="btn btn-outline" id="exportCsv">📊 CSV</button>
                </div>
            </section>

            <section class="error-section" id="errorSection" style="display:none;">
                <div class="error-message" id="errorMessage"></div>
            </section>

            <section class="status-section">
                <div class="status-indicator" id="statusIndicator">●</div>
                <span id="statusText">Готово</span>
            </section>
        </main>
    </div>

    <script src="js/app.js"></script>
</body>
</html>
```

### 11.2 CSS

```css
:root {
    --primary-color: #3b82f6;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --error-color: #ef4444;
    --border-radius: 8px;
    --shadow: 0 2px 8px rgba(0,0,0,0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 20px;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--shadow);
    overflow: hidden;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 20px;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

main {
    padding: 40px;
}

.upload-area {
    border: 2px dashed var(--primary-color);
    border-radius: var(--border-radius);
    padding: 60px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #f8fafc;
}

.upload-area:hover {
    border-color: var(--secondary-color);
    background: #f1f5f9;
}

.upload-area.drag-over {
    border-color: var(--success-color);
    background: #ecfdf5;
}

.upload-icon {
    width: 60px;
    height: 60px;
    fill: var(--primary-color);
    margin-bottom: 20px;
}

.buttons {
    display: flex;
    gap: 10px;
    margin: 30px 0;
}

.btn {
    padding: 12px 24px;
    border: none;
    border-radius: var(--border-radius);
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
    transform: translateY(-2px);
    box-shadow: var(--shadow);
}

.btn-secondary {
    background: var(--secondary-color);
    color: white;
}

.btn-outline {
    border: 2px solid var(--primary-color);
    color: var(--primary-color);
    background: transparent;
}

.btn-outline:hover {
    background: var(--primary-color);
    color: white;
}

.results-section {
    margin-top: 30px;
}

.file-info {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.file-name, .language-tag, .function-count {
    padding: 8px 12px;
    background: #f1f5f9;
    border-radius: 4px;
    font-size: 0.9rem;
}

.language-tag {
    background: var(--primary-color);
    color: white;
}

.function-count {
    background: var(--success-color);
    color: white;
}

.functions-list {
    border: 1px solid #e2e8f0;
    border-radius: var(--border-radius);
    max-height: 400px;
    overflow-y: auto;
}

.function-item {
    padding: 15px;
    border-bottom: 1px solid #e2e8f0;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    background: #f8fafc;
}

.function-item:last-child {
    border-bottom: none;
}

.error-section {
    background: #fee2e2;
    border: 1px solid #fca5a5;
    border-radius: var(--border-radius);
    padding: 20px;
    color: #991b1b;
}

.status-section {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse 2s infinite;
    color: var(--success-color);
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

### 11.3 JavaScript

```javascript
const API_BASE = 'http://localhost:8000';

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const selectBtn = document.getElementById('selectBtn');
const clearBtn = document.getElementById('clearBtn');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const functionsList = document.getElementById('functionsList');

// Обработчики загрузки файла
uploadArea.addEventListener('click', () => fileInput.click());
selectBtn.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

clearBtn.addEventListener('click', () => {
    fileInput.value = '';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
    functionsList.innerHTML = '';
});

async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        updateStatus('Обработка...', 'processing');
        
        const response = await fetch(`${API_BASE}/extract`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Ошибка: ${response.statusText}`);
        }

        const data = await response.json();
        displayResults(data);
        updateStatus('Завершено', 'success');
    } catch (error) {
        showError(error.message);
        updateStatus('Ошибка', 'error');
    }
}

function displayResults(data) {
    document.getElementById('fileName').textContent = data.file;
    document.getElementById('languageTag').textContent = data.language.toUpperCase();
    document.getElementById('functionCount').textContent = `${data.functions.length} функций`;

    functionsList.innerHTML = data.functions.map(fn => `
        <div class="function-item">
            <strong>${fn.name}</strong>(${fn.parameters.join(', ')})
            ${fn.return_type ? `→ ${fn.return_type}` : ''}
            <div style="font-size: 0.8em; color: #666; margin-top: 4px;">Строка ${fn.line_number}</div>
        </div>
    `).join('');

    resultsSection.style.display = 'block';
    errorSection.style.display = 'none';
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    errorSection.style.display = 'block';
    resultsSection.style.display = 'none';
}

function updateStatus(text, status) {
    document.getElementById('statusText').textContent = text;
    const indicator = document.getElementById('statusIndicator');
    indicator.style.color = status === 'success' ? '#10b981' : 
                           status === 'error' ? '#ef4444' : '#3b82f6';
}
```

---

## 12. Команды для запуска

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск тестов
pytest tests/ -v --cov=src

# Запуск сервиса локально
uvicorn src.main:app --reload

# Запуск с Docker
docker-compose up

# Форматирование кода
black src/ tests/

# Проверка типов
mypy src/
```

---

## 13. Возможные расширения

1. **Асинхронная обработка очереди** — Redis + Celery для batch processing
2. **WebSocket** — Live updates о прогрессе обработки
3. **Кеширование результатов** — Redis cache для часто обрабатываемых файлов
4. **Аналитика** — Сбор метрик об использовании сервиса
5. **Документирование API** — Swagger UI (встроена в FastAPI)
6. **Поддержка больших файлов** — Стриминг загрузки
7. **Интеграция с версионными системами** — GitHub API для анализа репозиториев
8. **ML анализ** — Предсказание типов данных, генерация документации

---

## Итого

**Выбор: Python с FastAPI**

Эта архитектура обеспечивает:
- ✅ Поддержку 7 языков программирования
- ✅ Масштабируемость и модульность
- ✅ Полное тестовое покрытие
- ✅ REST API с WebSocket для live updates
- ✅ Современный веб-интерфейс
- ✅ Docker готовность
- ✅ Легкость развертывания и поддержки