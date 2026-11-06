"""Пути, типы данных и сообщения интерфейса."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
ID_COLUMN = "ID"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
COMMAND_PROMPT = ">>> Введите команду: "

TABLE_HELP = (
    "<command> create_table <таблица> <столбец:тип> ... - создать таблицу",
    "<command> list_tables - показать список всех таблиц",
    "<command> drop_table <таблица> - удалить таблицу",
)
GENERAL_HELP = (
    "<command> exit - выход из программы",
    "<command> help - справочная информация",
)

CRUD_HELP = (
    "<command> insert into <таблица> values (<значения>) - добавить запись",
    "<command> select from <таблица> [where <столбец> = <значение>] - выбрать записи",
    "<command> update <таблица> set <столбец> = <значение> where <условие>"
    " - обновить записи",
    "<command> delete from <таблица> where <условие> - удалить записи",
    "<command> info <таблица> - показать схему и число записей",
)
