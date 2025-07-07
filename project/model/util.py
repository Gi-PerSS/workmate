from typing import Union

def convert_to_number_if_possible(data_string: str) -> Union[int, float, str]:
    """Пытается преобразовать строку в число (int или float), если это возможно.

    Args:
        data_string: Входная строка для преобразования.

    Returns:
        Преобразованное значение (число или исходная строка).
    """
    try:
        # Сначала пробуем float, чтобы не потерять дробную часть
        value = float(data_string)
        # Если значение float является целым числом, возвращаем int
        if value.is_integer():
            return int(value)
        return value
    except ValueError:
        try:
            # Если не получилось как float, пробуем int
            return int(data_string)
        except ValueError:
            # Если ничего не получилось, возвращаем строку без кавычек
            return data_string.strip("'\"")

class ExpressionParser:
    """Парсер выражений для условий фильтрации, сортировки и агрегации."""

    @staticmethod
    def parse_expression(row: str) -> tuple[str, str, Union[int, float, str]]:
        """Разбирает выражение на составляющие: поле, оператор и значение.

        Args:
            row: Строка с выражением (например, "age>=25").

        Returns:
            Кортеж из (поле, оператор, значение).

        Raises:
            ValueError: Если в выражении не найден поддерживаемый оператор.
        """
        OPERATORS = ['!=', '>=', '<=', '=', '>', '<']  # Порядок важен для корректного разбора
        for op in OPERATORS:
            if op in row:
                parts = row.split(op, 1)
                left_hand = parts[0].strip()
                right_hand = convert_to_number_if_possible(parts[1].strip())
                return (left_hand, op, right_hand)
        raise ValueError(f"Не найден оператор в выражении: {row}")
