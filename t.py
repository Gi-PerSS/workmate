import argparse
import sys
import csv

# Парсинг CLI
ARGUMENT_DEFINITIONS = {
     '--file': {
        'type': str,
        'help': 'Путь к CSV-файлу',
        'required': True
    },
    '--where': {
        'type': str,
        'help': 'Флаг фильтрации',
        'required': False
    },
    '--aggregate': {
        'type': str,
        'help': 'Флаг агрегации',
        'required': False
    },
    '--order-by': {
        'type': str,
        'help': 'Флаг порядка сортировки',
        'required': False
    }
}

class CLIArgumentParser(argparse.ArgumentParser):
    """Переопределяем стандартный парсер для вывода хелпа в случае неадеквата поданных аргументов."""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, f"\nОшибка: {message}\n")

class CLIArgumentsDispatcher:
    def run(self):
        parser = CLIArgumentParser(description='Workmate. Тестовое задание')
        for flag, params in ARGUMENT_DEFINITIONS.items():
            parser.add_argument(flag, **params)
        args = parser.parse_args()
        print(f"DBG. Переданные аргументы: {vars(args)}")
        return args
    
# Парсинг csv-файла
class CSVParser:
    """Парсер csv-файла. Считывает данные из файла и возвращает их в виде списка словарей."""
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):        
        with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            return [row for row in reader]

# Команды фильтрации, агрегации и прочего
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


if __name__ == "__main__":
    t = CLIArgumentsDispatcher()
    t.run()