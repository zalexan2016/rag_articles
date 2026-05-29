# Implementation Plan: Text Processing Pipeline

## Overview

Реализация пайплайна обработки текста для RAG-системы. Компоненты создаются инкрементально: сначала конфигурация и утилиты (ProcessingLog, PostProcessor), затем Chunker, factory для vector store, и наконец оркестратор Pipeline, связывающий всё воедино. Используется LangChain-экосистема для embeddings и vector store, кастомные классы — только для пост-обработки, логирования и оркестрации.

## Tasks

- [x] 1. Добавить зависимости и расширить конфигурацию
  - [x] 1.1 Добавить зависимости в pyproject.toml
    - Добавить `langchain-huggingface`, `langchain-chroma`, `langchain-qdrant`, `ftfy` в секцию `dependencies`
    - `langchain-docling` уже присутствует
    - _Requirements: 8.1, 5.1, 6.6_

  - [x] 1.2 Расширить config.py настройками пайплайна
    - Добавить константы: `SOURCE_MD_DIR`, `SOURCE_PDF_DIR`, `PROCESSING_LOG_PATH`
    - Добавить `EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"`
    - Добавить `MAX_CHUNK_TOKENS = 512`
    - Добавить `VECTOR_STORE_TYPE = "chroma"`, `CHROMA_PERSIST_DIR`, `CHROMA_COLLECTION_NAME`
    - Добавить `QDRANT_URL`, `QDRANT_COLLECTION_NAME`
    - Добавить `UPSERT_BATCH_SIZE = 64`
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 2. Реализовать ProcessingLog
  - [x] 2.1 Создать файл `processing_log.py` с классом ProcessingLog
    - Реализовать `__init__(self, log_path: Path)` — загрузка JSON-файла при наличии
    - Реализовать `is_processed(self, filename: str, content_hash: str) -> bool`
    - Реализовать `update(self, filename: str, content_hash: str) -> None` — обновление записи и сохранение на диск
    - Реализовать `compute_hash(content: str) -> str` — статический метод, MD5 от содержимого
    - Формат JSON: `{filename: md5_hex_digest}`
    - Использовать `logging` с `%s` подстановкой
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7_

- [x] 3. Реализовать PostProcessor
  - [x] 3.1 Создать файл `post_processor.py` с классом PostProcessor
    - Реализовать метод `process(self, text: str) -> str`
    - Порядок операций: `ftfy.fix_text()` → удаление нечитаемых символов → склейка переносов → удаление пробелов перед пунктуацией → замена множественных пробелов → схлопывание пустых строк
    - Строки таблиц (`|...|`) — пропускать при нормализации
    - Ссылки на изображения (`![Image](...)`) — сохранять как есть
    - Markdown-заголовки — структуру сохранять
    - Реальные составные слова с дефисом — не затрагивать
    - Зависимости: `ftfy`, `re`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11_

- [x] 4. Реализовать Chunker
  - [x] 4.1 Создать файл `chunker.py` с классом Chunker
    - Реализовать `__init__(self, max_tokens: int, tokenizer: str)` — создание `HybridChunker` из `docling.chunking`
    - Реализовать `chunk(self, text: str, md_filename: str) -> list[Document]`
    - Преобразовывать имя MD-файла в путь к PDF: `01_arctic_gold_2017.md` → `source/pdf/01_arctic_gold_2017.pdf`
    - Извлекать ссылки на изображения из текста (`![Image](img/...)`)
    - Метаданные Document: `source` (путь к PDF), `image_paths` (JSON-строка), `page_number`
    - Возвращать `list[Document]` — LangChain-объекты
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 5. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Реализовать Vector Store Factory и PipelineStats
  - [x] 6.1 Создать файл `vector_store_factory.py` с функцией `create_vector_store()`
    - Принимает `embeddings: HuggingFaceEmbeddings`, возвращает `VectorStore`
    - При `VECTOR_STORE_TYPE == "chroma"` — создать `Chroma` с `persist_directory` и `collection_name`
    - При `VECTOR_STORE_TYPE == "qdrant"` — создать `QdrantClient` и `QdrantVectorStore`
    - При неизвестном типе — `ValueError`
    - Импорты: `langchain_chroma.Chroma`, `langchain_qdrant.QdrantVectorStore`, `qdrant_client.QdrantClient`
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [x] 6.2 Создать dataclass `PipelineStats` в файле `pipeline.py`
    - Поля: `total_found`, `skipped`, `processed`, `failed`, `total_chunks`, `errors: list[str]`
    - _Requirements: 9.2, 9.3_

- [x] 7. Реализовать Pipeline (оркестратор)
  - [x] 7.1 Создать класс `Pipeline` в файле `pipeline.py`
    - `__init__(self, vector_store: VectorStore)` — принимает LangChain VectorStore через DI
    - Создаёт внутренние компоненты: `PostProcessor`, `Chunker`, `ProcessingLog`
    - Реализовать метод `run(self) -> PipelineStats`
    - Сканирование `SOURCE_MD_DIR` на `.md` файлы
    - Фильтрация через `ProcessingLog` (пропуск уже обработанных)
    - Цикл: чтение файла → `PostProcessor.process` → `Chunker.chunk` → `vector_store.add_documents` (батчами по `UPSERT_BATCH_SIZE`) → `ProcessingLog.update`
    - Стратегия ошибок: fail-per-file, логирование и продолжение
    - Если `SOURCE_MD_DIR` не существует — логировать error, завершиться
    - Если нет MD-файлов — логировать warning, выйти gracefully
    - Если все файлы обработаны — логировать info, выйти
    - Итоговый отчёт: total found, skipped, processed, failed
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.3, 2.4, 2.5, 2.6, 5.3, 5.4, 6.1, 6.2, 6.7, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 7.2 Создать функцию `main()` в файле `pipeline.py`
    - Создать `HuggingFaceEmbeddings` с `model_name` из конфига
    - Вызвать `create_vector_store(embeddings)`
    - Создать `Pipeline(vector_store)` и вызвать `run()`
    - Добавить блок `if __name__ == "__main__"` для запуска
    - _Requirements: 5.1, 5.2, 7.5, 8.2_

- [x] 8. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Тесты не создаются — проект верифицируется вручную (согласно constitution)
- Docstrings не нужны — код читается по именам
- Логирование через `logging` модуль с `%s` подстановкой, не f-строки
- Все настройки — в `config.py`, не хардкодить в модулях
- OOP стиль, Python 3.12+
- Зависимости добавляются в `pyproject.toml`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["2.1", "3.1"] },
    { "id": 2, "tasks": ["4.1"] },
    { "id": 3, "tasks": ["6.1", "6.2"] },
    { "id": 4, "tasks": ["7.1"] },
    { "id": 5, "tasks": ["7.2"] }
  ]
}
```
