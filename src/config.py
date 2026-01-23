import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

@dataclass
class LoggingConfig:
    """Конфигурация системы логирования."""
    
    log_dir: str = "logs"
    log_file: str = "err.log"
    
    @property
    def log_file_path(self) -> Path:
        """Полный путь к файлу логов."""
        return Path(self.log_dir) / self.log_file
