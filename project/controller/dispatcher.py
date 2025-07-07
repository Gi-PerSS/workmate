import argparse
from typing import Dict, List, Tuple, Union, Any
from tabulate import tabulate
from project.model.csv_parser import CSVParser
from project.model.util import ExpressionParser
from project.model.processors import Aggregate, Where, OrderBy
from project.view.results_printer import print_results
from project.controller.cli_parser import CLIArgumentParser

# Определения аргументов командной строки
ARGUMENT_DEFINITIONS: dict[str, dict[str, any]] = {
    'file': {
        'type': str,
        'help': 'Путь к CSV-файлу',
        'required': True
    },
    'where': {
        'type': str,
        'help': 'Флаг фильтрации',
        'required': False
    },
    'aggregate': {
        'type': str,
        'help': 'Флаг агрегации',
        'required': False
    },
    'order-by': {
        'type': str,
        'help': 'Флаг порядка сортировки',
        'required': False
    }
}

class CLIArgumentsDispatcher:
    """Основной диспетчер, обрабатывающий аргументы командной строки и управляющий потоком выполнения."""

    @staticmethod
    def _processor_pipeline(
        csv_obj: List[Dict[str, str]],
        args: argparse.Namespace
    ) -> Union[List[Dict[str, str]], Dict[str, List[Any]]]:
        """Обрабатывает данные согласно переданным аргументам.

        Порядок обработки: where -> order_by -> aggregate.

        Args:
            csv_obj: Данные CSV в виде списка словарей.
            args: Аргументы командной строки.

        Returns:
            Обработанные данные в зависимости от аргументов.
        """
        data = csv_obj
        args_dict = vars(args)

        if args_dict.get('where'):
            expression = ExpressionParser.parse_expression(args.where)
            data = Where.execute(data, expression)

        if args_dict.get('order_by'):  # argparse заменяет дефисы на подчеркивания
            expression = ExpressionParser.parse_expression(args.order_by)
            data = OrderBy.execute(data, expression)

        if args_dict.get('aggregate'):
            expression = ExpressionParser.parse_expression(args.aggregate)
            _, _, aggregator_type = expression
            data = {aggregator_type: [Aggregate.execute(data, expression)]}

        return data

    @staticmethod
    def run() -> None:
        """Основной метод, запускающий обработку аргументов и данных."""
        parser = CLIArgumentParser(description='Workmate. Тестовое задание')
        for flag, params in ARGUMENT_DEFINITIONS.items():
            parser.add_argument('--'+flag, **params)
        args = parser.parse_args()
        csv_obj = CSVParser.parse(args.file)
        data = CLIArgumentsDispatcher._processor_pipeline(csv_obj, args)
        print_results(data)
