"""Командный цикл и вывод результатов."""

import prompt
from prettytable import PrettyTable

from primitive_db import core
from primitive_db.constants import (
    COMMAND_PROMPT,
    CRUD_HELP,
    GENERAL_HELP,
    ID_COLUMN,
    META_FILE,
    TABLE_HELP,
)
from primitive_db.parser import parse_command
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Показать команды управления таблицами и строками."""
    print("\n***База данных***\n\nФункции:")
    print(*TABLE_HELP, *CRUD_HELP, *GENERAL_HELP, sep="\n")


def _create_table(metadata, table, columns):
    """Создать схему и пустой файл строк."""
    updated = core.create_table(metadata, table, columns)
    if updated is None:
        return
    save_table_data(table, [])
    save_metadata(META_FILE, updated)
    schema = ", ".join(updated[table])
    print(f'Таблица "{table}" успешно создана со столбцами: {schema}')


def _drop_table(metadata, table):
    """Сохранить метаданные и удалить файл строк после удаления таблицы."""
    updated = core.drop_table(metadata, table)
    if updated is None:
        return
    save_metadata(META_FILE, updated)
    remove_table_data(table)
    print(f'Таблица "{table}" успешно удалена.')


def _insert(metadata, table, values):
    """Сохранить результат вставки и показать ID новой строки."""
    rows = core.insert(metadata, table, values)
    if rows is None:
        return
    save_table_data(table, rows)
    row_id = rows[-1][ID_COLUMN]
    print(f'Запись с ID={row_id} успешно добавлена в таблицу "{table}".')


def _print_rows(schema, rows):
    """Показать строки в таблице PrettyTable."""
    columns = [column.split(":")[0] for column in schema]
    result = PrettyTable(columns)
    for row in rows:
        result.add_row([row[column] for column in columns])
    print(result)


def _save_changes(command, table, rows, updated, where_clause):
    """Сохранить изменения и вывести сообщение для каждой затронутой строки."""
    if updated is None:
        return
    save_table_data(table, updated)
    affected = [
        row[ID_COLUMN]
        for row in rows
        if all(row[column] == value for column, value in where_clause.items())
    ]
    if not affected:
        print("Подходящих записей не найдено.")
    for row_id in affected:
        if command == "update":
            print(f'Запись с ID={row_id} в таблице "{table}" успешно обновлена.')
        else:
            print(f'Запись с ID={row_id} успешно удалена из таблицы "{table}".')


def _manage_rows(command, metadata, table, *args):
    """Проверить схему и выполнить чтение, обновление или удаление строк."""
    schema = core.table_schema(metadata, table)
    if schema is None:
        return
    rows = load_table_data(table)
    if command == "info":
        print(f"Таблица: {table}")
        print(f"Столбцы: {', '.join(schema)}")
        print(f"Количество записей: {len(rows)}")
        return

    where_clause = args[-1]
    if where_clause and not core.validate_fields(schema, where_clause):
        return
    if command == "select":
        selected = core.select(rows, where_clause)
        if selected is not None:
            _print_rows(schema, selected)
        return
    if command == "update":
        set_clause = args[0]
        if not core.validate_fields(schema, set_clause):
            return
        updated = core.update(rows, set_clause, where_clause)
    else:
        updated = core.delete(rows, where_clause)
    _save_changes(command, table, rows, updated, where_clause)


def _execute(command, args):
    """Загрузить метаданные и передать команду её обработчику."""
    if command == "help":
        print_help()
    elif command in {
        "create_table",
        "drop_table",
        "insert",
        "list_tables",
        "info",
        "select",
        "update",
        "delete",
    }:
        metadata = load_metadata(META_FILE)
        if command == "create_table":
            _create_table(metadata, *args)
        elif command == "drop_table":
            _drop_table(metadata, *args)
        elif command == "insert":
            _insert(metadata, *args)
        elif command == "list_tables":
            for table in core.list_tables(metadata):
                print(f"- {table}")
        else:
            _manage_rows(command, metadata, *args)
    elif command:
        print(f"Функции {command} нет. Попробуйте снова.")


def run():
    """Читать команды до выхода, EOF или прерывания."""
    print_help()
    while True:
        try:
            command, args = parse_command(prompt.string(COMMAND_PROMPT))
            if command == "exit":
                return
            _execute(command, args)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
