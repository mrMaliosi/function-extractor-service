# try:
#     import tree_sitter
#     from tree_sitter import Language, Parser
#     TREE_SITTER_AVAILABLE = True
# except ImportError:
#     TREE_SITTER_AVAILABLE = False

# class TreeSitterParser(BaseParser):
#     """Базовый класс для парсеров на Tree-Sitter"""
    
#     LANGUAGE_LIB = None  # Переопределить в подклассе
    
#     def __init__(self):
#         if not TREE_SITTER_AVAILABLE:
#             raise RuntimeError("tree-sitter не установлен")
#         self.parser = Parser()
#         self.language = Language(self.LANGUAGE_LIB)
#         self.parser.set_language(self.language)
    
#     def parse(self, file_path: str) -> list[FunctionSignature]:
#         """Парсить файл"""
#         with open(file_path, 'rb') as f:
#             content = f.read()
#         return self.parse_content(content.decode('utf-8'))
    
#     def parse_content(self, content: str) -> list[FunctionSignature]:
#         """Парсить содержимое"""
#         tree = self.parser.parse(content.encode('utf-8'))
#         return self._extract_functions(tree.root_node)
    
#     def _extract_functions(self, node) -> list[FunctionSignature]:
#         """Переопределить в подклассах"""
#         return []

# class GoParser(TreeSitterParser):
#     """Парсер для Go"""
#     LANGUAGE_LIB = "build/my-languages.so"  # Путь к скомпилированной библиотеке

# class JavaParser(TreeSitterParser):
#     """Парсер для Java"""
#     LANGUAGE_LIB = "build/my-languages.so"

# class JavaScriptParser(TreeSitterParser):
#     """Парсер для JavaScript"""
#     LANGUAGE_LIB = "build/my-languages.so"

# class CSharpParser(TreeSitterParser):
#     """Парсер для C#"""
#     LANGUAGE_LIB = "build/my-languages.so"