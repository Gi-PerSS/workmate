# Workmate CSV Processor

Тестовое задание для Workmate - скрипт на Python для обработки CSV-файлов.

## Возможности

- **Фильтрация**: Поддержка условий `where` с операторами `>`, `<`, `>=`, `<=`, `=`, `!=` для точного выбора данных.
- **Сортировка**: Поддержка `order-by` для сортировки данных по возрастанию (`asc`) или убыванию (`desc`) по указанному полю.
- **Агрегация**: Вычисление `avg`, `min`, `max` и `median` для числовых столбцов.
- **Ввод**: Прием пути к CSV-файлу и аргументов через `argparse`.
- **Вывод**: Отображение результатов в удобном табличном формате с использованием `tabulate`.
- **Расширяемость**: Модульная архитектура.
- **Тестирование**: Покрытие кода тестами более 90% с использованием `pytest` для модульных и end-to-end тестов.
- **Надежность**: Аннотации типов и обработка ошибок обеспечивают удобство поддержки и надежность кода.

## Структура проекта

```
.
├── Workmate/
│   ├── project/
│   │   ├── main.py         # Точка входа для выполнения через CLI
│   │   ├── controller/     # Парсинг CLI и логика диспетчеризации
│   │   ├── model/          # Парсинг CSV, обработка данных и утилиты
│   │   ├── view/           # Форматирование и вывод результатов
│   │   └── tests/          # Модульные и end-to-end тесты
├── sample/
│   └── products.csv        # Пример CSV-файла для тестирования
├── requirements.txt         # Зависимости проекта
└── README.md
```

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Gi-PerSS/workmate
   cd workmate
   ```
2. Установите зависимости:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```
3. Наслаждайтесь! :)

## Примеры использования

- Фильтрация товаров с ценой > 500:
  ```bash
  python -m project.main --file sample/products.csv --where "price>500"
  ```
- Фильтрация товаров с ценой > 500 и выводом списка в порядке убывания:
  ```bash
  python -m project.main --file sample/products.csv --where "price>500" --order-by "price=desc"
  ```
- Вычисление средней цены:
  ```bash
  python -m project.main --file sample/products.csv --aggregate "price=avg"
  ```
- Фильтрация по бренду Apple и максимальная цена:
  ```bash
  python -m project.main --file sample/products.csv --where "brand=apple" --aggregate "price=max"
  ```
- Расчет медианы (порог разделяющий 2 части упорядоченного списка):
  ```bash
  python -m project.main --file sample/products.csv --where "brand=apple" --aggregate "rating=median"
  ```

## Запуск тестов

```bash
pytest project/tests
pytest --cov=project
```

## Требования

- Python 3.12+
- Стандартные библиотеки: `argparse`, `csv`
- Внешняя библиотека: `tabulate`
- Тестирование: `pytest`, `pytest-cov`

## Примечания

- диалекты csv не обрабатываются
- поддерживается одна кодировка: utf-8
- переустановка проекта:
  ```bash
  pip uninstall workmate
  rm -rf build/ dist/ *.egg-info/
  pip install -e .
  ```
