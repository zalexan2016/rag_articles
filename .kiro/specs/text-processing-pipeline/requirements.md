# Requirements Document

## Introduction

Пайплайн обработки текста для RAG-системы научных статей. Принимает на вход Markdown-файлы (результат конвертации PDF → MD из `source/md/`), выполняет пост-обработку текста, разбивает на чанки, генерирует векторные эмбеддинги и сохраняет в векторную базу данных Chroma с метаданными. Поддерживает инкрементальную обработку — уже проиндексированные документы повторно не обрабатываются. Языки документов: русский, английский, китайский.

## Glossary

- **Pipeline**: Python-модуль, выполняющий полный цикл обработки MD-файлов: пост-обработка → чанкинг → векторизация → сохранение в векторную БД
- **Post_Processor**: Компонент Pipeline, выполняющий нормализацию и очистку текста перед чанкингом
- **Chunker**: Компонент Pipeline, разбивающий пост-обработанный текст на фрагменты (чанки) с использованием HybridChunker из Docling
- **Embedder**: Компонент Pipeline, генерирующий векторные представления чанков с помощью модели intfloat/multilingual-e5-large через sentence-transformers
- **Vector_Store**: Абстрактный интерфейс для взаимодействия с векторной базой данных, с конкретными реализациями для Chroma (MVP) и Qdrant (production)
- **Chroma_Store**: Реализация Vector_Store для векторной БД ChromaDB
- **Qdrant_Store**: Реализация Vector_Store для векторной БД Qdrant
- **Chunk**: Фрагмент текста документа с ассоциированными метаданными, являющийся единицей хранения в векторной БД
- **Chunk_Metadata**: Набор атрибутов чанка: путь к исходному PDF-файлу (source), пути к изображениям (image_paths), номер страницы (page_number)
- **Source_Directory**: Директория `source/md/`, содержащая исходные Markdown-файлы для обработки
- **HybridChunker**: Компонент библиотеки Docling для гибридного разбиения документов на чанки
- **Hanging_Preposition**: Предлог или союз в конце строки, отделённый от связанного слова переносом строки (например, «в\nМоскве») — для RAG не критично, не обрабатывается
- **Processing_Log**: JSON-файл, хранящий список уже обработанных MD-файлов с хешами для отслеживания новых и изменённых документов

## Requirements

### Requirement 1: Обнаружение и чтение MD-файлов

**User Story:** Как пользователь, я хочу, чтобы Pipeline автоматически находил все MD-файлы в директории source/md/, чтобы мне не нужно было указывать каждый файл вручную.

#### Acceptance Criteria

1. WHEN the Pipeline is executed, THE Pipeline SHALL scan the Source_Directory for all files with the `.md` extension
2. WHEN the Source_Directory contains MD files, THE Pipeline SHALL collect the list of MD files for processing
3. IF the Source_Directory does not exist, THEN THE Pipeline SHALL log an error message indicating the missing directory path and terminate
4. IF the Source_Directory contains no MD files, THEN THE Pipeline SHALL log a warning message and exit gracefully

### Requirement 2: Инкрементальная обработка (пропуск проиндексированных документов)

**User Story:** Как пользователь, я хочу, чтобы Pipeline обрабатывал только новые или изменённые MD-файлы, чтобы не тратить ресурсы на повторную векторизацию уже проиндексированных документов.

#### Acceptance Criteria

1. WHEN the Pipeline discovers MD files in the Source_Directory, THE Pipeline SHALL check the Processing_Log to determine which files are new or modified
2. THE Processing_Log SHALL store the filename and content hash (MD5) for each processed file
3. WHEN an MD file hash matches the entry in the Processing_Log, THE Pipeline SHALL skip that file without processing
4. WHEN an MD file is new or its hash differs from the Processing_Log entry, THE Pipeline SHALL include that file in the processing queue
5. WHEN all MD files are already processed and unchanged, THE Pipeline SHALL log a message indicating no new files require processing and exit gracefully
6. WHEN skipping already processed files, THE Pipeline SHALL log which files were skipped
7. WHEN a file is successfully processed, THE Pipeline SHALL update the Processing_Log with the new hash

### Requirement 3: Пост-обработка текста

**User Story:** Как пользователь, я хочу, чтобы текст MD-файлов был нормализован перед чанкингом, чтобы устранить артефакты конвертации из PDF и повысить качество поиска.

#### Acceptance Criteria

1. WHEN an MD file is read, THE Post_Processor SHALL first apply `ftfy.fix_text()` to attempt Unicode encoding repair (e.g. `ÌÈÐÎÂÀß` → correct text if fixable)
2. WHEN an MD file contains characters that remain unreadable after ftfy fix (non-printable, mojibake sequences), THE Post_Processor SHALL remove them
3. WHEN an MD file is read, THE Post_Processor SHALL join words split by hyphen-transfer pattern (`слово -\nпродолжение` or `слово -продолжение`) into a single word, where a hyphen followed by a space and a lowercase letter indicates a line-break transfer
4. WHEN an MD file is read, THE Post_Processor SHALL remove spaces before punctuation marks (`. , ; : ! ?`) that are artifacts of PDF conversion (e.g. `г .` → `г.`)
5. WHEN an MD file is read, THE Post_Processor SHALL remove consecutive duplicate blank lines, replacing them with a single blank line
6. WHEN an MD file is read, THE Post_Processor SHALL replace sequences of multiple spaces with a single space
7. WHEN an MD file contains real compound words with hyphens (e.g. `золото-добывающей`), THE Post_Processor SHALL NOT remove those hyphens
8. WHEN an MD file contains Markdown heading markers (`##`), THE Post_Processor SHALL preserve heading structure intact
9. WHEN an MD file contains table markup (`|...|`), THE Post_Processor SHALL NOT apply normalization rules inside table rows
10. WHEN an MD file contains image references (`![Image](...)`), THE Post_Processor SHALL preserve image references intact
11. THE Post_Processor SHALL use `ftfy` for Unicode repair and the standard library `re` module for remaining normalization

### Requirement 4: Чанкинг документов

**User Story:** Как пользователь, я хочу, чтобы документы разбивались на семантически осмысленные фрагменты ограниченного размера, чтобы обеспечить точный поиск по векторной БД.

#### Acceptance Criteria

1. WHEN a post-processed document is ready, THE Chunker SHALL split the document into Chunks using HybridChunker from Docling
2. THE Chunker SHALL limit each Chunk to a maximum of 512 tokens
3. WHEN splitting a document, THE Chunker SHALL preserve semantic boundaries between sections where possible
4. WHEN a Chunk is created, THE Chunker SHALL attach Chunk_Metadata containing the source PDF path derived from the MD filename
5. WHEN images are referenced in the original MD file, THE Chunker SHALL include the image file paths in the Chunk_Metadata of the corresponding Chunk
6. WHEN page number information is available in the document, THE Chunker SHALL include the page number in the Chunk_Metadata

### Requirement 5: Генерация эмбеддингов

**User Story:** Как пользователь, я хочу, чтобы для каждого чанка генерировалось векторное представление, чтобы обеспечить семантический поиск по документам.

#### Acceptance Criteria

1. WHEN a Chunk is ready for vectorization, THE Embedder SHALL generate a vector embedding using the intfloat/multilingual-e5-large model via sentence-transformers
2. THE Embedder SHALL support documents in Russian, English, and Chinese languages without separate configuration
3. IF the embedding model is not available locally, THEN THE Embedder SHALL log an error message and terminate
4. WHEN generating embeddings, THE Embedder SHALL process Chunks in batches to optimize memory and performance

### Requirement 6: Сохранение в векторную БД

**User Story:** Как пользователь, я хочу, чтобы чанки с эмбеддингами сохранялись в векторную БД с метаданными батчами, чтобы впоследствии выполнять семантический поиск.

#### Acceptance Criteria

1. WHEN Chunks with embeddings are ready, THE Vector_Store SHALL persist Chunks in batches (not one by one) with their embeddings and Chunk_Metadata
2. THE Vector_Store SHALL accept a configurable batch size for upsert operations
3. THE Chunk_Metadata stored in Vector_Store SHALL contain the `source` field with the path to the original PDF file (not the MD file)
4. THE Chunk_Metadata stored in Vector_Store SHALL contain the `image_paths` field with paths to associated images from `source/md/img/`
5. WHERE page number information is available, THE Chunk_Metadata stored in Vector_Store SHALL contain the `page_number` field
6. THE Chroma_Store SHALL use a persistent storage directory for the Chroma database specified in config.py
7. IF writing to Vector_Store fails, THEN THE Pipeline SHALL log an error identifying the problematic document and continue processing remaining documents

### Requirement 7: Абстракция векторной БД через Dependency Injection

**User Story:** Как разработчик, я хочу, чтобы взаимодействие с векторной БД было абстрагировано через интерфейс, чтобы переключаться между Chroma и Qdrant через конфиг без изменения кода пайплайна.

#### Acceptance Criteria

1. THE Pipeline SHALL interact with the vector database exclusively through the Vector_Store abstract interface
2. THE Vector_Store interface SHALL define methods for adding documents in batches, checking document existence, and querying by vector similarity
3. THE Chroma_Store SHALL implement the Vector_Store interface for ChromaDB
4. THE Qdrant_Store SHALL implement the Vector_Store interface for Qdrant
5. THE Pipeline SHALL receive the Vector_Store implementation via dependency injection, configured in config.py
6. WHEN switching between Chroma and Qdrant, THE Pipeline SHALL require only a change in config.py (vector store type selector) without modifying pipeline code

### Requirement 8: Конфигурация пайплайна

**User Story:** Как пользователь, я хочу, чтобы все настройки пайплайна хранились в config.py, чтобы менять параметры без редактирования основного кода.

#### Acceptance Criteria

1. THE Pipeline SHALL read all configurable parameters from config.py
2. THE config.py SHALL contain the embedding model name (`intfloat/multilingual-e5-large`)
3. THE config.py SHALL contain the maximum chunk size in tokens (512)
4. THE config.py SHALL contain the Chroma database persistent storage path
5. THE config.py SHALL contain the vector store type selector for choosing between implementations
6. THE config.py SHALL contain the source MD directory path and source PDF directory path

### Requirement 9: Логирование и отчёт о выполнении

**User Story:** Как пользователь, я хочу получать информацию о ходе обработки, чтобы понимать статус индексации и выявлять проблемы.

#### Acceptance Criteria

1. WHEN processing each MD file, THE Pipeline SHALL log a progress message indicating the current file being processed
2. WHEN all files have been processed, THE Pipeline SHALL log a summary showing the total number of files found, skipped, successfully processed, and failed
3. IF errors occur during processing, THEN THE Pipeline SHALL include error details in the final summary
4. THE Pipeline SHALL use the Python logging module with `%s` substitution for all log messages
5. THE Pipeline SHALL log the number of chunks created and embeddings generated for each processed document
