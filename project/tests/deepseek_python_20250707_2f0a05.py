import pytest
import subprocess
from pathlib import Path

@pytest.fixture
def sample_csv(tmp_path):
    """Фикстура создает временный CSV с тестовыми данными."""
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

def test_where_filter_operations(sample_csv):
    """Тест фильтрации (WHERE-условий) через CLI."""
    # Тест оператора 'больше' (>)
    result = subprocess.run(
        ["python", "-m", "project.main", "--file", sample_csv, "--where", "rating>4.7"],
        capture_output=True, text=True
    )
    
    # Должны отобразиться только товары с рейтингом > 4.7
    assert "iphone 15 pro" in result.stdout    # 4.9 > 4.7
    assert "galaxy s23 ultra" in result.stdout # 4.8 > 4.7
    assert "redmi note 12" not in result.stdout # 4.6 < 4.7 (этот assert падает)