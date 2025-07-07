import pytest
import subprocess
from pathlib import Path

# Фикстура создает временный CSV-файл для тестирования
@pytest.fixture
def sample_csv(tmp_path):
    """
    Фикстура создает временный CSV-файл с тестовыми данными о продуктах.
    Использует встроенную фикстуру pytest tmp_path для безопасного создания файла во временной директории.
    
    Структура данных:
    - Заголовки: name, brand, price, rating
    - Тестовые данные: 6 записей о смартфонах разных брендов
    
    Особенности:
    1. Автоматически создается перед каждым тестом
    2. Автоматически удаляется после каждого теста
    3. Возвращает абсолютный путь к файлу в виде строки
    """
    # Создаем путь к файлу во временной директории
    file_path = tmp_path / "products.csv"
    # Записываем содержимое CSV
    file_path.write_text(
        "name,brand,price,rating\n"
        "iphone 15 pro,apple,999,4.9\n"
        "galaxy s23 ultra,samsung,1199,4.8\n"
        "redmi note 12,xiaomi,199,4.6\n"
        "poco x5 pro,xiaomi,299,4.4\n"
        "iphone 14,apple,799,4.7\n"
        "galaxy a54,samsung,349,4.2"
    )
    return str(file_path)  # Возвращаем путь как строку для удобства использования

def test_basic_output(sample_csv):
    """
    Тестирует базовую функциональность CLI без дополнительных параметров.
    Проверяет что:
    1. Программа завершается с кодом 0 (успех)
    2. Основные элементы данных присутствуют в выводе
    """
    # Запускаем CLI-команду как subprocess
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv],
        capture_output=True,  # Перехватываем stdout/stderr
        text=True             # Возвращаем вывод как строку (а не bytes)
    )
    
    # Проверки:
    assert result.returncode == 0  # Убеждаемся в успешном завершении
    # Проверяем наличие ожидаемых товаров в выводе
    assert "iphone 15 pro" in result.stdout
    assert "galaxy s23 ultra" in result.stdout
    assert "redmi note 12" in result.stdout

def test_where_filter_operations(sample_csv):
    """
    Комплексный тест фильтрации (WHERE-условий) через CLI.
    Проверяет все поддерживаемые операторы сравнения: 
    >, <, =, >=, <=, !=
    
    Каждый подтест:
    1. Запускает команду с разными параметрами --where
    2. Проверяет наличие ОЖИДАЕМЫХ записей в выводе
    3. Проверяет ОТСУТСТВИЕ неожиданных записей
    """
    # Тест оператора 'больше' (>)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "rating>4.7"],
        capture_output=True, text=True
    )
    # Должны отобразиться только товары с рейтингом > 4.7
    assert "iphone 15 pro" in result.stdout    # 4.9 > 4.7
    assert "galaxy s23 ultra" in result.stdout # 4.8 > 4.7
    assert "redmi note 12" not in result.stdout # 4.6 < 4.7

    # Тест оператора 'меньше' (<)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "price<300"],
        capture_output=True, text=True
    )
    assert "redmi note 12" in result.stdout  # 199 < 300
    assert "poco x5 pro" in result.stdout    # 299 < 300
    assert "iphone 15 pro" not in result.stdout # 999 > 300

    # Тест оператора 'равно' (=)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "brand=apple"],
        capture_output=True, text=True
    )
    assert "iphone 15 pro" in result.stdout
    assert "iphone 14" in result.stdout
    assert "samsung" not in result.stdout  # Посторонний бренд

    # Тест оператора 'больше или равно' (>=)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "rating>=4.7"],
        capture_output=True, text=True
    )
    assert "iphone 15 pro" in result.stdout  # 4.9 >= 4.7
    assert "iphone 14" in result.stdout      # 4.7 >= 4.7
    assert "galaxy a54" not in result.stdout # 4.2 < 4.7

    # Тест оператора 'меньше или равно' (<=)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "price<=799"],
        capture_output=True, text=True
    )
    assert "iphone 14" in result.stdout     # 799 <= 799
    assert "redmi note 12" in result.stdout # 199 <= 799
    assert "galaxy s23 ultra" not in result.stdout # 1199 > 799

    # Тест оператора 'не равно' (!=)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "brand!=apple"],
        capture_output=True, text=True
    )
    assert "samsung" in result.stdout
    assert "xiaomi" in result.stdout
    assert "apple" not in result.stdout  # Проверяем отсутствие записей apple

def test_aggregate_operations(sample_csv):
    """
    Тестирование агрегирующих функций (avg, min, max) через CLI.
    Проверяет что:
    1. Вычисляются корректные значения
    2. Результаты правильно форматируются в выводе
    """
    # Тест среднего значения (avg)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "rating=avg"],
        capture_output=True, text=True
    )
    # Ожидаемое значение: (4.9+4.8+4.6+4.4+4.7+4.2)/6 ≈ 4.6
    assert "4.6" in result.stdout  # Проверяем округление до десятых

    # Тест минимального значения (min)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "price=min"],
        capture_output=True, text=True
    )
    # Самый дешевый товар: redmi note 12 (199)
    assert "199" in result.stdout

    # Тест максимального значения (max)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "price=max"],
        capture_output=True, text=True
    )
    # Самый дорогой товар: galaxy s23 ultra (1199)
    assert "1199" in result.stdout

def test_combined_operations(sample_csv):
    """
    Тестирование КОМБИНАЦИИ фильтрации (--where) и агрегации (--aggregate).
    Проверяет что:
    1. Фильтрация применяется перед агрегацией
    2. Результаты вычислений корректны
    """
    # Сценарий 1: Фильтр по бренду + средняя цена
    result = subprocess.run(
        [
            "python", "-m", "project.main",
            "--file", sample_csv,
            "--where", "brand=xiaomi",  # Выбираем товары Xiaomi
            "--aggregate", "price=avg"   # Средняя цена по ним
        ],
        capture_output=True, text=True
    )
    # Расчет: (redmi note 12:199 + poco x5 pro:299) / 2 = 249
    assert "249" in result.stdout

    # Сценарий 2: Фильтр по рейтингу + максимальная цена
    result = subprocess.run(
        [
            "python", "-m", "project.main",
            "--file", sample_csv,
            "--where", "rating>=4.7",   # Товары с рейтингом ≥4.7
            "--aggregate", "price=max"   # Максимальная цена среди них
        ],
        capture_output=True, text=True
    )
    # Ожидаемый результат: 
    # iphone 15 pro (999), galaxy s23 ultra (1199), iphone 14 (799) → max=1199
    assert "1199" in result.stdout