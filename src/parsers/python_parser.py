from __future__ import annotations

import ast
from typing import Optional

from src.models.function_description import FunctionDescription
from src.parsers.base_parser import BaseParser
from src.models import Language


class PythonParser(BaseParser):
    def parse_content(self, content: str) -> list[FunctionDescription]:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        lines = content.splitlines(keepends=True)       # Весь код в файле.
        out: list[FunctionDescription] = []             # Результат работы функции.

        #==============================ФУНКЦИИ==============================
        def node_span(node: ast.AST) -> tuple[int, int]:
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            if start is None:
                return (1, 0)
            if end is None:
                end = start
            return (start, end)

        def slice_lines(start_1based: int, end_1based_inclusive: int) -> str:
            if end_1based_inclusive < start_1based:
                return ""
            return "".join(lines[start_1based - 1 : end_1based_inclusive])

        def build_params(fn: ast.AST) -> list[str]:
            assert isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            a = fn.args
            params: list[str] = []

            def fmt_arg(arg: ast.arg) -> str:
                if arg.annotation is None:
                    return arg.arg
                return f"{arg.arg}: {ast.unparse(arg.annotation)}"

            for arg in a.posonlyargs:
                params.append(fmt_arg(arg))
            if a.posonlyargs:
                params.append("/")

            for arg in a.args:
                params.append(fmt_arg(arg))

            if a.vararg:
                var = f"*{a.vararg.arg}"
                if a.vararg.annotation:
                    var += f": {ast.unparse(a.vararg.annotation)}"
                params.append(var)
            elif a.kwonlyargs:
                params.append("*")

            for arg in a.kwonlyargs:
                params.append(fmt_arg(arg))

            if a.kwarg:
                kw = f"**{a.kwarg.arg}"
                if a.kwarg.annotation:
                    kw += f": {ast.unparse(a.kwarg.annotation)}"
                params.append(kw)

            return params

        def build_return_type(fn: ast.AST) -> Optional[str]:
            assert isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            if fn.returns is None:
                return None
            return ast.unparse(fn.returns)

        def build_decorators(fn: ast.AST) -> list[str]:
            assert isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            return [ast.unparse(d) for d in fn.decorator_list]  # строковое представление [web:148]

        def is_docstring_expr(stmt: ast.stmt) -> bool:
            # docstring в AST — первый stmt в body вида Expr(Constant(str)) [web:188]
            return (
                isinstance(stmt, ast.Expr)
                and isinstance(getattr(stmt, "value", None), ast.Constant)
                and isinstance(stmt.value.value, str)
            )

        def build_signature_text(
            fn: ast.AST,
            *,
            decorators: list[str],
            return_type: Optional[str],
            parameters: list[str],
            is_async: bool,
        ) -> str:
            deco_lines = "".join(f"@{d}\n" for d in decorators)
            async_kw = "async " if is_async else ""
            params_joined = ", ".join(parameters)
            ret = f" -> {return_type}" if return_type else ""
            return f"{deco_lines}{async_kw}def {fn.name}({params_joined}){ret}:"

        def build_function_texts(fn: ast.AST) -> tuple[str, str, Optional[str], int, int]:
            """return (full_text, function_text_wo_docstring, docstring, ds_lines, fn_lines)."""
            assert isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))
            start, end = node_span(fn)
            full_text = slice_lines(start, end)

            doc = ast.get_docstring(fn)  # извлекает docstring функции [web:188]
            doc_lines = 0

            # По умолчанию function_text == full_text
            function_text = full_text

            if fn.body and is_docstring_expr(fn.body[0]) and doc is not None:
                ds_node = fn.body[0]
                ds_start, ds_end = node_span(ds_node)
                doc_lines = ds_end - ds_start + 1

                # Убираем docstring из текста: header до docstring + тело после docstring
                header = slice_lines(start, ds_start - 1)
                tail_start = ds_end + 1
                tail = slice_lines(tail_start, end) if tail_start <= end else ""
                function_text = header + tail

            fn_lines = end - start + 1
            return full_text, function_text, doc, doc_lines, fn_lines

        def build_modifiers(is_async: bool, decorators: list[str]) -> list[str]:
            mods: list[str] = []
            if is_async:
                mods.append("async")
            # "staticmethod"/"classmethod" как модификаторы для Python (по декораторам)
            if any(d == "staticmethod" or d.endswith(".staticmethod") for d in decorators):
                mods.append("staticmethod")
            if any(d == "classmethod" or d.endswith(".classmethod") for d in decorators):
                mods.append("classmethod")
            return mods

        def build_desc(
            fn: ast.AST,
            *,
            is_method: bool,
            class_name: Optional[str],
            class_description: Optional[str],
        ) -> FunctionDescription:
            assert isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef))

            start, end = node_span(fn)
            full_text, function_text, doc, doc_lines, full_lines = build_function_texts(fn)

            is_async = isinstance(fn, ast.AsyncFunctionDef)  # async-функции
            decorators = build_decorators(fn)
            params = build_params(fn)
            ret_type = build_return_type(fn)

            qualified_name = f"{class_name}.{fn.name}" if class_name else fn.name
            signature_text = build_signature_text(
                fn,
                decorators=decorators,
                return_type=ret_type,
                parameters=params,
                is_async=is_async,
            )

            # Длины
            full_len = full_lines
            function_len = function_text.count("\n") + (0 if function_text.endswith("\n") or function_text == "" else 1)

            return FunctionDescription(
                language=str(Language.PYTHON),
                full_function_text=full_text,
                function_text=function_text,
                docstring=doc,
                full_function_lines_length=full_len,
                function_lines_length=function_len,
                docstring_lines_length=doc_lines,
                name=fn.name,
                qualified_name=qualified_name,
                namespace=None,  # Python: можно будет позже вычислять по модулю/пакету
                signature_text=signature_text,
                return_type=ret_type,
                parameters=params,
                start_line=start,
                end_line=end,
                is_method=is_method,
                class_name=class_name,
                class_description=class_description,
                decorators=decorators,
                modifiers=build_modifiers(is_async, decorators),
                visibility=None,
                has_body=True,  # в Python у FunctionDef всегда есть body (даже если 'pass')
                is_constructor=(is_method and fn.name == "__init__"),
            )

        def visit_class(cls: ast.ClassDef) -> None:
            cls_doc = ast.get_docstring(cls)  # docstring класса [web:188]
            for stmt in cls.body:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append(
                        build_desc(
                            stmt,
                            is_method=True,
                            class_name=cls.name,
                            class_description=cls_doc,
                        )
                    )
                elif isinstance(stmt, ast.ClassDef):
                    visit_class(stmt)       # Случай рекурсивных классов
        #===========================КОНЕЦ ФУНКЦИЙ===========================

        # Обходим и обрабатываем каждую найденную функцию
        for stmt in tree.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append(
                    build_desc(
                        stmt,
                        is_method=False,
                        class_name=None,
                        class_description=None,
                    )
                )
            elif isinstance(stmt, ast.ClassDef):
                visit_class(stmt)

        return out
