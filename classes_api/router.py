from typing import Annotated

from fastapi import APIRouter, Depends, Query

from classes_api.auth import verify_api_key
from classes_api.schema import QueryResponse
from classes_api.service import QueryService


def create_query_router(service: QueryService) -> APIRouter:
    router = APIRouter()

    @router.get("/query", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
    async def query(question: Annotated[str, Query(min_length=1)]) -> QueryResponse:
        return await service.process(question)

    return router
