"""Чтение и запись JSON-файлов базы данных."""

import json
import os

from primitive_db.constants import DATA_DIR


def _load_json(filepath, default):
    """Прочитать JSON или вернуть значение по умолчанию для нового файла."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _save_json(filepath, data):
    """Записать JSON во временный файл и заменить целевой файл."""
    temporary = f"{filepath}.{os.getpid()}.tmp"
    try:
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(temporary, filepath)
    finally:
        if os.path.exists(temporary):
            os.remove(temporary)


def load_metadata(filepath):
    """Загрузить схемы таблиц из файла метаданных."""
    return _load_json(filepath, {})


def save_metadata(filepath, data):
    """Сохранить схемы таблиц."""
    _save_json(filepath, data)


def _table_path(table_name):
    """Получить путь к файлу таблицы."""
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")
    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Прочитать строки таблицы или вернуть пустой список."""
    return _load_json(_table_path(table_name), [])


def save_table_data(table_name, data):
    """Сохранить строки таблицы в отдельный файл."""
    filepath = _table_path(table_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    _save_json(filepath, data)


def remove_table_data(table_name):
    """Удалить файл строк, если он существует."""
    try:
        os.remove(_table_path(table_name))
    except FileNotFoundError:
        pass
