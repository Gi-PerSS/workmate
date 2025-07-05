import argparse
import sys

class MyArgumentParser(argparse.ArgumentParser):
    """Переопределяем стандартный парсер для вывода хелпа при ошибке ввода аргументов."""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, f"\nОшибка: {message}\n")

class CommandRegistry:
    """Реестр команд. Регистрируем классы-команд, обрабатывающие csv-файлы. 
    (Для удобного расширения функционала)"""
    _registry = {}

    @classmethod    
    def register(cls, command):
        """На вход принимается команда, так, как она задана в командной строке.
        Возвращает декоратор, который регистрирует функцию в реестре команд."""
        def decorator(func):
            cls._registry[command] = func
            return func
        return decorator

    @classmethod
    def get_command(cls, command):
        return cls._registry.get(command)



if __name__ == "__main":
    parser = MyArgumentParser(description='Workmate. Тестовое задание')

    parser.add_argument('--foo', type=int, help='Пример аргумента')

    args = parser.parse_args()
    print(f"DBG. All arguments: {args.foo}")
