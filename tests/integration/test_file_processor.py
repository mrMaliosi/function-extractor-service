# import pytest
# from pathlib import Path
# from src.core.file_processor import FileProcessor
# from src.core.parser_factory import ParserFactory

# @pytest.fixture
# def processor():
#     return FileProcessor(ParserFactory())

# def test_process_single_file(processor, tmp_path):
#     """Тест обработки одного файла"""
#     test_file = tmp_path / "test.py"
#     test_file.write_text("""
# def test_func(x, y):
#     return x + y
# """)
    
#     sigs = processor.process_file(str(test_file))
#     assert len(sigs) == 1
#     assert sigs.name == "test_func"

# def test_process_directory(processor, tmp_path):
#     """Тест обработки директории"""
#     # Создать тестовые файлы
#     (tmp_path / "file1.py").write_text("def func1(): pass")
#     (tmp_path / "file2.py").write_text("def func2(): pass")
    
#     results = processor.process_directory(str(tmp_path))
#     assert len(results) == 2

# def test_unsupported_file(processor):
#     """Тест обработки неподдерживаемого файла"""
#     with pytest.raises(ValueError):
#         processor.process_file("file.xyz")