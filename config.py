from pathlib import Path
import os

PDF_SOURCE_DIR = Path("source/pdf")
SOURCE_MD_DIR = Path("source/md")
IMAGES_MD_DIR = Path("source/md/img")
PDF_EXTENSION = ".pdf"
MD_EXTENSION = ".md"

# Минимальное кол-во символов текста на страницу чтобы считать PDF текстовым
MIN_TEXT_CHARS_PER_PAGE = 50

# Использовать локальный кэш моделей HuggingFace без обращения к серверу
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
