# test_csv_parser.py
import pytest
from pathlib import Path
from project.model.csv_parser import CSVParser

@pytest.fixture
def sample_csv(tmp_path):
    """
    Фикстура создает временный CSV-файл с тестовыми данными.
    Используется для тестирования парсера CSV.
    
    Особенности:
    1. Создает файл с заголовками и 3 тестовыми записями
    2. Поддерживает как строковые, так и числовые значения
    3. Автоматически удаляется после теста
    """
    file_path = tmp_path / "test.csv"
    file_path.write_text(
        "name,brand,price,rating\n"
        "iphone 15 pro,apple,999,4.9\n"
        "galaxy s23 ultra,samsung,1199,4.8\n"
        "redmi note 12,xiaomi,199,4.6"
    )
    return str(file_path)

def test_parse_returns_list_of_dicts(sample_csv):
    """
    Тест проверяет базовую функциональность парсера:
    1. Возвращаемый тип - список
    2. Каждый элемент списка - словарь
    3. Ключи словаря соответствуют заголовкам CSV
    """
    result = CSVParser.parse(sample_csv)
    
    assert isinstance(result, list)  # Проверяем тип возвращаемого значения
    assert all(isinstance(item, dict) for item in result)  # Все элементы - словари
    assert set(result[0].keys()) == {"name", "brand", "price", "rating"}  # Проверяем ключи

def test_parse_correct_values(sample_csv):
    """
    Тест проверяет корректность распарсенных значений:
    1. Соответствие значений ожидаемым
    2. Правильное преобразование всех колонок в строки (как работает csv.DictReader)
    """
    result = CSVParser.parse(sample_csv)
    
    # Проверяем первую запись
    assert result[0]["name"] == "iphone 15 pro"
    assert result[0]["brand"] == "apple"
    assert result[0]["price"] == "999" 
    assert result[0]["rating"] == "4.9"
    
    # Проверяем вторую запись
    assert result[1]["brand"] == "samsung"
    assert result[1]["price"] == "1199"

def test_parse_empty_file(tmp_path):
    """
    Тест проверяет обработку пустого CSV-файла (только заголовки).
    Ожидается пустой список.
    """
    file_path = tmp_path / "empty.csv"
    file_path.write_text("name,brand,price,rating\n")  # Только заголовки
    
    result = CSVParser.parse(str(file_path))
    assert result == []  # Для файла только с заголовками ожидаем пустой список

def test_parse_file_not_found():
    """
    Проверяет, что при попытке парсинга несуществующего файла метод выбрасывает FileNotFoundError.
    Контекстный менеджер pytest.raises следит за тем, чтобы исключение действительно возникло —
    если оно не будет выброшено или будет другого типа, тест завершится с ошибкой.
    """
    with pytest.raises(FileNotFoundError):
        CSVParser.parse("non_existent_file.csv")