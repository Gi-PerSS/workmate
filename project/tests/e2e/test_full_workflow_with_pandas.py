import pytest
import subprocess
from pathlib import Path
import pandas as pd  # Импортируем pandas для эталонных вычислений

@pytest.fixture
def sample_csv(tmp_path):
    """Фикстура создает временный CSV-файл с тестовыми данными."""
    file_path = tmp_path / "products.csv"
    file_path.write_text(
        "name,brand,price,rating\n"
        "iphone 15 pro,apple,999,4.9\n"
        "galaxy s23 ultra,samsung,1199,4.8\n"
        "redmi note 12,xiaomi,199,4.6\n"
        "poco x5 pro,xiaomi,299,4.4\n"
        "iphone 14,apple,799,4.7\n"
        "galaxy a54,samsung,349,4.2"
    )
    return str(file_path)

def test_basic_output(sample_csv):
    """Тестирует базовый вывод без параметров."""
    # Запускаем команду
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv],
        capture_output=True, text=True
    )
    
    # Проверяем успешность выполнения
    assert result.returncode == 0
    
    # Проверяем наличие основных товаров в выводе
    assert "iphone 15 pro" in result.stdout
    assert "galaxy s23 ultra" in result.stdout
    assert "redmi note 12" in result.stdout

def test_where_filter_operations(sample_csv):
    """Тестирует все операторы фильтрации: >, <, =, >=, <=, !=."""
    # Читаем тестовые данные в DataFrame для эталонных вычислений
    df = pd.read_csv(sample_csv)
    
    # Тест для оператора >
    filtered = df[df['rating'] > 4.7]
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "rating>4.7"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "redmi note 12" not in result.stdout  # Негативная проверка

    # Тест для оператора <
    filtered = df[df['price'] < 300]
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "price<300"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "iphone 15 pro" not in result.stdout

    # Тест для оператора =
    filtered = df[df['brand'] == 'apple']
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "brand=apple"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "samsung" not in result.stdout

    # Тест для оператора >=
    filtered = df[df['rating'] >= 4.7]
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "rating>=4.7"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "galaxy a54" not in result.stdout

    # Тест для оператора <=
    filtered = df[df['price'] <= 799]
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "price<=799"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "galaxy s23 ultra" not in result.stdout

    # Тест для оператора !=
    filtered = df[df['brand'] != 'apple']
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "brand!=apple"],
        capture_output=True, text=True
    )
    for _, row in filtered.iterrows():
        assert row['name'] in result.stdout
    assert "apple" not in result.stdout

def test_aggregate_operations(sample_csv):
    """Тестирует все виды агрегации: avg, min, max с использованием pandas как эталона."""
    df = pd.read_csv(sample_csv)
    
    # Тест для avg
    expected_avg = df['rating'].mean()
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "rating=avg"],
        capture_output=True, text=True
    )
    # Проверяем что вывод содержит ожидаемое значение с точностью до 1 знака
    assert f"{expected_avg:.1f}" in result.stdout

    # Тест для min
    expected_min = df['price'].min()
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "price=min"],
        capture_output=True, text=True
    )
    assert str(int(expected_min)) in result.stdout  # Цены у нас целые

    # Тест для max
    expected_max = df['price'].max()
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--aggregate", "price=max"],
        capture_output=True, text=True
    )
    assert str(int(expected_max)) in result.stdout

def test_combined_operations(sample_csv):
    """Тестирует комбинацию фильтрации и агрегации с pandas-верификацией."""
    df = pd.read_csv(sample_csv)
    
    # Фильтрация по бренду + средняя цена
    filtered = df[df['brand'] == 'xiaomi']
    expected_avg = filtered['price'].mean()
    result = subprocess.run(
        [
            "python", "-m", "project.main",
            "--file", sample_csv,
            "--where", "brand=xiaomi",
            "--aggregate", "price=avg"
        ],
        capture_output=True, text=True
    )
    # Проверяем целое число если среднее целое, иначе 1 знак после запятой
    if expected_avg.is_integer():
        assert str(int(expected_avg)) in result.stdout
    else:
        assert f"{expected_avg:.1f}" in result.stdout

    # Фильтрация по рейтингу + максимальная цена
    filtered = df[df['rating'] >= 4.7]
    expected_max = filtered['price'].max()
    result = subprocess.run(
        [
            "python", "-m", "project.main",
            "--file", sample_csv,
            "--where", "rating>=4.7",
            "--aggregate", "price=max"
        ],
        capture_output=True, text=True
    )
    assert str(int(expected_max)) in result.stdout