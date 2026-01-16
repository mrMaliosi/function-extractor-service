import pytest
from src.core.language_detector import LanguageDetector, Language


@pytest.fixture
def detector():
    return LanguageDetector()


def test_detect_python(detector):
    assert detector.detect_language("a.py") == Language.PYTHON


def test_detect_javascript(detector):
    assert detector.detect_language("a.js") == Language.JAVASCRIPT
    assert detector.detect_language("a.mjs") == Language.JAVASCRIPT
    assert detector.detect_language("a.cjs") == Language.JAVASCRIPT
    assert detector.detect_language("a.jsx") == Language.JAVASCRIPT
    assert detector.detect_language("a.ts") == Language.JAVASCRIPT
    assert detector.detect_language("a.tsx") == Language.JAVASCRIPT

def test_detect_java(detector):
    assert detector.detect_language("Main.java") == Language.JAVA


def test_detect_go(detector):
    assert detector.detect_language("main.go") == Language.GO


def test_detect_csharp(detector):
    assert detector.detect_language("Program.cs") == Language.CSHARP


def test_detect_c(detector):
    assert detector.detect_language("a.c") == Language.C
    assert detector.detect_language("a.h") == Language.C


def test_detect_cpp(detector):
    assert detector.detect_language("a.cpp") == Language.CPP
    assert detector.detect_language("a.cc") == Language.CPP
    assert detector.detect_language("a.cxx") == Language.CPP
    assert detector.detect_language("a.hpp") == Language.CPP
    assert detector.detect_language("a.hh") == Language.CPP
    assert detector.detect_language("a.hxx") == Language.CPP


def test_unknown_extension(detector):
    assert detector.detect_language("a.xyz") is None


def test_case_insensitive(detector):
    assert detector.detect_language("A.PY") == Language.PYTHON
    assert detector.detect_language("/tmp/HELLO.CPP") == Language.CPP
