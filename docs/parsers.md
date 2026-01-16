Идеи расширения структуры (на будущее)

То, что обычно реально полезно и добываемо большинством парсеров:

    visibility: str | None (public/private/protected) — актуально для C++/C#/Java.

    decorators/annotations: list[str] — Python/Java/C#.

    modifiers: list[str] (static, virtual, override, async) — Java/C#/C++.

    namespace/package: str | None — C++/Java.

    calls: list[str] (список вызванных функций) — можно позже через AST-проход.


завести отдельное поле под module docstring

Если тебе важно сохранять информацию про модульный комментарий (что логично для дальнейшего UI/аналитики), лучше добавить отдельную сущность ModuleDescription или поле module_docstring в результате парсинга файла (но это уже не поле функции).
ast.get_docstring(tree) как раз возвращает module-level docstring, не исполняя код.