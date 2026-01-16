import pytest
from src.parsers.python_parser import PythonParser


@pytest.fixture
def parser():
    return PythonParser()


def test_function_signature_and_docstring(parser):
    code = '''\
def f(a: int, b) -> int:
    """doc"""
    return a
'''
    res = parser.parse_content(code)
    assert len(res) == 1
    fd = res[0]

    assert fd.name == "f"
    assert fd.qualified_name == "f"
    assert fd.start_line == 1
    assert fd.end_line >= 1
    assert fd.docstring == "doc"
    assert fd.docstring_lines_length >= 1
    assert "def f(" in fd.signature_text
    assert "-> int" in fd.signature_text
    assert fd.parameters[0].startswith("a")
    assert fd.has_body is True

def test_function_signature_and_before_docstrings(parser):
    code = '''\
"""doc"""
def f(a: int, b) -> int:
    return a
'''
    res = parser.parse_content(code)
    assert len(res) == 1
    fd = res[0]

    assert fd.name == "f"
    assert fd.qualified_name == "f"
    assert fd.start_line == 2
    assert fd.end_line >= 1
    assert fd.docstring == None
    assert fd.docstring_lines_length == 0
    assert "def f(" in fd.signature_text
    assert "-> int" in fd.signature_text
    assert fd.parameters[0].startswith("a")
    assert fd.has_body is True

def test_function_signature_noisy(parser):
    code = '''\
def    f  ( a : int , b )  ->  int  :  
    return a
'''
    res = parser.parse_content(code)
    assert len(res) == 1
    fd = res[0]

    assert fd.name == "f"
    assert fd.qualified_name == "f"
    assert fd.start_line == 1
    assert fd.end_line == 2
    assert fd.docstring == None
    assert fd.docstring_lines_length == 0
    assert "def f(a: int, b) -> int:" in fd.signature_text
    assert fd.parameters[0] == "a: int"
    assert fd.parameters[1] == "b"
    assert fd.has_body is True

def test_decorators_and_async(parser):
    code = '''\
@dec1
@pkg.dec2(1)
async def g(x):
    return x
'''
    res = parser.parse_content(code)
    fd = res[0]
    assert "async" in fd.modifiers
    assert len(fd.decorators) == 2
    assert "dec1" in fd.decorators[0]


def test_constructor_and_class_doc(parser):
    code = '''\
class A:
    """class doc"""
    def __init__(self, x):
        """ctor doc"""
        self.x = x
'''
    res = parser.parse_content(code)
    fd = res[0]
    assert fd.is_method is True
    assert fd.class_name == "A"
    assert fd.class_description == "class doc"
    assert fd.is_constructor is True
