import argparse
import sys


class CLIArgumentParser(argparse.ArgumentParser):
    """Кастомный парсер аргументов командной строки.

    Переопределяет стандартное поведение для вывода help-сообщения при ошибках.
    """
    def error(self, message: str) -> None:
        """Обработчик ошибок парсера.

        Args:
            message: Сообщение об ошибке.
        """
        self.print_help(sys.stderr)
        self.exit(2, f"\nОшибка: {message}\n")
