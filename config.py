import logging
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
# OCR mode: None = auto-detect, True = always on, False = always off
PDF_OCR_MODE: bool | None = None
# EasyOCR languages for table image recognition
OCR_LANGUAGES: list[str] = ["ru", "en"]

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 1 — use local HuggingFace cache (offline), 0 — allow downloading
os.environ["HF_HUB_OFFLINE"] = "1"

# Disable tqdm progress bars from sentence-transformers and safetensors
os.environ["TQDM_DISABLE"] = "1"

# --- Text Processing Pipeline ---
PROCESSING_LOG_PATH = Path("processing_log.json")

# Embedding
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large"  # RU-only alt: ai-forever/ru-en-RoSBERTa
EMBEDDING_VECTOR_SIZE = 1024  # must match the model output dimension

# Chunking
MAX_CHUNK_TOKENS = 512

# Vector Store
VECTOR_STORE_TYPE = "qdrant"  # "chroma" | "qdrant"

# DB Chroma
CHROMA_PERSIST_DIR = "chroma_db"
CHROMA_COLLECTION_NAME = "documents"

# DB Qdrant (production)
QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "documents"
QDRANT_SPARSE_MODEL = "Qdrant/bm25"  # multilingual alt: "Qdrant/bm42-all-minilm-l6-v2-attentions"

# Batch settings
UPSERT_BATCH_SIZE = 64

# --- Telegram Bot ---
TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WELCOME_MESSAGE: str = "Привет! Я готов ответить на ваши вопросы."

# Allowed Telegram usernames (without @). Empty = allow all.
# Example: frozenset({"alice", "bob"})
ACCESS_USERNAMES: frozenset[str] = frozenset()
PROTECT_CONTENT: bool = True  # disable message forwarding/saving in Telegram

# --- LLM ---
LLM_API_KEY: str = os.environ.get("LLM_API_KEY", "")
LLM_MODEL: str = "deepseek-v4-flash"
LLM_BASE_URL: str = "https://api.deepseek.com"

# --- RAG ---
RAG_TOP_K: int = 5  # final number of chunks sent to LLM
RAG_CANDIDATES_K: int = 15  # candidates before reranking (MMR for Chroma, hybrid for Qdrant)
RAG_FETCH_K: int = 20  # initial vector search pool for MMR (Chroma only)
RAG_SHOW_SOURCES: bool = True  # show source filenames in bot response
RERANKER_MODEL: str = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"  # RU-only alt: DiTy/cross-encoder-russian-msmarco
RAG_SYSTEM_PROMPT: str = (
    "Ты — ассистент, отвечающий на вопросы по научным статьям. "
    "Отвечай ТОЛЬКО на основе предоставленного контекста. "
    "ВСЕГДА отвечай СТРОГО на том же языке, на котором задан вопрос. "
    "Если вопрос на английском — отвечай на английском. Если на русском — на русском. "
    "Каждый фрагмент контекста помечен тегом [source: файл]. "
    "В конце ответа ОБЯЗАТЕЛЬНО укажи теги [source: файл] тех фрагментов, "
    "информацию из которых ты использовал в ответе. Не дублируй одинаковые. "
    "В контексте могут быть теги [image: путь_к_файлу] — это изображения из статей. "
    "Если ты использовал информацию из фрагмента, содержащего тег [image: ...], "
    "ОБЯЗАТЕЛЬНО скопируй этот тег в конец своего ответа БЕЗ изменений, в точном формате [image: путь]. "
    "НЕ используй markdown-формат для изображений (не пиши ![...](...)), только [image: путь]. "
    "НЕ упоминай теги [section: ...] в ответе — они только для внутренней навигации. "
    "Если информации в контексте недостаточно для ответа, или вопрос не относится к теме статей, "
    "начни ответ с маркера [NO_SOURCES] и НЕ указывай никаких тегов [source:] и [image:]. "
    "Ответ об отсутствии информации тоже должен быть на языке вопроса."
)
RAG_USER_PROMPT: str = "Контекст:\n{context}\n\nВопрос: {question}"

# Sections to exclude from retrieval (references, bibliographies, etc.)
RAG_EXCLUDED_SECTIONS: list[str] = [
    "Литература",
    "References",
    "Библиографическое описание данной статьи",
    "Bibliographic description",
    "Information about the authors",
    "Информация об авторах",
]
