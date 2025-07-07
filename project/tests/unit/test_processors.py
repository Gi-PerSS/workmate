# test_processors.py
import pytest
from typing import List, Dict
from project.model.processors import Aggregate, Where, OrderBy

@pytest.fixture
def sample_data() -> List[Dict[str, str]]:
    """
    Фикстура предоставляет тестовые данные для агрегации и фильтрации.
    Включает числовые и строковые значения для комплексного тестирования.
    """
    return [
        {"name": "iphone", "brand": "apple", "price": "999", "rating": "4.9"},
        {"name": "galaxy", "brand": "samsung", "price": "1199", "rating": "4.8"},
        {"name": "redmi", "brand": "xiaomi", "price": "199", "rating": "4.6"},
        {"name": "poco", "brand": "xiaomi", "price": "299", "rating": "4.4"},
    ]

class TestAggregate:
    """Тестирование агрегатных функций."""
    
    def test_min_aggregation(self, sample_data):
        """Тест нахождения минимального значения."""
        result = Aggregate._agr_min(sample_data, "price")
        assert result == 199  # Самый дешевый телефон
        
    def test_max_aggregation(self, sample_data):
        """Тест нахождения максимального значения."""
        result = Aggregate._agr_max(sample_data, "rating")
        assert result == 4.9  # Максимальный рейтинг
        
    def test_avg_aggregation(self, sample_data):
        """Тест вычисления среднего значения."""
        result = Aggregate._agr_avg(sample_data, "price")
        # (999 + 1199 + 199 + 299) / 4 = 674.0
        assert result == 674.0
        
    def test_median_aggregation(self, sample_data):
        """Тест вычисления медианы."""
        result = Aggregate._agr_median(sample_data, "price")
        # Отсортированные цены: [199, 299, 999, 1199] → медиана (299+999)/2 = 649
        assert result == 649
        
    def test_convert_float_to_int(self):
        """Тест конвертации float в int при необходимости."""
        assert Aggregate.convert_float_to_int_if_necessary(5.0) == 5
        assert Aggregate.convert_float_to_int_if_necessary(5.5) == 5.5
        
    def test_string_aggregation_error(self, sample_data):
        """Тест ошибки при агрегации строковых значений."""
        with pytest.raises(ValueError, match="Агрегация для строк не предусмотрена"):
            Aggregate._agr_avg(sample_data, "brand")

class TestWhere:
    """Тестирование фильтрации данных."""
    
    def test_equals_filter(self, sample_data):
        """Тест фильтрации по равенству."""
        result = Where.execute(sample_data, ("brand", "=", "xiaomi"))
        assert len(result) == 2  # Два телефона Xiaomi
        assert all(item["brand"] == "xiaomi" for item in result)
        
    def test_greater_than_filter(self, sample_data):
        """Тест фильтрации по 'больше'."""
        result = Where.execute(sample_data, ("rating", ">", "4.7"))
        assert len(result) == 2  # Только iphone (4.9) и galaxy (4.8)
        
    def test_less_than_filter(self, sample_data):
        """Тест фильтрации по 'меньше'."""
        result = Where.execute(sample_data, ("price", "<", "300"))
        assert len(result) == 2  # redmi (199) и poco (299)
        
    def test_not_equals_filter(self, sample_data):
        """Тест фильтрации по неравенству."""
        result = Where.execute(sample_data, ("brand", "!=", "apple"))
        assert len(result) == 3  # Все кроме apple
        
    def test_case_insensitive_filter(self, sample_data):
        """Тест регистронезависимой фильтрации строк."""
        result = Where.execute(sample_data, ("brand", "=", "XIAOMI"))
        assert len(result) == 2  # Должен найти xiaomi несмотря на регистр

class TestOrderBy:
    """Тестирование сортировки данных."""
    
    def test_ascending_sort(self, sample_data):
        """Тест сортировки по возрастанию."""
        result = OrderBy.execute(sample_data, ("price", "", "asc"))
        prices = [item["price"] for item in result]
        assert prices == ["199", "299", "999", "1199"]
        
    def test_descending_sort(self, sample_data):
        """Тест сортировки по убыванию."""
        result = OrderBy.execute(sample_data, ("rating", "", "desc"))
        ratings = [item["rating"] for item in result]
        assert ratings == ["4.9", "4.8", "4.6", "4.4"]
        
    def test_invalid_sort_direction(self, sample_data):
        """Тест ошибки при некорректном направлении сортировки."""
        with pytest.raises(ValueError, match="Направление сортировки должно быть 'asc' или 'desc'"):
            OrderBy.execute(sample_data, ("price", "", "invalid"))