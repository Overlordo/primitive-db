"""Разбор команд и преобразование литералов в int, str и bool."""

import shlex


def _split(line):
    """Разбить команду на токены, сохранив кавычки вокруг строк."""
    lexer = shlex.shlex(line, posix=False, punctuation_chars="(),=")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _require(condition, syntax):
    """Сообщить ожидаемый синтаксис при неправильной форме команды."""
    if not condition:
        raise ValueError(f"Некорректная команда. Синтаксис: {syntax}")


def _parse_value(token):
    """Прочитать строку в кавычках, целое число или логическое значение."""
    if token[0] in {'"', "'"} and token[-1] == token[0] and len(token) >= 2:
        return token[1:-1]
    if token.lower() in {"true", "false"}:
        return token.lower() == "true"
    if token.removeprefix("-").removeprefix("+").isdecimal():
        return int(token)
    raise ValueError(f"Некорректное значение: {token}. Попробуйте снова.")


def _parse_assignment(tokens):
    """Преобразовать выражение столбец = значение в словарь."""
    _require(
        len(tokens) == 3 and tokens[0].isidentifier() and tokens[1] == "=",
        "столбец = значение",
    )
    return {tokens[0]: _parse_value(tokens[2])}


def parse_where_clause(clause):
    """Разобрать текст условия WHERE."""
    return _parse_assignment(_split(clause))


def parse_set_clause(clause):
    """Разобрать текст присваивания SET."""
    return _parse_assignment(_split(clause))


def _parse_insert(args):
    """Извлечь имя таблицы и значения из INSERT."""
    syntax = "insert into <таблица> values (<значения>)"
    _require(
        len(args) >= 6
        and args[0].lower() == "into"
        and args[2].lower() == "values"
        and args[3] == "("
        and args[-1] == ")",
        syntax,
    )
    values = args[4:-1]
    _require(len(values) % 2 == 1 and all(t == "," for t in values[1::2]), syntax)
    return args[1], [_parse_value(token) for token in values[::2]]


def _parse_selection(command, args):
    """Извлечь таблицу и условие из SELECT или DELETE."""
    syntax = f"{command} from <таблица> where <столбец> = <значение>"
    _require(len(args) >= 2 and args[0].lower() == "from", syntax)
    if command == "select" and len(args) == 2:
        return args[1], None
    _require(len(args) == 6 and args[2].lower() == "where", syntax)
    return args[1], parse_where_clause(" ".join(args[3:]))


def _parse_update(args):
    """Извлечь таблицу, присваивание и условие из UPDATE."""
    _require(
        len(args) == 9 and args[1].lower() == "set" and args[5].lower() == "where",
        "update <таблица> set <столбец> = <значение> where <условие>",
    )
    return (
        args[0],
        parse_set_clause(" ".join(args[2:5])),
        parse_where_clause(" ".join(args[6:])),
    )


def parse_command(line):
    """Разобрать команду и вернуть её имя и аргументы для движка."""
    tokens = _split(line)
    if not tokens:
        return "", ()
    command, *args = tokens
    command = command.lower()
    if command == "insert":
        return command, _parse_insert(args)
    if command in {"select", "delete"}:
        return command, _parse_selection(command, args)
    if command == "update":
        return command, _parse_update(args)
    if command == "create_table":
        _require(len(args) >= 2, "create_table <таблица> <столбец:тип> ...")
        return command, (args[0], args[1:])
    if command in {"drop_table", "info"}:
        _require(len(args) == 1, f"{command} <таблица>")
    elif command in {"list_tables", "help", "exit"}:
        _require(not args, command)
    return command, tuple(args)
