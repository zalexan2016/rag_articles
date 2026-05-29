# RAG Pipeline

Пайплайн для обработки научных статей: конвертация PDF → Markdown, пост-обработка текста, чанкинг, векторизация, семантический поиск и Telegram-бот с ответами через LLM. Языки документов: русский, английский, китайский.

## Структура проекта

```
main.py                          # Точка входа CLI
config.py                        # Все настройки
.env                             # Секреты (не в git)
.env.example                     # Пример переменных окружения
common/
  vector_store_factory.py        # Factory для Chroma/Qdrant
classes_processing/
  base_converter.py              # ABC для конвертеров
  pdf_converter.py               # PDF → Markdown (Docling)
  pipeline.py                    # Пост-обработка + чанкинг + vectorstore
  chunker.py                     # HybridChunker (Docling) → LangChain Documents
  post_processor.py              # Нормализация текста (ftfy + regex)
  processing_log.py              # Инкрементальная обработка (MD5)
classes_bot/
  bot.py                         # TelegramBot (aiogram 3.x, polling)
  handlers.py                    # Роутер сообщений
  rag_chain.py                   # RAG-оркестратор (retrieval + LLM)
  retriever.py                   # Async обёртка над VectorStore
  llm_factory.py                 # Фабрика LLM (DeepSeek/Ollama/OpenAI)
  exceptions.py                  # Кастомные исключения
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

### Переменные окружения

Скопировать `.env.example` → `.env` и заполнить:

```bash
cp .env.example .env
```

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
LLM_API_KEY=your_llm_api_key_here
```

## Использование

### Конвертация PDF → Markdown

```bash
uv run python main.py --convert-pdf
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

Ищет топ-5 релевантных чанков в векторной БД.

### Telegram-бот

```bash
uv run python main.py --bot
```

Запускает бота, который принимает вопросы, ищет в БД, генерирует ответ через LLM и отправляет с цитатами и изображениями.

### Комбинированный запуск

```bash
uv run python main.py --convert-pdf --pipeline
```

## Конфигурация LLM

Настройки в `config.py`. Логика: если `LLM_API_KEY` задан — используется OpenAI-совместимый API, если пустой — Ollama.

**DeepSeek (production):**
```python
LLM_MODEL = "deepseek-v4-flash"
LLM_BASE_URL = "https://api.deepseek.com/v1"
# LLM_API_KEY в .env
```

**Ollama (локальные тесты):**
```python
LLM_MODEL = "qwen2.5:7b"
LLM_BASE_URL = "http://localhost:11434"
# LLM_API_KEY оставить пустым в .env
```

**OpenAI:**
```python
LLM_MODEL = "gpt-4o"
LLM_BASE_URL = "https://api.openai.com/v1"
# LLM_API_KEY в .env
```

`LLM_API_KEY` — единый ключ для любого платного API, хранится в `.env`.

## Конфигурация пайплайна

| Параметр | Значение | Описание |
|----------|----------|----------|
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-large` | Модель эмбеддингов |
| `MAX_CHUNK_TOKENS` | `512` | Макс. размер чанка |
| `VECTOR_STORE_TYPE` | `chroma` / `qdrant` | Тип векторной БД |
| `UPSERT_BATCH_SIZE` | `64` | Размер батча для записи |
| `RAG_TOP_K` | `5` | Количество чанков для retrieval |

## Метаданные чанков

| Поле | Описание |
|------|----------|
| `source` | Путь к оригинальному PDF |
| `image_paths` | JSON-массив путей к изображениям в чанке |
