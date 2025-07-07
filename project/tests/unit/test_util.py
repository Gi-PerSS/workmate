# test_util.py
import pytest
from project.model.util import convert_to_number_if_possible, ExpressionParser

class TestConvertToNumberIfPossible:
    """Тестирование функции преобразования строк в числа."""
    
    def test_convert_integer_string(self):
        """Тест преобразования строки с целым числом."""
        result = convert_to_number_if_possible("42")
        assert result == 42
        assert isinstance(result, int)
        
    def test_convert_float_string(self):
        """Тест преобразования строки с дробным числом."""
        result = convert_to_number_if_possible("3.14")
        assert result == 3.14
        assert isinstance(result, float)
        
    def test_convert_scientific_notation(self):
        """Тест преобразования строки с числом в научной нотации."""
        result = convert_to_number_if_possible("1.23e-4")
        assert result == 1.23e-4
        assert isinstance(result, float)
        
    def test_convert_string_with_quotes(self):
        """Тест обработки строки в кавычках."""
        result = convert_to_number_if_possible("'hello'")
        assert result == "hello"
        assert isinstance(result, str)
        
    def test_convert_regular_string(self):
        """Тест обработки обычной строки (без чисел)."""
        result = convert_to_number_if_possible("apple")
        assert result == "apple"
        assert isinstance(result, str)

class TestExpressionParser:
    """Тестирование парсера выражений."""
    
    def test_parse_simple_equals(self):
        """Тест разбора выражения с простым равенством."""
        result = ExpressionParser.parse_expression("rating=4.5")
        assert result == ("rating", "=", 4.5)
        
    def test_parse_greater_than(self):
        """Тест разбора выражения с оператором 'больше'."""
        result = ExpressionParser.parse_expression("price>1000")
        assert result == ("price", ">", 1000)
        
    def test_parse_less_or_equal(self):
        """Тест разбора выражения с оператором 'меньше или равно'."""
        result = ExpressionParser.parse_expression("age<=25")
        assert result == ("age", "<=", 25)
        
    def test_parse_not_equals(self):
        """Тест разбора выражения с оператором 'не равно'."""
        result = ExpressionParser.parse_expression("brand!=apple")
        assert result == ("brand", "!=", "apple")
        
    def test_parse_string_value(self):
        """Тест разбора выражения со строковым значением."""
        result = ExpressionParser.parse_expression("name='iphone'")
        assert result == ("name", "=", "iphone")
        
    def test_parse_invalid_expression(self):
        """Тест обработки некорректного выражения."""
        with pytest.raises(ValueError, match="Не найден оператор в выражении"):
            ExpressionParser.parse_expression("invalid_expression")
            
    def test_parse_with_whitespace(self):
        """Тест разбора выражения с пробелами."""
        result = ExpressionParser.parse_expression("  price  >=  500  ")
        assert result == ("price", ">=", 500)
        
    def test_parse_complex_operator_order(self):
        """Тест правильного определения операторов с разной длиной."""
        # Проверяем что оператор "!=" обрабатывается раньше "="
        result = ExpressionParser.parse_expression("status!=active")
        assert result == ("status", "!=", "active")