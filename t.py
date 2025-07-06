import argparse
import sys
import csv
from abc import ABC, abstractmethod

# Парсинг CLI
ARGUMENT_DEFINITIONS = {
     'file': {
        'type': str,
        'help': 'Путь к CSV-файлу',
        'required': True
    },
    'where': {
        'type': str,
        'help': 'Флаг фильтрации',
        'required': False
    },
    'aggregate': {
        'type': str,
        'help': 'Флаг агрегации',
        'required': False
    },
    'order-by': {
        'type': str,
        'help': 'Флаг порядка сортировки',
        'required': False
    }
}

aggregate_cases = ['min', 'max', 'avg', 'median']

class CLIArgumentParser(argparse.ArgumentParser):
    """Переопределяем стандартный парсер для вывода хелпа в случае неадеквата поданных аргументов."""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, f"\nОшибка: {message}\n")


    
# Парсинг csv-файла
class CSVParser:
    """Парсер csv-файла с автодетекцией диалекта. Возвращает данные в виде списка словарей."""
    @staticmethod
    def parse(file_path):        
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile)) 
        
# Парсинг выражений
OPERATORS = ['!=', '>=', '<=', '=', '>', '<'] # Порядок операторов важен.

class ExpressionParser:
    @staticmethod
    def detect_data_type(data_string):
        try:
            value = int(data_string)
        except ValueError:
            try:
                value = float(data_string)
            except ValueError:
               value = data_string.strip("'\"")
        return value      

    @staticmethod
    def parse_expression(row):
        for op in OPERATORS:
            if op in row:
                parts = row.split(op, 1)
                left_hand = parts[0].strip()
                right_hand = ExpressionParser.detect_data_type(parts[1].strip())
                return (left_hand, op, right_hand) 
        raise ValueError(f"Не найден оператор в выражении: {row}")
        


# Диспетчер коллбеков
class CLIArgumentsDispatcher:
    @staticmethod
    def processor_pipeline(csv_obj, args):
        """Метод последовательно вызывает исполнение команд, согласно содержимому args"""
        data = csv_obj 
        for command in ARGUMENT_DEFINITIONS.keys():
            if command == 'file':
                continue
            if command == 'where':
               expression = ExpressionParser.parse_expression(args.where)
               command_class = CommandRegistry.get_command('Where')
               data = command_class().execute(csv_obj, expression)
            elif command == 'aggregate':
                pass
            elif command == 'order-by':
                pass
            else: 
                raise ValueError(f"Неизвестная команда: {command}")
        
         # Выводим результат
        if data:
            # Выводим заголовки
            print("\t".join(data[0].keys()))
            # Выводим данные
            for row in data:
                print("\t".join(str(value) for value in row.values()))
        else:
            print("Нет данных, соответствующих условиям")
        
    @staticmethod
    def run():
        parser = CLIArgumentParser(description='Workmate. Тестовое задание')
        for flag, params in ARGUMENT_DEFINITIONS.items():
            parser.add_argument('--'+flag, **params)
        args = parser.parse_args()
        csv_obj = CSVParser.parse(args.file)
        CLIArgumentsDispatcher.processor_pipeline(csv_obj, args)
        # print(csv_obj)
        # print(f"DBG. Переданные аргументы: {vars(args)}")
        return args


        
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
    

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

# @CommandRegistry.register('Aggregate')
# class Aggregate(Command):
#     """АЛгоритм. Константы с возможными значениями. Для каждой свой case и цикл прохода по столбцу."""
#     def execute(self):
#         field, operator, expected_value = expression
#         filtered_rows = []

#     _agr_min(self, )

#     match aggregator_type:
#         case 'min': pass
#         case 'max': pass
#         case 'avg': pass
#         case 'median': pass


@CommandRegistry.register('Where')
class Where(Command):
    def execute(self, csv_obj, expression):
        field, operator, expected_value = expression
        filtered_rows = []
        
        for row in csv_obj:
            field_value = row.get(field)
            if field_value is None:
                continue
            
            field_value = ExpressionParser.detect_data_type(field_value)
            
            # Нормализация строк (если оба значения - строки)
            if isinstance(field_value, str) and isinstance(expected_value, str):
                field_value = field_value.strip().lower()
                expected_value = expected_value.strip().lower()
            
            if self._compare_values(field_value, operator, expected_value):
                filtered_rows.append(row)
        
        return filtered_rows

    def _compare_values(self, field_value, operator, expected_value):
        match operator:
            case '=': return field_value == expected_value
            case '!=': return field_value != expected_value
            case '>': return field_value > expected_value
            case '<': return field_value < expected_value
            case '>=': return field_value >= expected_value
            case '<=': return field_value <= expected_value
            case _: raise ValueError(f"Unsupported operator: {operator}")

if __name__ == "__main__":
    t = CLIArgumentsDispatcher()
    t.run()