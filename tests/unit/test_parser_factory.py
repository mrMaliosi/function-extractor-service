import pytest

from src.core.language_detector import Language
from src.core.parser_factory import ParserFactory
from src.parsers.python_parser import PythonParser


@pytest.fixture
def factory():
    return ParserFactory()


def test_factory_returns_python_parser(factory):
    parser = factory.get_parser(Language.PYTHON)
    assert isinstance(parser, PythonParser)


def test_factory_unsupported_language_raises(factory):
    with pytest.raises(NotImplementedError):
        factory.get_parser(Language.JAVA)
