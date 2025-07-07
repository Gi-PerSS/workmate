# test_dispatcher.py
import pytest
from unittest.mock import patch, MagicMock
from argparse import Namespace
from project.controller.dispatcher import CLIArgumentsDispatcher
from typing import List, Dict, Any

@pytest.fixture
def sample_csv_data() -> List[Dict[str, str]]:
    """Фикстура предоставляет тестовые данные CSV."""
    return [
        {"name": "iphone", "brand": "apple", "price": "999", "rating": "4.9"},
        {"name": "galaxy", "brand": "samsung", "price": "1199", "rating": "4.8"},
        {"name": "redmi", "brand": "xiaomi", "price": "199", "rating": "4.6"},
    ]

@pytest.fixture
def mock_args() -> Namespace:
    """Фикстура создает mock-объект аргументов командной строки."""
    return Namespace(
        file="test.csv",
        where=None,
        aggregate=None,
        order_by=None
    )

class TestProcessorPipeline:
    """Тестирование конвейера обработки данных."""
    
    def test_pipeline_without_args(self, sample_csv_data, mock_args):
        """Тест конвейера без дополнительных аргументов."""
        result = CLIArgumentsDispatcher._processor_pipeline(sample_csv_data, mock_args)
        assert result == sample_csv_data  # Данные должны остаться без изменений
        
    def test_pipeline_with_where(self, sample_csv_data, mock_args):
        """Тест конвейера с фильтрацией."""
        mock_args.where = "brand=apple"
        result = CLIArgumentsDispatcher._processor_pipeline(sample_csv_data, mock_args)
        assert len(result) == 1
        assert result[0]["brand"] == "apple"
        
    def test_pipeline_with_order_by(self, sample_csv_data, mock_args):
        """Тест конвейера с сортировкой."""
        mock_args.order_by = "price=asc"
        result = CLIArgumentsDispatcher._processor_pipeline(sample_csv_data, mock_args)
        prices = [item["price"] for item in result]
        assert prices == ["199", "999", "1199"]
        
    def test_pipeline_with_aggregate(self, sample_csv_data, mock_args):
        """Тест конвейера с агрегацией."""
        mock_args.aggregate = "price=avg"
        result = CLIArgumentsDispatcher._processor_pipeline(sample_csv_data, mock_args)
        assert "avg" in result
        # (999 + 1199 + 199) / 3 ≈ 799.0
        assert result["avg"][0] == pytest.approx(799.0, 0.1)
        
    def test_pipeline_full_flow(self, sample_csv_data, mock_args):
        """Тест полного конвейера обработки (where -> order_by -> aggregate)."""
        mock_args.where = "rating>4.6"
        mock_args.order_by = "price=desc"
        mock_args.aggregate = "price=max"
        result = CLIArgumentsDispatcher._processor_pipeline(sample_csv_data, mock_args)
        assert "max" in result
        assert result["max"][0] == 1199  # galaxy (после фильтрации и сортировки)

class TestCLIArgumentsDispatcher:
    """Тестирование основного диспетчера командной строки."""
    
    @patch('project.controller.dispatcher.CLIArgumentParser')
    @patch('project.controller.dispatcher.CSVParser.parse')
    @patch('project.controller.dispatcher.print_results')
    def test_run_method(
        self, 
        mock_print_results, 
        mock_parse, 
        mock_parser,
        sample_csv_data
    ):
        """Тест основного метода run() с моками зависимостей."""
        # Настройка mock-объектов
        mock_args = MagicMock()
        mock_args.file = "test.csv"
        mock_args.where = None
        mock_args.aggregate = None
        mock_args.order_by = None
        
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_args.return_value = mock_args
        mock_parser.return_value = mock_parser_instance
        
        mock_parse.return_value = sample_csv_data
        
        # Вызов тестируемого метода
        CLIArgumentsDispatcher.run()
        
        # Проверки
        mock_parser.assert_called_once()
        mock_parse.assert_called_once_with("test.csv")
        mock_print_results.assert_called_once_with(sample_csv_data)
        
    @patch('project.controller.dispatcher.CLIArgumentParser')
    def test_argument_definitions(self, mock_parser):
        """Тест корректности определения аргументов командной строки."""
        # Создаем mock для парсера
        mock_parser_instance = MagicMock()
        mock_parser.return_value = mock_parser_instance
        
        # Вызываем метод run
        CLIArgumentsDispatcher.run()
        
        # Проверяем что все аргументы были добавлены
        calls = mock_parser_instance.add_argument.call_args_list
        added_args = {call[0][0].lstrip('-') for call in calls}
        assert added_args == {'file', 'where', 'aggregate', 'order-by'}