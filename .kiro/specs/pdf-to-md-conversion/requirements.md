# Requirements Document

## Introduction

Скрипт на Python для автоматической конвертации PDF-файлов в формат Markdown с использованием фреймворка Langchain и библиотеки Docling. Скрипт обрабатывает все PDF-файлы из указанной директории и сохраняет результат в виде .md файлов с сохранением исходных имён. Поддерживается инкрементальная обработка — файлы, для которых уже существует .md, пропускаются.

## Glossary

- **Converter**: Python-скрипт, выполняющий конвертацию PDF-файлов в Markdown
- **Source_Directory**: Директория `source/pdf/`, содержащая исходные PDF-файлы
- **Output_Directory**: Директория `source/md/`, в которую сохраняются результирующие Markdown-файлы
- **Images_Directory**: Директория `source/md/img/`, в которую сохраняются извлечённые из PDF изображения и графики
- **Docling**: Библиотека для извлечения структурированного контента из PDF-документов
- **Langchain**: Фреймворк для построения приложений с использованием LLM и обработки документов
- **DoclingLoader**: Компонент интеграции Langchain с Docling для загрузки PDF-документов
- **uv**: Быстрый пакетный менеджер для Python, используемый для управления зависимостями проекта

## Requirements

### Requirement 1: Обнаружение и чтение PDF-файлов

**User Story:** Как пользователь, я хочу, чтобы скрипт автоматически находил все PDF-файлы в исходной директории, чтобы мне не нужно было указывать каждый файл вручную.

#### Acceptance Criteria

1. WHEN the Converter is executed, THE Converter SHALL scan the Source_Directory for all files with the `.pdf` extension
2. WHEN the Source_Directory contains PDF files, THE Converter SHALL process each PDF file found
3. IF the Source_Directory does not exist, THEN THE Converter SHALL report an error with a descriptive message indicating the missing directory path
4. IF the Source_Directory contains no PDF files, THEN THE Converter SHALL report a warning message and exit gracefully

### Requirement 2: Инкрементальная обработка (пропуск уже сконвертированных файлов)

**User Story:** Как пользователь, я хочу, чтобы скрипт обрабатывал только новые PDF-файлы, для которых ещё нет соответствующего .md файла, чтобы не тратить время на повторную конвертацию.

#### Acceptance Criteria

1. WHEN the Converter discovers PDF files in the Source_Directory, THE Converter SHALL compare the list of PDF filenames with existing Markdown filenames in the Output_Directory
2. WHEN a PDF file has a corresponding Markdown file with the same base name in the Output_Directory, THE Converter SHALL skip that PDF file without processing
3. WHEN a PDF file does not have a corresponding Markdown file in the Output_Directory, THE Converter SHALL include that PDF file in the processing queue
4. WHEN all PDF files already have corresponding Markdown files, THE Converter SHALL report that no new files require conversion and exit gracefully
5. WHEN skipping already converted files, THE Converter SHALL print a message indicating which files were skipped

### Requirement 3: Конвертация PDF в Markdown с использованием Langchain и Docling

**User Story:** Как пользователь, я хочу, чтобы содержимое PDF-файлов конвертировалось в Markdown с сохранением структуры документа, чтобы я мог использовать текст в дальнейших задачах обработки.

#### Acceptance Criteria

1. WHEN a PDF file is loaded, THE Converter SHALL use the DoclingLoader from the langchain-docling integration to parse the PDF content
2. WHEN a PDF file is parsed, THE Converter SHALL extract the document content as Markdown-formatted text
3. WHEN the PDF contains tables, THE Converter SHALL convert them into Markdown table format preserving rows, columns, and headers
4. WHEN the PDF contains mathematical formulas, THE Converter SHALL convert them into LaTeX notation within the Markdown output
5. WHEN the PDF contains images or charts, THE Converter SHALL extract them, save to the Images_Directory (`source/md/img/`), and include relative image references (`img/<filename>`) in the Markdown output
6. WHEN the PDF contains structured elements such as headings, lists, and paragraphs, THE Converter SHALL preserve the hierarchy and formatting in the resulting Markdown output
7. IF a PDF file cannot be parsed, THEN THE Converter SHALL log an error message identifying the problematic file and continue processing remaining files

### Requirement 4: Сохранение результатов в Markdown-файлы

**User Story:** Как пользователь, я хочу, чтобы результаты конвертации сохранялись в виде .md файлов с теми же именами, что и исходные PDF, чтобы я мог легко соотнести исходные и результирующие файлы.

#### Acceptance Criteria

1. WHEN a PDF file is successfully converted, THE Converter SHALL save the Markdown content to the Output_Directory
2. WHEN saving the output file, THE Converter SHALL use the same base filename as the source PDF file with the `.md` extension replacing `.pdf`
3. WHEN the Output_Directory does not exist, THE Converter SHALL create the Output_Directory before saving files
4. IF writing a Markdown file fails, THEN THE Converter SHALL log an error message and continue processing remaining files

### Requirement 5: Отчёт о выполнении

**User Story:** Как пользователь, я хочу получать информацию о ходе конвертации, чтобы понимать, какие файлы были обработаны успешно, а какие — с ошибками.

#### Acceptance Criteria

1. WHEN processing each file, THE Converter SHALL print a progress message indicating the current file being processed
2. WHEN all files have been processed, THE Converter SHALL print a summary showing the total number of files found, skipped, successfully converted, and failed
3. IF errors occur during processing, THEN THE Converter SHALL include the error details in the final summary

### Requirement 6: Документация проекта (README.md)

**User Story:** Как пользователь, я хочу иметь файл README.md с понятной инструкцией, чтобы быстро понять куда класть PDF, где искать результаты и как запускать конвертацию.

#### Acceptance Criteria

1. WHEN the project is set up, THE project SHALL contain a README.md file in the root directory of the project
2. THE README.md SHALL contain a section describing where to place source PDF files (the `source/pdf/` directory)
3. THE README.md SHALL contain a section describing where to find the resulting Markdown files (the `source/md/` directory)
4. THE README.md SHALL contain a section with instructions on how to install dependencies using `uv` package manager (langchain-docling and related packages)
5. THE README.md SHALL contain a section with instructions on how to run the conversion script using `uv run`, including the exact command to execute
6. THE README.md SHALL contain a brief description of the project's purpose
