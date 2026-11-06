"""Командный цикл приложения."""

import shlex

import prompt

from primitive_db import core
from primitive_db.constants import COMMAND_PROMPT, GENERAL_HELP, META_FILE, TABLE_HELP
from primitive_db.utils import load_metadata, save_metadata


def print_help():
    """Показать доступные команды."""
    print("\n***Процесс работы с таблицей***\nФункции:")
    print(*TABLE_HELP, *GENERAL_HELP, sep="\n")


def run():
    """Принимать команды и сохранять изменения схемы."""
    print_help()
    while True:
        try:
            tokens = shlex.split(prompt.string(COMMAND_PROMPT))
            if not tokens:
                continue
            command, *args = tokens
            if command == "exit":
                return
            if command == "help":
                print_help()
                continue
            metadata = load_metadata(META_FILE)
            if command == "create_table" and len(args) >= 2:
                table, *columns = args
                updated = core.create_table(metadata, table, columns)
                save_metadata(META_FILE, updated)
                print(
                    f'Таблица "{table}" успешно создана со столбцами: '
                    f"{', '.join(updated[table])}"
                )
            elif command == "drop_table" and len(args) == 1:
                table = args[0]
                save_metadata(META_FILE, core.drop_table(metadata, table))
                print(f'Таблица "{table}" успешно удалена.')
            elif command == "list_tables" and not args:
                for table in core.list_tables(metadata):
                    print(f"- {table}")
            elif command in {"create_table", "drop_table", "list_tables"}:
                print("Некорректные аргументы. Введите help.")
            else:
                print(f"Функции {command} нет. Попробуйте снова.")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except (ValueError, OSError) as error:
            print(f"Ошибка: {error}")
