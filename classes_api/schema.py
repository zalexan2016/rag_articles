from pydantic import BaseModel, Field


class QueryParams(BaseModel):
    question: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    image_paths: list[str]


class ErrorResponse(BaseModel):
    detail: str
