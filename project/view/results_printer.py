from typing import Union, List, Dict, Any
from tabulate import tabulate

def print_results(data: Union[List[Dict[str, str]], Dict[str, List[Any]]]) -> None:
    """Выводит результаты обработки в табличном формате.

    Args:
        data: Данные для вывода.
    """
    if data:
        print()
        print(tabulate(data, headers="keys", tablefmt="github"))
        print()
    else:
        print("Нет данных, соответствующих условиям")
