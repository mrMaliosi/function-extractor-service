import json
import os
import logging
from typing import Dict, Any
from src.config import LoggingConfig
from datetime import datetime, timedelta

class SimpleLogger:
    def __init__(self, name):
        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # Формат сообщений
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

            # 1. Обработчик для записи в файл
            file_handler = logging.FileHandler(name + ".log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            # 2. Обработчик для вывода в консоль
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)

            # Добавляем обработчики к логгеру
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_error(self, problem: str, context: Dict[str, Any] = None) -> None:
        """Логирует ошибку."""
        error_data = {
            "problem": str(problem),
            "context": context or {},
        }
        self._log_data(error_data, "ERROR")

    def log_exception(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Логирует ошибку."""
        error_data = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context or {},
        }
        self._log_data(error_data, "ERROR")

    def debug(self, context: str = None) -> None:
        """Логирует дебаг информацию."""
        debug_data = {
            "context": context or {},
        }
        self._log_data(debug_data, "DEBUG")

    def _log_data(self, data: Dict[str, Any], log_type: str) -> None:
        """Записывает данные в лог файл."""
        self.logger.debug(f"{log_type}: {json.dumps(data, ensure_ascii=False, indent=2)}")

    def get_logger(self):
        return self.logger
    
error_logger = SimpleLogger("err")
process_logger = SimpleLogger("process")