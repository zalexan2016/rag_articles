# Requirements Document

## Introduction

Telegram-бот — пользовательский интерфейс для RAG-системы по научным статьям. Бот принимает текстовые вопросы от пользователей, выполняет семантический поиск по векторной базе данных, формирует ответ с помощью LLM и возвращает ответ с цитатами из источников и релевантными изображениями. Поддерживаемые языки документов: русский, английский, китайский.

## Glossary

- **Bot**: Telegram-бот на базе библиотеки iogramm, единственный канал взаимодействия пользователя с RAG-системой
- **User**: Пользователь Telegram, отправляющий вопросы боту
- **Retriever**: Компонент, выполняющий семантический поиск релевантных чанков в векторной БД (top-k, k=5)
- **LLM**: Языковая модель для генерации ответов (DeepSeek-V4-Flash API — production, Ollama + qwen2.5:7b — локальные тесты), подключение через LangChain (ChatOpenAI/ChatOllama)
- **Vector_Store**: Векторная база данных (Chroma для MVP, Qdrant для production), содержащая эмбеддинги чанков научных статей
- **Chunk**: Фрагмент текста научной статьи с метаданными (source — ссылка на PDF, image_paths — пути к изображениям на диске)
- **RAG_Chain**: LangChain-цепочка, объединяющая retrieval и генерацию ответа с контекстом
- **Source_Citation**: Ссылка на оригинальный PDF-документ из метаданных чанка (поле "source")
- **Image_Path**: Путь к изображению на диске (каталог source/md/img/), хранящийся в метаданных чанка

## Requirements

### Requirement 1: Приём вопросов пользователя

**User Story:** As a User, I want to send a text question to the Bot in Telegram, so that I can get an answer based on the scientific articles in the knowledge base.

#### Acceptance Criteria

1. WHEN a User sends a text message to the Bot, THE Bot SHALL accept the message as a question for the RAG system
2. WHILE the Bot is processing a previous question from the same User, THE Bot SHALL queue the new question and process it after the current one completes
3. IF a User sends a non-text message (sticker, voice, video), THEN THE Bot SHALL respond with a message explaining that only text questions are supported

### Requirement 2: Семантический поиск по векторной БД

**User Story:** As a User, I want the Bot to find relevant fragments of scientific articles for my question, so that the answer is grounded in the knowledge base.

#### Acceptance Criteria

1. WHEN the Bot receives a question from the User, THE Retriever SHALL perform an asynchronous similarity search in the Vector_Store and return the top 5 most relevant Chunks
2. THE Retriever SHALL use the same embedding model (intfloat/multilingual-e5-large) that was used during indexing
3. WHEN no relevant Chunks are found in the Vector_Store, THE Bot SHALL inform the User that no relevant information was found in the knowledge base
4. THE Retriever SHALL use async methods (asimilarity_search) to avoid blocking the asyncio event loop

### Requirement 3: Генерация ответа с помощью LLM

**User Story:** As a User, I want to receive a coherent answer synthesized from the relevant fragments, so that I don't have to read entire articles.

#### Acceptance Criteria

1. WHEN the Retriever returns relevant Chunks, THE RAG_Chain SHALL asynchronously pass the Chunks as context to the LLM along with the User question
2. THE RAG_Chain SHALL use a system prompt instructing the LLM to answer based only on the provided context and to indicate when information is insufficient
3. THE LLM SHALL generate an answer in the same language as the User question
4. IF the LLM determines that the provided context does not contain enough information to answer the question, THEN THE Bot SHALL inform the User that the knowledge base does not contain sufficient information for a complete answer

### Requirement 4: Цитирование источников

**User Story:** As a User, I want to see references to the original PDF documents in the answer, so that I can verify the information and find the full article.

#### Acceptance Criteria

1. WHEN the Bot sends an answer to the User, THE Bot SHALL include Source_Citations from the metadata of the Chunks used to generate the answer
2. THE Bot SHALL display each unique Source_Citation only once, even if multiple Chunks reference the same PDF
3. THE Bot SHALL format Source_Citations as a numbered list below the answer text

### Requirement 5: Отправка релевантных изображений

**User Story:** As a User, I want to see relevant images from the articles alongside the answer, so that I can better understand the information (charts, diagrams, figures).

#### Acceptance Criteria

1. WHEN the retrieved Chunks contain Image_Paths in their metadata, THE Bot SHALL send the corresponding image files to the User
2. THE Bot SHALL read image files from disk using the Image_Path from the Chunk metadata
3. IF an image file does not exist at the specified Image_Path, THEN THE Bot SHALL log a warning and skip the missing image without interrupting the answer delivery
4. THE Bot SHALL send images after the text answer and Source_Citations

### Requirement 6: Конфигурация LLM провайдера

**User Story:** As a developer, I want to switch between DeepSeek (API) and Ollama (local) LLM providers via configuration, so that I can use the local model for development and the API model for production.

#### Acceptance Criteria

1. WHERE the LLM provider is configured as "deepseek", THE RAG_Chain SHALL use ChatOpenAI with the DeepSeek API endpoint, DeepSeek-V4-Flash model, and API key from the .env file (loaded via config.py)
2. WHERE the LLM provider is configured as "ollama", THE RAG_Chain SHALL use ChatOllama with the local Ollama endpoint and the qwen2.5:7b model
3. THE Bot SHALL read the LLM provider setting from config.py at startup

### Requirement 7: Запуск и остановка бота

**User Story:** As a developer, I want to start and stop the Bot via a CLI command, so that I can integrate it into the existing project workflow.

#### Acceptance Criteria

1. WHEN the developer runs the application with the --bot flag, THE Bot SHALL start polling for Telegram updates
2. THE Bot SHALL use the Telegram bot token from the .env file (loaded via config.py)
3. IF the Telegram bot token is missing or invalid, THEN THE Bot SHALL log an error message and exit with a non-zero exit code
4. WHEN the Bot receives a SIGINT or SIGTERM signal, THE Bot SHALL perform a graceful shutdown and stop polling

### Requirement 8: Обработка ошибок

**User Story:** As a User, I want the Bot to handle errors gracefully, so that I always receive a meaningful response even when something goes wrong.

#### Acceptance Criteria

1. IF the Vector_Store is unreachable during a search, THEN THE Bot SHALL send the User a message indicating a temporary service error and log the error details
2. IF the LLM API returns an error or times out, THEN THE Bot SHALL send the User a message indicating that answer generation failed and log the error details
3. IF an unexpected error occurs during question processing, THEN THE Bot SHALL send the User a generic error message and log the full exception traceback

### Requirement 9: Логирование

**User Story:** As a developer, I want the Bot to log its operations, so that I can diagnose issues and monitor bot activity.

#### Acceptance Criteria

1. THE Bot SHALL log each incoming question from the User at INFO level, including the User identifier
2. THE Bot SHALL log the retrieval result (number of Chunks found) at INFO level
3. THE Bot SHALL log all errors at ERROR level with the full exception context
4. THE Bot SHALL use the standard Python logging module with %s-style string formatting
