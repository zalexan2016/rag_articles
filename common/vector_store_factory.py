import logging

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    QDRANT_COLLECTION_NAME,
    QDRANT_URL,
    VECTOR_STORE_TYPE,
)

logger = logging.getLogger(__name__)


def create_vector_store(embeddings: HuggingFaceEmbeddings) -> VectorStore:
    if VECTOR_STORE_TYPE == "chroma":
        logger.info("Creating Chroma vector store with collection '%s'", CHROMA_COLLECTION_NAME)
        return Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
    elif VECTOR_STORE_TYPE == "qdrant":
        logger.info("Creating Qdrant vector store at '%s' with collection '%s'", QDRANT_URL, QDRANT_COLLECTION_NAME)
        client = QdrantClient(url=QDRANT_URL)
        return QdrantVectorStore(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME,
            embedding=embeddings,
        )
    else:
        msg = f"Unknown vector store type: {VECTOR_STORE_TYPE}"
        raise ValueError(msg)
