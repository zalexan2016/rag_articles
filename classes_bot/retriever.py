import asyncio
import logging

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from sentence_transformers import CrossEncoder

from classes_bot.exceptions import VectorStoreError
from common.search_filter import build_search_filter
from config import RAG_FETCH_K, RAG_MMR_K, RAG_TOP_K, RERANKER_MODEL

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self._reranker = CrossEncoder(RERANKER_MODEL)

    async def search(self, query: str) -> list[Document]:
        try:
            # Stage 1: MMR selects diverse candidates
            candidates = await self._vector_store.amax_marginal_relevance_search(
                query,
                k=RAG_MMR_K,
                fetch_k=RAG_FETCH_K,
                filter=build_search_filter(),
            )
            logger.info("MMR returned %s candidates", len(candidates))

            if not candidates:
                return []

            # Stage 2: Cross-encoder reranks candidates (in thread to avoid blocking event loop)
            results = await asyncio.to_thread(self._rerank, query, candidates)
            logger.info("Reranker selected %s chunks", len(results))
            return results
        except Exception as e:
            msg = f"Vector store search failed: {e}"
            raise VectorStoreError(msg) from e

    def _rerank(self, query: str, documents: list[Document]) -> list[Document]:
        pairs: list[tuple[str, str]] = [(query, doc.page_content) for doc in documents]
        scores: list[float] = self._reranker.predict(pairs).tolist()

        try:
            scored_docs = sorted(
                zip(scores, documents, strict=True),
                key=lambda x: x[0],
                reverse=True,
            )
        except ValueError:
            logger.error("Reranker scores/documents length mismatch: %s vs %s", len(scores), len(documents))
            return documents[:RAG_TOP_K]

        return [doc for _, doc in scored_docs[:RAG_TOP_K]]
