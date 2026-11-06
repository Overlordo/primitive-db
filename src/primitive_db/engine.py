"""Командный цикл приложения."""

import prompt


def run():
    """Показать справку и принимать команды до выхода."""
    while True:
        print("<command> exit - выход из программы")
        print("<command> help - справочная информация")
        try:
            command = prompt.string(">>> Введите команду: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command == "exit":
            return
        if command != "help":
            print(f"Функции {command} нет. Попробуйте снова.")
