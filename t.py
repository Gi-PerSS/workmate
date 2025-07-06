import argparse
import sys
import csv
from tabulate import tabulate




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


class CLIArgumentParser(argparse.ArgumentParser):
    """Переопределяем стандартный парсер для вывода хелпа в случае неадеквата поданных аргументов."""
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, f"\nОшибка: {message}\n")


    
# Парсинг csv-файла
class CSVParser:
    """Парсер csv-файла. Возвращает данные в виде списка словарей."""
    @staticmethod
    def parse(file_path):        
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile)) 
        
# Парсинг выражений
class ExpressionParser:
    @staticmethod
    def convert_to_number_if_possible(data_string):
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
        OPERATORS = ['!=', '>=', '<=', '=', '>', '<'] # Порядок операторов важен.
        for op in OPERATORS:
            if op in row:
                parts = row.split(op, 1)
                left_hand = parts[0].strip()
                right_hand = ExpressionParser.convert_to_number_if_possible(parts[1].strip())
                return (left_hand, op, right_hand) 
        raise ValueError(f"Не найден оператор в выражении: {row}")
        
# Диспетчер коллбеков
class CLIArgumentsDispatcher:
    @staticmethod
    def processor_pipeline(csv_obj, args):

        data = csv_obj
        args_dict = vars(args) 
        
        # Порядок обработки важен: where -> order_by -> aggregate
        if args_dict.get('where'):
            expression = ExpressionParser.parse_expression(args.where)
            data = Where.execute(data, expression)
        
        if args_dict.get('order_by'):  # argparse автоматом заменяет дефис из аругментов на _
            expression = ExpressionParser.parse_expression(args.order_by)
            data = OrderBy.execute(data, expression)

        if args_dict.get('aggregate'):
            expression = ExpressionParser.parse_expression(args.aggregate)
            _, _, aggregator_type = expression
            data = {aggregator_type: [Aggregate.execute(data, expression)]}

        # Вывод результатов
        if data:
            print(tabulate(data, headers="keys", tablefmt="github"))
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



class Aggregate:
    """АЛгоритм. Константы с возможными значениями. Для каждой свой case и цикл прохода по столбцу."""
    def execute(csv_obj, expression):
        field, _, aggregator_type = expression
        match aggregator_type:
            case 'min': return Aggregate._agr_min(csv_obj, field)
            case 'max': return Aggregate._agr_max(csv_obj, field)
            case 'avg': return Aggregate._agr_avg(csv_obj, field)
            case 'median': return Aggregate._agr_median(csv_obj, field)
            case _: raise ValueError(f"Неизвестный тип агрегации: {aggregator_type}")

    @staticmethod
    def convert_float_to_int_if_necessary(value):
        """Преобразует результат в int если это целое число, иначе оставляет float"""
        if isinstance(value, (int, float)) and value == int(value):
            return int(value)
        return value
    
    @staticmethod
    def _agr_min(csv_obj, field):
        min_value = float('inf') 
        for row in csv_obj:
            actual_value = ExpressionParser.convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            min_value = min(min_value, actual_value)
        return Aggregate.convert_float_to_int_if_necessary(min_value)
    
    @staticmethod
    def _agr_max(csv_obj, field):
        max_value = float('-inf') 
        for row in csv_obj:
            actual_value = ExpressionParser.convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            if actual_value > max_value:
                max_value = actual_value
        return Aggregate.convert_float_to_int_if_necessary(max_value)

    @staticmethod
    def _agr_avg(csv_obj, field):
        if not csv_obj:
            return 0
            
        total = 0
        for row in csv_obj:
            actual_value = ExpressionParser.convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            total += actual_value
        
        avg = total /len(csv_obj)
        return Aggregate.convert_float_to_int_if_necessary(avg)
    
    @staticmethod
    def _agr_median(csv_obj, field):
        """Медиана - это среднее значение в отсортированном списке. Для четного числа элементов - 
        среднее двух средних элементов."""
        values = []
        for row in csv_obj:
            actual_value = ExpressionParser.convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            values.append(actual_value)
        
        if not values:
            return 0
            
        values.sort()
        n = len(values)
        if n % 2 == 1:
            median = values[n//2]
        else:
            median = (values[n//2 - 1] + values[n//2]) / 2
            
        return Aggregate.convert_float_to_int_if_necessary(median)
    


class Where:
    @staticmethod
    def execute(csv_obj, expression):
        field, operator, expected_value = expression
        filtered_rows = []
        
        # Проходим по списку словарей и проверяем значение поля в каждой строке на соответствие условию.
        for row in csv_obj:
            field_value = row.get(field)
            if field_value is None:
                continue

            # Конвертируем значение поля в число, если это возможно, для сравнения с заданным значением.
            field_value = ExpressionParser.convert_to_number_if_possible(field_value)
            
            # Нормализация строк (если оба значения - строки)
            if isinstance(field_value, str) and isinstance(expected_value, str):
                field_value = field_value.strip().lower()
                expected_value = expected_value.strip().lower()

            # Если условие соблюдается, добавляем строку в вывод
            if Where._compare_values(field_value, operator, expected_value):
                filtered_rows.append(row)
        
        return filtered_rows
    
    @staticmethod
    def _compare_values(field_value, operator, expected_value):
        match operator:
            case '=': return field_value == expected_value
            case '!=': return field_value != expected_value
            case '>': return field_value > expected_value
            case '<': return field_value < expected_value
            case '>=': return field_value >= expected_value
            case '<=': return field_value <= expected_value
            case _: raise ValueError(f"Unsupported operator: {operator}")

class OrderBy:
    """Класс для сортировки данных из CSV по указанному полю."""
    
    @staticmethod
    def execute(data, expression):
        """
        Сортирует данные по заданному полю в указанном порядке.
        
        Параметры:
            data: список словарей (например, [{'name': 'Alice', 'age': 30}, ...])
            expression: кортеж из (поле, оператор, направление), например ('age', '=', 'asc')
        
        Возвращает:
            Отсортированный список словарей
        """
        field, _, direction = expression  # Разбираем выражение на части
        
        # Проверяем, что направление сортировки корректное
        if direction not in ('asc', 'desc'):
            raise ValueError("Направление сортировки должно быть 'asc' или 'desc'")
        
        # Создаем копию данных, чтобы не менять исходный список
        sorted_data = data.copy()
        
        # Функция для получения значения поля с конвертацией в число (если возможно)
        def get_key(row):
            value = row.get(field)
            return ExpressionParser.convert_to_number_if_possible(value)
        
        # Сортируем данные
        sorted_data.sort(
            key=get_key,          # Ключ сортировки
            reverse=(direction == 'desc')  # True для сортировки по убыванию
        )
        
        return sorted_data

if __name__ == "__main__":
    t = CLIArgumentsDispatcher()
    t.run()