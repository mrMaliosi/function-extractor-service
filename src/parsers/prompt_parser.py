from __future__ import annotations

import re
import ast
from typing import Optional

from src.models.function_description import FunctionDescription
from src.parsers.base_parser import BaseParser
from src.utils.logger import process_logger, error_logger

class PromptParser(BaseParser):
    def parse_content(self, content: str) -> list[FunctionDescription]:
        lines = content.splitlines(keepends=True)       # Весь код в файле.
        out: list[FunctionDescription] = []             # Результат работы функции.

        GENERIC_CODE_RE = re.compile(
            r"""
            ^\s*(
                @|
                (def|class|public|private|protected|func|function)\s|
                .*[\{\};].*|
                .*->.*|
                .*=>.*
            )
            """,
            re.VERBOSE
        )

        code_start = None
        for i, line in enumerate(lines):
            if GENERIC_CODE_RE.match(line):
                code_start = i
                break

        if code_start is None:
            error_logger.debug("Не найдено начало кода для запроса:\n" + str(lines))
            return None

        prompt = "".join(lines[:code_start]).strip()
        code = "".join(lines[code_start:]).strip()

        fd = FunctionDescription(
                full_function_text=code,
                function_text=None,
                docstring=prompt,
            )
        
        process_logger.debug(f"Prompt:\n{prompt}\nCode:\n{code}")
        
        out.append(fd)
        return out