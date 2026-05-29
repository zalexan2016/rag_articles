# RAG Pipeline

Пайплайн для обработки научных статей: конвертация PDF → Markdown, пост-обработка текста, чанкинг, векторизация и семантический поиск. Языки документов: русский, английский, китайский.

## Структура проекта

```
main.py                          # Точка входа CLI
config.py                        # Все настройки
common/
  vector_store_factory.py        # Factory для Chroma/Qdrant
classes_processing/
  base_converter.py              # ABC для конвертеров
  pdf_converter.py               # PDF → Markdown (Docling)
  pipeline.py                    # Пост-обработка + чанкинг + vectorstore
  chunker.py                     # HybridChunker (Docling) → LangChain Documents
  post_processor.py              # Нормализация текста (ftfy + regex)
  processing_log.py              # Инкрементальная обработка (MD5)
source/
  pdf/                           # Исходные PDF
  md/                            # Результаты конвертации
    img/                         # Извлечённые изображения
```

## Установка

### Системные зависимости (Ubuntu/Debian)

```bash
sudo apt-get install -y libgl1
```

### Python-зависимости

Проект использует `uv`.

**CPU-режим:**

```bash
uv sync --extra cpu
```

**GPU-режим** (NVIDIA GPU + CUDA 12.4):

```bash
uv sync --extra gpu
```

## Использование

### Конвертация PDF → Markdown

```bash
uv run python main.py --convert
```

Сканирует `source/pdf/`, конвертирует новые PDF в Markdown через Docling. Уже сконвертированные файлы пропускаются.

### Запуск пайплайна обработки

```bash
uv run python main.py --pipeline
```

Обрабатывает MD-файлы из `source/md/`:
1. Пост-обработка текста (ftfy, удаление артефактов конвертации)
2. Чанкинг через HybridChunker (max 512 токенов)
3. Сохранение в векторную БД (Chroma/Qdrant) с метаданными

Уже проиндексированные документы пропускаются (инкрементальная обработка по MD5).

### Семантический поиск

```bash
uv run python main.py --input "золото Чукотка"
```

Ищет топ-5 релевантных чанков в векторной БД и выводит текст, source и пути к изображениям.

### Комбинированный запуск

```bash
uv run python main.py --convert --pipeline
```

## Конфигурация

Все настройки в `config.py`:

| Параметр | Значение | Описание |
|----------|----------|----------|
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-large` | Модель эмбеддингов |
| `MAX_CHUNK_TOKENS` | `512` | Макс. размер чанка |
| `VECTOR_STORE_TYPE` | `chroma` / `qdrant` | Тип векторной БД |
| `UPSERT_BATCH_SIZE` | `64` | Размер батча для записи |

Переключение между Chroma и Qdrant — одна строка в `config.py`.

## Метаданные чанков

| Поле | Описание |
|------|----------|
| `source` | Путь к оригинальному PDF |
| `image_paths` | JSON-массив путей к изображениям в чанке |
