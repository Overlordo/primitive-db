"""Управление схемами и строками таблиц."""

import json

from primitive_db.constants import ID_COLUMN, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

_cache_select = create_cacher()


def _schema(metadata, table_name):
    """Вернуть схему существующей таблицы."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Проверить схему, добавить ID и зарегистрировать таблицу."""
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")
    if not columns:
        raise ValueError("Укажите хотя бы один столбец.")

    schema = {ID_COLUMN: "int"}
    explicit_id = False
    for column in columns:
        name, separator, type_name = column.partition(":")
        if not separator or not name.isidentifier() or type_name not in VALID_TYPES:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        if name == ID_COLUMN and type_name == "int" and not explicit_id:
            explicit_id = True
            continue
        if name in schema:
            raise ValueError(f"Недопустимое повторное объявление столбца {name}.")
        schema[name] = type_name

    metadata[table_name] = [f"{name}:{kind}" for name, kind in schema.items()]
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удалить схему существующей таблицы."""
    _schema(metadata, table_name)
    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """Вернуть имена таблиц в алфавитном порядке."""
    return sorted(metadata)


def _validate_value(column, type_name, value):
    """Проверить точное соответствие значения типу столбца."""
    if type(value) is not VALID_TYPES[type_name]:
        raise ValueError(f"Столбец {column} ожидает {type_name}, получено {value!r}.")


@handle_db_errors
def validate_fields(schema, fields):
    """Проверить имена и типы полей из WHERE или SET."""
    types = dict(column.split(":") for column in schema)
    for column, value in fields.items():
        if column not in types:
            raise KeyError(f'Столбец "{column}" не существует.')
        _validate_value(column, types[column], value)
    return True


@handle_db_errors
def table_schema(metadata, table_name):
    """Вернуть список столбцов для вывода или проверки команды."""
    return _schema(metadata, table_name)


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Проверить значения и вернуть данные с новой строкой."""
    columns = _schema(metadata, table_name)[1:]
    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось значений: {len(columns)}, получено: {len(values)}."
        )

    table_data = load_table_data(table_name)
    next_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    row = {ID_COLUMN: next_id}
    for column, value in zip(columns, values):
        name, type_name = column.split(":")
        _validate_value(name, type_name, value)
        row[name] = value
    return [*table_data, row]


def _matches(row, where_clause):
    """Проверить, что строка соответствует всем полям условия."""
    return all(row[column] == value for column, value in where_clause.items())


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Вернуть копии подходящих строк, переиспользуя результат запроса."""
    condition = where_clause or {}
    key = json.dumps((table_data, condition), sort_keys=True)

    def matching_rows():
        """Вычислить результат для текущего содержимого таблицы."""
        return [row.copy() for row in table_data if _matches(row, condition)]

    return [row.copy() for row in _cache_select(key, matching_rows)]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Заменить указанные поля у подходящих строк."""
    if ID_COLUMN in set_clause:
        raise ValueError(f"Столбец {ID_COLUMN} нельзя изменить.")
    return [
        {**row, **set_clause} if _matches(row, where_clause) else row
        for row in table_data
    ]


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Вернуть строки, не подходящие под условие удаления."""
    return [row for row in table_data if not _matches(row, where_clause)]
