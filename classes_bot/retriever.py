import asyncio
import logging

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from sentence_transformers import CrossEncoder

from classes_bot.exceptions import VectorStoreError
from config import RAG_EXCLUDED_SECTIONS, RAG_FETCH_K, RAG_MMR_K, RAG_TOP_K, RERANKER_MODEL

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self._reranker = CrossEncoder(RERANKER_MODEL)

    async def search(self, query: str) -> list[Document]:
        try:
            search_filter = None
            if RAG_EXCLUDED_SECTIONS:
                search_filter = {"section": {"$nin": RAG_EXCLUDED_SECTIONS}}

            # Stage 1: MMR selects diverse candidates
            candidates = await self._vector_store.amax_marginal_relevance_search(
                query,
                k=RAG_MMR_K,
                fetch_k=RAG_FETCH_K,
                filter=search_filter,
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

        # zip создаёт пары (score, document), sorted упорядочивает по score от большего к меньшему
        scored_docs = sorted(
            zip(scores, documents),
            key=lambda x: x[0],
            reverse=True,
        )
        return [doc for _, doc in scored_docs[:RAG_TOP_K]]
