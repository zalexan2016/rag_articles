# Project Constitution

## Описание проекта

RAG-пайплайн для обработки научных статей. Этапы: конвертация PDF → Markdown, пост-обработка, чанкинг, векторизация, поиск и генерация ответов с помощью запросов-ответов в чат-боте Telegram (библиотека iogramm). Языки документов: русский, английский, китайский.

## Стек

- Python 3.12+
- Пакетный менеджер: `uv`
- **LangChain** — основной фреймворк (максимально использовать его экосистему для всех компонентов)
- Конвертация PDF: Docling (напрямую, без langchain-обёртки для конвертации)
- Embedding: `intfloat/multilingual-e5-large` через `langchain-huggingface` (HuggingFaceEmbeddings)
- Векторные БД: `langchain-chroma` (MVP), `langchain-qdrant` (production)
- Чанкинг: HybridChunker из langchain-docling
- Telegram-бот: iogramm
- LLM: DeepSeek (API) — production, Ollama + qwen2.5:7b — локальные тесты (6 GB VRAM)

## Архитектурные решения

- Подключение к векторным БД через LangChain-интерфейсы (`langchain-chroma`, `langchain-qdrant`), переключение через config.py
- Перед чанкингом: пост-обработка текста (убрать лишние переносы строк, множественные пробелы, висячие предлоги)
- Чанкинг: HybridChunker (Docling), max_tokens=512
- Retrieval: top-k (k=5 для MVP, без reranking)
- LLM для генерации ответов: DeepSeek (API) — production, Ollama + qwen2.5:7b — локальные тесты (6 GB VRAM), подключение через LangChain (ChatOpenAI/ChatOllama)
- Telegram-бот — единый канал взаимодействия пользователя с RAG-системой (приём вопросов, возврат ответов с цитатами из документов)
- Картинки хранятся на диске (`source/md/img/`), в векторной БД — только ссылки (пути) в метаданных чанка. Бот отправляет картинки по пути из метаданных.
- Метаданные чанка содержат `source` — ссылку на оригинальный PDF (не MD), т.к. MD после пост-обработки может быть нечитаем для человека.

## Стандарты кода

- ООП стиль
- Логирование через `logging` (logger), не print
- В логгере использовать `%s` подстановку, не f-строки
- Конфигурация хранится в `config.py`
- Без подробных docstrings — код читается по именам
- Без тестов — проект верифицируется вручную

## Структура проекта

- `config.py` — все константы и настройки
- `convert.py` — конвертация PDF → MD
- `source/pdf/` — исходные PDF
- `source/md/` — результаты конвертации
- `source/md/img/` — извлечённые изображения
- `pyproject.toml` — зависимости, CPU/GPU extras

## Окружение

- Два режима: `uv sync --extra cpu` и `uv sync --extra gpu`
- GPU: CUDA 12.4, torch 2.6.0
- HF_HUB_OFFLINE для офлайн-работы с моделями
