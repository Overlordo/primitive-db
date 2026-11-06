"""Операции со схемами таблиц."""

from primitive_db.constants import ID_COLUMN, VALID_TYPES


def _schema(metadata, table_name):
    """Вернуть схему существующей таблицы."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]


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


def drop_table(metadata, table_name):
    """Удалить схему существующей таблицы."""
    _schema(metadata, table_name)
    del metadata[table_name]
    return metadata


def list_tables(metadata):
    """Вернуть имена таблиц в алфавитном порядке."""
    return sorted(metadata)
