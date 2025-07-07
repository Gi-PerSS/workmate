from typing import Dict, List
import csv

class CSVParser:
    """Парсер CSV-файлов. Преобразует данные в список словарей."""
    @staticmethod
    def parse(file_path: str) -> List[Dict[str, str]]:
        """Чтение и парсинг CSV-файла.

        Args:
            file_path: Путь к CSV-файлу.

        Returns:
            Список словарей, где ключи - названия колонок, значения - данные ячеек.
        """
        with open(file_path, mode='r', encoding='utf-8') as csvfile:
            return list(csv.DictReader(csvfile))
