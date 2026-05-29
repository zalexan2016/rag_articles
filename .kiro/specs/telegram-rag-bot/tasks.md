# Implementation Plan: Telegram RAG Bot

## Overview

Реализация Telegram-бота как пользовательского интерфейса для существующей RAG-системы. Бот принимает текстовые вопросы, выполняет семантический поиск по векторной БД, генерирует ответ через LLM (DeepSeek/Ollama) и возвращает пользователю текст с цитатами и изображениями. Реализация полностью асинхронная на aiogram 3.x + LangChain async API.

## Tasks

- [x] 1. Настройка конфигурации и зависимостей
  - [x] 1.1 Расширить config.py настройками бота и LLM
    - Добавить `from dotenv import load_dotenv` и `load_dotenv()` в начало файла
    - Добавить `import os` (если отсутствует)
    - Добавить настройки: TELEGRAM_BOT_TOKEN, DEEPSEEK_API_KEY, LLM_PROVIDER, DEEPSEEK_MODEL, DEEPSEEK_BASE_URL, OLLAMA_BASE_URL, OLLAMA_MODEL, RAG_TOP_K
    - Значения TELEGRAM_BOT_TOKEN и DEEPSEEK_API_KEY загружаются из .env через os.environ.get
    - _Requirements: 6.1, 6.2, 6.3, 7.2_

  - [x] 1.2 Добавить зависимости в pyproject.toml
    - Добавить в основные зависимости: aiogram, python-dotenv, langchain-openai, langchain-ollama
    - _Requirements: 6.1, 6.2_

  - [x] 1.3 Создать структуру каталога classes_bot/
    - Создать `classes_bot/__init__.py`
    - Создать `classes_bot/exceptions.py` с классами BotError, VectorStoreError, LLMError
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 2. Реализация инфраструктурных компонентов
  - [x] 2.1 Реализовать LLMFactory (classes_bot/llm_factory.py)
    - Класс LLMFactory со статическим методом create() -> BaseChatModel
    - При LLM_PROVIDER == "deepseek": возвращает ChatOpenAI с параметрами из config
    - При LLM_PROVIDER == "ollama": возвращает ChatOllama с параметрами из config
    - При неизвестном провайдере: поднимает ValueError
    - Логирование создания через logger.info с %s подстановкой
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 2.2 Реализовать Retriever (classes_bot/retriever.py)
    - Класс Retriever с конструктором принимающим VectorStore и top_k
    - Метод async search(query: str) -> list[Document]
    - Вызывает vector_store.asimilarity_search(query, k=self._top_k)
    - Оборачивает ошибки VectorStore в VectorStoreError
    - Логирование количества найденных чанков через logger.info
    - _Requirements: 2.1, 2.4, 8.1_

- [x] 3. Реализация RAG-цепочки
  - [x] 3.1 Реализовать RAGChain (classes_bot/rag_chain.py)
    - Dataclass RAGResult с полями: answer (str), sources (list[str]), image_paths (list[str])
    - Класс RAGChain с конструктором принимающим Retriever и BaseChatModel
    - Метод async process(question: str) -> RAGResult
    - Формирование промпта: системный промпт + контекст из chunks + вопрос пользователя
    - Вызов LLM через ainvoke(messages)
    - Извлечение sources из metadata с дедупликацией
    - Извлечение image_paths из metadata всех chunks
    - Обработка пустого результата поиска — возврат RAGResult с сообщением "не найдено"
    - Оборачивание ошибок LLM в LLMError
    - Логирование на каждом этапе
    - _Requirements: 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1_

  - [ ]* 3.2 Написать property-тест для формирования промпта
    - **Property 1: Prompt contains all context and question**
    - **Validates: Requirements 3.1**

  - [ ]* 3.3 Написать property-тест для дедупликации источников
    - **Property 2: Source citation deduplication and formatting**
    - **Validates: Requirements 4.1, 4.2, 4.3**

  - [ ]* 3.4 Написать property-тест для извлечения image_paths
    - **Property 3: Image paths extraction completeness**
    - **Validates: Requirements 5.1**

- [x] 4. Checkpoint - Проверка core-логики
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Реализация Telegram-интерфейса
  - [x] 5.1 Реализовать MessageHandler (classes_bot/handlers.py)
    - Класс MessageHandler с конструктором принимающим RAGChain
    - Создание aiogram Router в конструкторе
    - Метод async handle_text(message: Message) — обработка текстовых сообщений
    - Отправка typing action перед обработкой
    - Вызов rag_chain.process(question)
    - Форматирование ответа: текст + "📚 Источники:" + нумерованный список
    - Отправка изображений отдельными сообщениями (проверка существования файла на диске)
    - Метод async handle_unsupported(message: Message) — ответ что поддерживаются только текстовые вопросы
    - Трёхуровневая обработка ошибок: VectorStoreError, LLMError, Exception
    - Логирование входящих вопросов (user_id, текст) на INFO
    - Логирование ошибок на ERROR с контекстом
    - _Requirements: 1.1, 1.3, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 5.4, 8.1, 8.2, 8.3, 9.1, 9.2, 9.3, 9.4_

  - [x] 5.2 Реализовать TelegramBot (classes_bot/bot.py)
    - Класс TelegramBot с конструктором принимающим token и RAGChain
    - Создание aiogram Bot и Dispatcher
    - Подключение роутера из MessageHandler к Dispatcher
    - Метод async start() — запуск polling через Dispatcher.start_polling()
    - Метод async stop() — graceful shutdown
    - Валидация наличия token при запуске: если пустой — logger.error + sys.exit(1)
    - _Requirements: 1.2, 7.1, 7.2, 7.3, 7.4_

  - [ ]* 5.3 Написать property-тест для последовательной обработки сообщений
    - **Property 4: Sequential per-user message processing**
    - **Validates: Requirements 1.2**

- [x] 6. Интеграция и точка входа
  - [x] 6.1 Добавить флаг --bot в main.py
    - Добавить аргумент --bot в argparse (action="store_true")
    - Реализовать функцию run_bot(): создание embeddings, vector_store, Retriever, LLMFactory.create(), RAGChain, TelegramBot и запуск
    - Обработка SIGINT/SIGTERM для graceful shutdown
    - Добавить проверку совместимости --bot с другими флагами
    - Валидация DEEPSEEK_API_KEY при LLM_PROVIDER == "deepseek"
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 6.2 Обновить classes_bot/__init__.py с экспортом основных классов
    - Экспортировать TelegramBot, RAGChain, Retriever, LLMFactory, MessageHandler
    - _Requirements: 7.1_

- [x] 7. Final checkpoint - Полная проверка
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Задачи помеченные `*` являются опциональными (property-based тесты) — проект по конституции верифицируется вручную
- Каждая задача ссылается на конкретные требования для прослеживаемости
- Используется Python как язык реализации (явно указан в дизайне)
- Все настройки в config.py, секреты из .env через python-dotenv
- Логирование через logging с %s подстановкой (не f-строки)
- ООП стиль, без docstrings
- Существующий `common/vector_store_factory.py` переиспользуется для создания VectorStore

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["3.1"] },
    { "id": 3, "tasks": ["3.2", "3.3", "3.4", "5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3"] },
    { "id": 5, "tasks": ["6.1", "6.2"] }
  ]
}
```
