import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from classes_api.router import create_query_router
from classes_api.service import QueryService
from config import API_IMAGES_ROUTE, IMAGES_MD_DIR
from core_rag.exceptions import LLMError, VectorStoreError
from core_rag.rag_chain import RAGChain

logger = logging.getLogger(__name__)


def create_app(rag_chain: RAGChain) -> FastAPI:
    app = FastAPI(title="RAG API")

    service = QueryService(rag_chain)
    query_router = create_query_router(service)
    app.include_router(query_router)
    app.mount(API_IMAGES_ROUTE, StaticFiles(directory=str(IMAGES_MD_DIR)), name="images")

    @app.exception_handler(VectorStoreError)
    async def vector_store_error_handler(_request: Request, exc: VectorStoreError) -> JSONResponse:
        logger.error("VectorStoreError: %s", exc, exc_info=True)
        return JSONResponse(status_code=502, content={"detail": "Ошибка сервиса поиска"})

    @app.exception_handler(LLMError)
    async def llm_error_handler(_request: Request, exc: LLMError) -> JSONResponse:
        logger.error("LLMError: %s", exc, exc_info=True)
        return JSONResponse(status_code=502, content={"detail": "Ошибка сервиса генерации"})

    @app.exception_handler(Exception)
    async def generic_error_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})

    return app
