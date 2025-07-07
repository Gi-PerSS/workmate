from typing import Dict, List, Union, Tuple
from project.model.util import convert_to_number_if_possible, ExpressionParser

class Aggregate:
    """Класс для выполнения агрегатных функций над данными."""

    @staticmethod
    def execute(
        csv_obj: List[Dict[str, str]],
        expression: Tuple[str, str, str]
    ) -> Union[int, float]:
        """Выполняет агрегатную функцию по заданному выражению.

        Args:
            csv_obj: Данные для агрегации.
            expression: Кортеж (поле, оператор, тип_агрегации).

        Returns:
            Результат агрегации.

        Raises:
            ValueError: Если тип агрегации неизвестен или данные строковые.
        """
        field, _, aggregator_type = expression
        match aggregator_type:
            case 'min': return Aggregate._agr_min(csv_obj, field)
            case 'max': return Aggregate._agr_max(csv_obj, field)
            case 'avg': return Aggregate._agr_avg(csv_obj, field)
            case 'median': return Aggregate._agr_median(csv_obj, field)
            case _: raise ValueError(f"Неизвестный тип агрегации: {aggregator_type}")

    @staticmethod
    def convert_float_to_int_if_necessary(value: Union[int, float]) -> Union[int, float]:
        """Конвертирует float в int, если значение целое.

        Args:
            value: Число для проверки.

        Returns:
            Целое число, если значение было целым, иначе исходное число.
        """
        if isinstance(value, (int, float)) and value == int(value):
            return int(value)
        return value

    @staticmethod
    def _agr_min(csv_obj: List[Dict[str, str]], field: str) -> Union[int, float]:
        """Вычисляет минимальное значение в указанном поле.

        Args:
            csv_obj: Данные для обработки.
            field: Поле для поиска минимума.

        Returns:
            Минимальное значение.

        Raises:
            ValueError: Если поле содержит строковые значения.
        """
        min_value = float('inf')
        for row in csv_obj:
            actual_value = convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            min_value = min(min_value, actual_value)
        return Aggregate.convert_float_to_int_if_necessary(min_value)

    @staticmethod
    def _agr_max(csv_obj: List[Dict[str, str]], field: str) -> Union[int, float]:
        """Вычисляет максимальное значение в указанном поле.

        Args:
            csv_obj: Данные для обработки.
            field: Поле для поиска максимума.

        Returns:
            Максимальное значение.

        Raises:
            ValueError: Если поле содержит строковые значения.
        """
        max_value = float('-inf')
        for row in csv_obj:
            actual_value = convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            if actual_value > max_value:
                max_value = actual_value
        return Aggregate.convert_float_to_int_if_necessary(max_value)

    @staticmethod
    def _agr_avg(csv_obj: List[Dict[str, str]], field: str) -> Union[int, float]:
        """Вычисляет среднее значение в указанном поле.

        Args:
            csv_obj: Данные для обработки.
            field: Поле для вычисления среднего.

        Returns:
            Среднее значение.

        Raises:
            ValueError: Если поле содержит строковые значения.
        """
        if not csv_obj:
            return 0

        total = 0
        for row in csv_obj:
            actual_value = convert_to_number_if_possible(row.get(field))
            if isinstance(actual_value, str):
                raise ValueError("Агрегация для строк не предусмотрена")
            total += actual_value

        avg = total / len(csv_obj)
        return Aggregate.convert_float_to_int_if_necessary(avg)

    @staticmethod
    def _agr_median(csv_obj: List[Dict[str, str]], field: str) -> Union[int, float]:
        """Вычисляет медиану значений в указанном поле.

        Медиана - среднее значение в отсортированном списке. Для четного числа элементов -
        среднее двух центральных элементов.

        Args:
            csv_obj: Данные для обработки.
            field: Поле для вычисления медианы.

        Returns:
            Медианное значение.

        Raises:
            ValueError: Если поле содержит строковые значения.
        """
        values = []
        for row in csv_obj:
            actual_value = convert_to_number_if_possible(row.get(field))
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
    """Класс для фильтрации данных по условию."""

    @staticmethod
    def execute(
        csv_obj: List[Dict[str, str]],
        expression: Tuple[str, str, Union[int, float, str]]
    ) -> List[Dict[str, str]]:
        """Фильтрует данные по заданному условию.

        Args:
            csv_obj: Данные для фильтрации.
            expression: Кортеж (поле, оператор, значение) для фильтрации.

        Returns:
            Отфильтрованные данные.
        """

        field, operator, expected_value = expression
        filtered_rows = []

        expected_value = convert_to_number_if_possible(expected_value)
        for row in csv_obj:
            field_value = row.get(field)
            if field_value is None:
                continue

            field_value = convert_to_number_if_possible(field_value)

            # Нормализация строк для сравнения
            if isinstance(field_value, str) and isinstance(expected_value, str):
                field_value = field_value.strip().lower()
                expected_value = expected_value.strip().lower()

            if Where._compare_values(field_value, operator, expected_value):
                filtered_rows.append(row)

        return filtered_rows

    @staticmethod
    def _compare_values(
        field_value: Union[int, float, str],
        operator: str,
        expected_value: Union[int, float, str]
    ) -> bool:
        """Сравнивает значения согласно оператору.

        Args:
            field_value: Значение из данных.
            operator: Оператор сравнения.
            expected_value: Ожидаемое значение.

        Returns:
            Результат сравнения (True/False).

        Raises:
            ValueError: Если оператор не поддерживается.
        """
    
        match operator:
            case '=': return field_value == expected_value
            case '!=': return field_value != expected_value
            case '>': return field_value > expected_value
            case '<': return field_value < expected_value
            case '>=': return field_value >= expected_value
            case '<=': return field_value <= expected_value
            case _: raise ValueError(f"Unsupported operator: {operator}")


class OrderBy:
    """Класс для сортировки данных по указанному полю."""

    @staticmethod
    def execute(
        data: List[Dict[str, str]],
        expression: Tuple[str, str, str]
    ) -> List[Dict[str, str]]:
        """Сортирует данные по заданному полю в указанном направлении.

        Args:
            data: Данные для сортировки.
            expression: Кортеж (поле, оператор, направление).

        Returns:
            Отсортированные данные.

        Raises:
            ValueError: Если направление сортировки некорректно.
        """
        field, _, direction = expression

        if direction not in ('asc', 'desc'):
            raise ValueError("Направление сортировки должно быть 'asc' или 'desc'")

        sorted_data = data.copy()

        def get_key(row: Dict[str, str]) -> Union[int, float, str]:
            """Вспомогательная функция для получения значения ключа сортировки."""
            value = row.get(field)
            return convert_to_number_if_possible(value)

        sorted_data.sort(
            key=get_key,
            reverse=(direction == 'desc')
        )

        return sorted_data
