"""Чтение и запись JSON-файлов базы данных."""

import json
import os


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
