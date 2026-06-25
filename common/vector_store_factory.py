import logging

from langchain_core.vectorstores import VectorStore
from langchain_huggingface import HuggingFaceEmbeddings

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    EMBEDDING_VECTOR_SIZE,
    QDRANT_COLLECTION_NAME,
    QDRANT_SPARSE_MODEL,
    QDRANT_URL,
    VECTOR_STORE_TYPE,
)

logger = logging.getLogger(__name__)

_QDRANT_DENSE_VECTOR = "dense"
_QDRANT_SPARSE_VECTOR = "sparse"


def create_vector_store(embeddings: HuggingFaceEmbeddings) -> VectorStore:
    if VECTOR_STORE_TYPE == "chroma":
        from langchain_chroma import Chroma
        logger.info("Creating Chroma vector store with collection '%s'", CHROMA_COLLECTION_NAME)
        return Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
    elif VECTOR_STORE_TYPE == "qdrant":
        from langchain_qdrant import FastEmbedSparse, QdrantVectorStore, RetrievalMode
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance, SparseIndexParams, SparseVectorParams, VectorParams
        logger.info("Creating Qdrant vector store at '%s' with collection '%s'", QDRANT_URL, QDRANT_COLLECTION_NAME)
        client = QdrantClient(url=QDRANT_URL)
        sparse_embeddings = FastEmbedSparse(model_name=QDRANT_SPARSE_MODEL)

        if not client.collection_exists(QDRANT_COLLECTION_NAME):
            logger.info("Collection '%s' not found, creating...", QDRANT_COLLECTION_NAME)
            client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config={_QDRANT_DENSE_VECTOR: VectorParams(
                    size=EMBEDDING_VECTOR_SIZE, distance=Distance.COSINE,
                    )},
                sparse_vectors_config={_QDRANT_SPARSE_VECTOR: SparseVectorParams(index=SparseIndexParams())},
            )

        return QdrantVectorStore(
            client=client,
            collection_name=QDRANT_COLLECTION_NAME,
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name=_QDRANT_DENSE_VECTOR,
            sparse_vector_name=_QDRANT_SPARSE_VECTOR,
        )
    else:
        msg = f"Unknown vector store type: {VECTOR_STORE_TYPE}"
        raise ValueError(msg)
