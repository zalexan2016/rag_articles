# Implementation Plan: PDF to Markdown Conversion

## Overview

Реализация однофайлового Python-скрипта `convert.py` для конвертации PDF-файлов в Markdown с использованием `langchain-docling`. Скрипт включает обнаружение файлов, инкрементальную обработку, конвертацию через `DoclingLoader` и формирование отчёта о выполнении. Также создаётся README.md с инструкциями по установке и запуску.

## Tasks

- [x] 1. Инициализация проекта и управление зависимостями
  - [x] 1.1 Создать файл pyproject.toml с зависимостями проекта
    - Создать `pyproject.toml` в корне проекта с указанием `langchain-docling` как зависимости
    - Указать минимальную версию Python 3.12+ (`requires-python = ">=3.12"`) и метаданные проекта
    - Настроить точку запуска через `uv run convert.py`
    - _Requirements: 6.4, 6.5_

- [x] 2. Реализация скрипта конвертации
  - [x] 2.1 Создать файл config.py с константами конфигурации
    - Создать `config.py` в корне проекта
    - Определить константы: `SOURCE_DIR = Path("source/pdf")`, `OUTPUT_DIR = Path("source/md")`, `IMAGES_DIR = Path("source/md/img")`, `PDF_EXTENSION = ".pdf"`, `MD_EXTENSION = ".md"`
    - Импортировать `Path` из `pathlib`
    - _Requirements: 1.1, 3.5, 4.1_

  - [x] 2.2 Создать файл convert.py с моделью данных и импортами
    - Определить dataclass `ConversionStats` с полями: `total_found`, `skipped`, `converted`, `failed`, `errors`
    - Импортировать константы из `config.py`: `from config import SOURCE_DIR, OUTPUT_DIR, PDF_EXTENSION, MD_EXTENSION`
    - Добавить необходимые импорты: `pathlib.Path`, `dataclasses`, `langchain_docling`
    - _Requirements: 5.2_

  - [x] 2.3 Реализовать функцию discover_pdf_files
    - Реализовать `discover_pdf_files(source_dir: Path) -> list[Path]`
    - Сканировать директорию на наличие файлов с расширением `.pdf`
    - Возвращать отсортированный список путей
    - Выбрасывать `FileNotFoundError` с описательным сообщением если директория не существует
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 2.4 Реализовать функцию filter_unconverted
    - Реализовать `filter_unconverted(pdf_files: list[Path], output_dir: Path) -> tuple[list[Path], list[Path]]`
    - Сравнивать базовые имена PDF с существующими .md файлами в output-директории
    - Возвращать кортеж: (файлы для конвертации, пропущенные файлы)
    - Выводить сообщение для каждого пропущенного файла
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 2.5 Реализовать функцию convert_pdf_to_markdown
    - Реализовать `convert_pdf_to_markdown(pdf_path: Path) -> str`
    - Использовать `DoclingLoader` с `export_type=ExportType.MARKDOWN`
    - Загрузить PDF и вернуть `page_content` первого документа
    - Обеспечить корректное извлечение таблиц, формул, заголовков и списков через настройки Docling
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 2.6 Реализовать функцию save_markdown
    - Реализовать `save_markdown(content: str, output_path: Path) -> None`
    - Создать выходную директорию если не существует (`mkdir(parents=True, exist_ok=True)`)
    - Записать контент в файл с кодировкой UTF-8
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 2.7 Реализовать функцию main — оркестратор
    - Реализовать `main() -> None` — главную функцию, координирующую все компоненты
    - Вызвать `discover_pdf_files`, обработать случаи пустой директории и отсутствия файлов
    - Вызвать `filter_unconverted` для определения файлов к обработке
    - В цикле обработать каждый файл: вывести прогресс, вызвать `convert_pdf_to_markdown`, вызвать `save_markdown`
    - Обрабатывать ошибки отдельных файлов через try/except без остановки процесса
    - Вывести итоговый отчёт: всего найдено, пропущено, сконвертировано, ошибки
    - Добавить блок `if __name__ == "__main__": main()`
    - _Requirements: 1.2, 2.4, 3.7, 4.4, 5.1, 5.2, 5.3_

- [x] 3. Checkpoint — Проверка работоспособности скрипта
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Создание документации
  - [x] 4.1 Создать README.md в корне проекта
    - Написать краткое описание проекта (назначение скрипта)
    - Добавить секцию с описанием структуры директорий (`source/pdf/` для исходников, `source/md/` для результатов)
    - Добавить секцию с инструкцией установки зависимостей через `uv` (команда `uv sync` или `uv pip install`)
    - Добавить секцию с инструкцией запуска скрипта (`uv run convert.py`)
    - Описать инкрементальную обработку (повторный запуск пропустит уже сконвертированные файлы)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 5. Final checkpoint — Финальная проверка
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Тестирование не включено — проект верифицируется вручную
- Каждая задача ссылается на конкретные требования для трассируемости
- Проект состоит из двух Python-файлов: `config.py` (константы) и `convert.py` (логика)
- Зависимости управляются через `uv` и `pyproject.toml`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3", "2.4", "2.5", "2.6"] },
    { "id": 4, "tasks": ["2.7"] },
    { "id": 5, "tasks": ["4.1"] }
  ]
}
```
