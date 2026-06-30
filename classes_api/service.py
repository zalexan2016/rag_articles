from classes_api.schema import QueryResponse
from config import API_IMAGES_ROUTE, IMAGES_MD_DIR, SOURCE_MD_DIR
from core_rag.rag_chain import RAGChain

# image_paths from RAGChain are relative to SOURCE_MD_DIR (e.g. "img/doc/file.png")
# We strip the IMAGES_MD_DIR relative prefix and prepend the API route
_IMG_REL_PREFIX = str(IMAGES_MD_DIR.relative_to(SOURCE_MD_DIR)) + "/"


class QueryService:
    def __init__(self, rag_chain: RAGChain):
        self._rag_chain = rag_chain

    async def process(self, question: str) -> QueryResponse:
        result = await self._rag_chain.process(question)
        image_urls = [
            API_IMAGES_ROUTE + "/" + path.removeprefix(_IMG_REL_PREFIX)
            for path in result.image_paths
        ]
        return QueryResponse(
            answer=result.answer,
            sources=result.sources,
            image_paths=image_urls,
        )
