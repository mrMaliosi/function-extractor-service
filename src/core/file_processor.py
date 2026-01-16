# from pathlib import Path

# class FileProcessor:
#     """Обработчик файлов и директорий"""
    
#     SUPPORTED_EXTENSIONS = {'.py', '.c', '.cpp', '.cc', '.cxx', 
#                             '.cs', '.go', '.java', '.js', '.ts'}
    
#     def __init__(self, parser_factory: ParserFactory):
#         self.parser_factory = parser_factory
#         self.detector = LanguageDetector()
    
#     def process_file(self, file_path: str) -> list[FunctionSignature]:
#         """Обработать один файл"""
#         path = Path(file_path)
        
#         if not self._is_supported(path):
#             raise ValueError(f"Unsupported file: {file_path}")
        
#         language = self.detector.detect_language(file_path)
#         if language is None:
#             return []
        
#         parser = self.parser_factory.create_parser(language)
#         return parser.parse(file_path)
    
#     def process_directory(self, dir_path: str, recursive=True) -> dict:
#         """Обработать директорию"""
#         path = Path(dir_path)
#         results = {}
        
#         pattern = "**/*" if recursive else "*"
        
#         for file_path in path.glob(pattern):
#             if file_path.is_file() and self._is_supported(file_path):
#                 try:
#                     sigs = self.process_file(str(file_path))
#                     results[str(file_path.relative_to(path))] = sigs
#                 except Exception as e:
#                     results[str(file_path.relative_to(path))] = {"error": str(e)}
        
#         return results
    
#     def _is_supported(self, file_path: Path) -> bool:
#         """Проверить, поддерживается ли файл"""
#         return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS