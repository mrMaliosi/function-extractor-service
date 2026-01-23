import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from src.models.function_description import FunctionDescription
from src.parsers.base_parser import BaseParser

class JavaParser(BaseParser):
    """
    Продвинутый Java-парсер:
    - Исправлен захват тела метода (счетчик скобок вместо regex)
    - Игнорирование конструкций throw/return/new в начале строки
    - Поддержка <T> generics в сигнатуре метода
    - Корректная обработка отступов и форматирования в Javadoc
    """

    # Паттерн для поиска классов
    _class_pattern = re.compile(
        r"(?P<comments>(?:/\*\*.*?\*/\s*|//.*\n)*)"
        r"(?P<modifiers>(?:public|private|protected|abstract|final|static|\s)+)?\s*"
        r"(?P<type>class|interface|enum)\s+"
        r"(?P<name>\w+)"
        r"(\s*<[^>]+>)?", 
        re.DOTALL
    )

    # Паттерн заголовка метода
    # Обрабатывает Javadoc и аннотации с произвольными отступами
    _method_header_pattern = re.compile(
        r"(?m)"  # Multiline mode
        # 1. Javadoc и комментарии (жадный захват, допускает отступы)
        r"(?P<comments>(?:(?:^[ \t]*)(?:/\*\*.*?\*/|//[^\n]*)\s*)+)?"
        
        # 2. Аннотации
        r"(?P<annotations>(?:(?:^[ \t]*)(?:@\w+(?:\([^\)]*\))?)\s*)+)?"
        
        # 3. Начало сигнатуры (строго с начала строки с учетом отступа)
        r"(?:^[ \t]*)" 
        # Negative lookahead: исключаем throw, return, new, if, else и т.д.
        r"(?!(?:throw|return|new|catch|if|else|try|break|case)\b)"
        
        r"(?P<modifiers>(?:public|private|protected|static|final|abstract|synchronized|strictfp|default|native|transient|volatile|\s)+)?"
        r"(?P<type_params><[\w\s,extends\?\[\]]+>\s+)??" 
        r"(?P<return_type>[\w\<\>\[\], ?]+)\s+"
        r"(?P<name>(?!for\b|while\b|if\b|else\b|switch\b|catch\b|synchronized\b|return\b|throw\b|try\b|new\b|break\b|continue\b|assert\b)\w+)\s*"
        r"\((?P<params>(?:[^)(]+|\((?:[^)(]+|\([^)(]*\))*\))*)\)\s*"
        r"(?:throws\s+[^{;]+)?\s*"
        r"(?P<terminator>[{;])", 
        re.DOTALL
    )

    def parse_content(self, content: str) -> List[FunctionDescription]:
        functions: List[FunctionDescription] = []

        def find_classes(text: str, parent: Optional[str] = None, offset: int = 0):
            matches = list(self._class_pattern.finditer(text))
            processed_ranges = []
            
            for class_match in matches:
                # Пропускаем вложенные классы (они будут обработаны рекурсивно)
                if any(start <= class_match.start() < end for start, end in processed_ranges):
                    continue

                start_idx = class_match.end()
                body, end_idx = self._extract_braces_content(text, start_idx - 1)
                
                processed_ranges.append((class_match.start(), end_idx))
                
                name = class_match.group("name")
                type_ = class_match.group("type")
                doc = self._clean_docstring(class_match.group("comments"))
                
                qualified_class_name = f"{parent}.{name}" if parent else name
                current_body_offset = offset + start_idx
                
                # Парсим методы текущего класса
                class_methods = self._parse_methods(
                    body,
                    qualified_class_name,
                    name,
                    type_,
                    doc,
                    current_body_offset
                )
                functions.extend(class_methods)
                
                # Рекурсивно ищем классы внутри текущего
                find_classes(body, qualified_class_name, current_body_offset)

        find_classes(content)
        if len(functions) == 0:
            functions = self._parse_methods(content, None, None, None, None, 0)

        print(functions)
        return functions

    def _parse_methods(
        self, 
        class_body: str, 
        qualified_class_name: str, 
        class_name: str, 
        class_type: str, 
        class_doc: Optional[str],
        body_offset: int
    ) -> List[FunctionDescription]:
        methods = []
        pos = 0
        nested_ranges = self._get_nested_class_ranges(class_body)

        while True:
            match = self._method_header_pattern.search(class_body, pos)
            if not match:
                break
            
            # Пропускаем методы внутри вложенных классов
            if self._is_in_nested_class(match.start(), nested_ranges):
                pos = match.end()
                continue
            
            terminator = match.group("terminator")
            match_end = match.end()
            
            # Извлекаем тело метода
            if terminator == ';':
                method_body = ";"
                full_method_end = match_end
                has_body = False
            else:
                brace_start_idx = match_end - 1 
                body_content, body_end_idx = self._extract_braces_content(class_body, brace_start_idx)
                method_body = "{" + body_content + "}"
                full_method_end = body_end_idx
                has_body = True

            # Метаданные
            comments = self._clean_docstring(match.group("comments"))
            annotations = [a.strip() for a in (match.group("annotations") or "").splitlines() if a.strip()]
            
            modifiers_str = match.group("modifiers")
            modifiers = modifiers_str.split() if modifiers_str else []
            
            if class_type == "interface":
                if not modifiers:
                    modifiers = ["public", "abstract"]
                if not has_body and "default" not in modifiers and "static" not in modifiers:
                     if "abstract" not in modifiers:
                         modifiers.append("abstract")

            visibility = next((v for v in ["public", "private", "protected"] if v in modifiers), "package-private")
            
            raw_ret = match.group("return_type") or ""
            return_type = raw_ret.strip().split()[-1] if raw_ret else None

            name = match.group("name")
            params_text = match.group("params")
            parameters = self._split_params(params_text)

            start_line = class_body[:match.start()].count("\n") + body_offset + 1
            full_text = class_body[match.start():full_method_end]
            end_line = start_line + full_text.count("\n")

            func_desc = FunctionDescription(
                full_function_text=full_text,
                function_text=method_body,
                docstring=comments,
                full_function_lines_length=full_text.count("\n") + 1,
                function_lines_length=method_body.count("\n") + 1,
                docstring_lines_length=comments.count("\n") + 1 if comments else None,
                name=name,
                qualified_name=f"{qualified_class_name}.{name}",
                namespace=None,
                signature_text=f"{return_type or 'void'} {name}({params_text})",
                return_type=return_type,
                parameters=parameters,
                start_line=start_line,
                end_line=end_line,
                is_method=True,
                class_name=qualified_class_name,
                class_description=class_doc,
                decorators=annotations,
                modifiers=modifiers,
                visibility=visibility,
                has_body=has_body,
                is_constructor=name == class_name
            )
            methods.append(func_desc)
            pos = full_method_end

        return methods

    def _get_nested_class_ranges(self, text: str) -> List[Tuple[int, int]]:
        ranges = []
        for match in self._class_pattern.finditer(text):
            start = match.start()
            idx = text.find("{", match.end())
            if idx != -1:
                _, end = self._extract_braces_content(text, idx)
                ranges.append((start, end))
        return ranges

    def _is_in_nested_class(self, pos: int, nested_ranges: List[Tuple[int, int]]) -> bool:
        for start, end in nested_ranges:
            if start <= pos < end:
                return True
        return False

    def _split_params(self, params_text: str) -> List[str]:
        if not params_text:
            return []
        params = []
        depth = 0
        current = []
        for char in params_text:
            if char == ',' and depth == 0:
                params.append("".join(current).strip())
                current = []
            else:
                current.append(char)
                if char == '<': depth += 1
                elif char == '>': depth -= 1
        if current:
            params.append("".join(current).strip())
        return [p for p in params if p]

    def _clean_docstring(self, text: Optional[str]) -> Optional[str]:
        """
        Очищает Javadoc от маркеров /**, *, */ и лишних отступов.
        Сохраняет пустые строки-разделители внутри текста.
        """
        if not text:
            return None
            
        # Убираем внешние маркеры комментария
        text = text.strip()
        if text.startswith("/**"):
            text = text[3:]
        elif text.startswith("/*"):
            text = text[2:]
        if text.endswith("*/"):
            text = text[:-2]
            
        lines = []
        for line in text.splitlines():
            # Если это обычный комментарий //
            if line.strip().startswith("//"):
                content = line.strip()[2:]
                lines.append(content.strip())
                continue

            # Javadoc: убираем начальные пробелы и звездочку
            # Регулярка убирает: начало строки, любые пробелы, звездочку, опциональный пробел после
            line = re.sub(r"^\s*\*\s?", "", line)
            
            # Убираем пробелы по краям самого текста строки
            cleaned = line.strip()
            lines.append(cleaned)
        
        # Удаляем пустые строки ТОЛЬКО в начале и в конце списка (trimming),
        # но оставляем внутренние пустые строки (например, перед @param)
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
            
        return "\n".join(lines) if lines else None

    def _extract_braces_content(self, text: str, start_idx: int) -> Tuple[str, int]:
        if start_idx >= len(text) or text[start_idx] != "{":
            next_brace = text.find("{", start_idx)
            if next_brace == -1:
                return "", start_idx
            start_idx = next_brace

        stack = 1
        i = start_idx + 1
        length = len(text)
        
        while i < length:
            char = text[i]
            if char == '{':
                stack += 1
            elif char == '}':
                stack -= 1
                if stack == 0:
                    return text[start_idx + 1:i], i + 1
            i += 1
            
        return text[start_idx + 1:], length
