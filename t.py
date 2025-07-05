import argparse
import sys
import csv
from abc import ABC, abstractmethod

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
        csv_obj = CSVParser.parse(args.file)
        print(csv_obj)
        print(f"DBG. Переданные аргументы: {vars(args)}")
        return args
    
# Парсинг csv-файла
class CSVParser:
    """Парсер csv-файла с автодетекцией диалекта. Возвращает данные в виде списка словарей."""
    @staticmethod
    def parse(file_path):        
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            # Читаем небольшой образец для определения диалекта
            sample = csvfile.readline()
            csvfile.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            # Парсим файл с обнаруженным диалектом
            reader = csv.DictReader(csvfile, dialect=dialect)
            return list(reader)

# Команды фильтрации, агрегации и прочего
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

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