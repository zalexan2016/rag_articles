import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


PDF_SOURCE_DIR = Path("source/pdf")
SOURCE_MD_DIR = Path("source/md")
IMAGES_MD_DIR = Path("source/md/img")
PDF_EXTENSION = ".pdf"
MD_EXTENSION = ".md"

# Минимальное кол-во символов текста на страницу чтобы считать PDF текстовым
MIN_TEXT_CHARS_PER_PAGE = 50

# 1 — use local HuggingFace cache (offline), 0 — allow downloading
os.environ["HF_HUB_OFFLINE"] = "1"

# --- Text Processing Pipeline ---
PROCESSING_LOG_PATH = Path("processing_log.json")

# Embedding
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"

# Chunking
MAX_CHUNK_TOKENS = 512

# Vector Store
VECTOR_STORE_TYPE = "chroma"  # "chroma" | "qdrant"

# DB Chroma
CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "documents"

# DB Qdrant (production)
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "documents"

# Batch settings
UPSERT_BATCH_SIZE = 64

# --- Telegram Bot ---
TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# --- LLM ---
LLM_API_KEY: str = os.environ.get("LLM_API_KEY", "")
LLM_MODEL: str = "gpt-4.1-mini"
LLM_BASE_URL: str = "https://api.openai.com/v1"

# --- RAG ---
RAG_TOP_K: int = 5
RAG_SYSTEM_PROMPT: str = (
    "Ты — ассистент, отвечающий на вопросы по научным статьям. "
    "Отвечай ТОЛЬКО на основе предоставленного контекста. "
    "Если информации недостаточно, скажи об этом. "
    "Отвечай на том же языке, на котором задан вопрос. "
    "Каждый фрагмент контекста помечен тегом [source: файл]. "
    "В конце ответа ОБЯЗАТЕЛЬНО укажи теги [source: файл] тех фрагментов, "
    "информацию из которых ты использовал в ответе. Не дублируй одинаковые. "
    "В контексте могут быть теги [image: путь_к_файлу] — это изображения из статей. "
    "Если ты использовал информацию из фрагмента, содержащего тег [image: ...], "
    "ОБЯЗАТЕЛЬНО скопируй этот тег в конец своего ответа без изменений. "
    "Если сообщение пользователя не является вопросом по теме статей "
    "(приветствие, благодарность, не относящийся к теме запрос), "
    "начни ответ с маркера [NO_SOURCES] и ответь коротко без ссылок на контекст."
)
RAG_USER_PROMPT: str = "Контекст:\n{context}\n\nВопрос: {question}"
