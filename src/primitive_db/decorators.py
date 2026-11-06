"""Общие обёртки для команд базы данных и кэширование запросов."""

import time


def _keep_metadata(wrapper, func):
    """Сохранить имя и описание исходной функции."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func):
    """Вывести понятную ошибку и вернуть None при сбое операции."""

    def wrapper(*args, **kwargs):
        """Выполнить операцию с обработкой ошибок базы данных."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except OSError as error:
            print(f"Ошибка файловой системы: {error}")
        return None

    return _keep_metadata(wrapper, func)


def confirm_action(action_name):
    """Создать декоратор, запрашивающий согласие на удаление."""

    def decorate(func):
        """Оборачивать операцию в запрос подтверждения."""

        def wrapper(*args, **kwargs):
            """Выполнить операцию только после ответа y."""
            try:
                answer = input(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            except EOFError:
                answer = ""
            if answer.strip().lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return _keep_metadata(wrapper, func)

    return decorate


def log_time(func):
    """Печатать длительность вызова с точностью до миллисекунд."""

    def wrapper(*args, **kwargs):
        """Измерить время вызова монотонными часами."""
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")

    return _keep_metadata(wrapper, func)


def create_cacher():
    """Вернуть функцию, которая хранит результаты запросов в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть значение из кэша или вычислить и запомнить его."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
