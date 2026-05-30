import logging

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore

from classes_bot.exceptions import VectorStoreError
from config import RAG_TOP_K

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, vector_store: VectorStore, top_k: int = RAG_TOP_K):
        self._vector_store = vector_store
        self._top_k = top_k

    async def search(self, query: str) -> list[Document]:
        try:
            results = await self._vector_store.asimilarity_search(query, k=self._top_k)
            logger.info("Found %s chunks for query", len(results))
            return results
        except Exception as e:
            msg = f"Vector store search failed: {e}"
            raise VectorStoreError(msg) from e
