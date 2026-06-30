# Tasks

## Task 1: Create Pydantic schemas and service layer

- [x] Create `classes_api/__init__.py`
- [x] Create `classes_api/schema.py` with `QueryParams`, `QueryResponse`, `ErrorResponse` Pydantic models
- [x] Create `classes_api/service.py` with `QueryService` class wrapping `RAGChain`

## Task 2: Implement authentication dependency

- [x] Create `classes_api/auth.py` with `verify_api_key` FastAPI dependency
- [x] Use `HTTPBearer` with `auto_error=False`
- [x] Return 503 if API_KEY is empty, 401 if no credentials, 403 if token is invalid

## Task 3: Implement API router with /query endpoint

- [x] Create `classes_api/router.py` with `create_query_router(service)` factory
- [x] Implement `GET /query` endpoint with `Annotated[str, Query(min_length=1)]` parameter
- [x] Wire `verify_api_key` dependency and `QueryResponse` response model

## Task 4: Create FastAPI app factory with error handlers

- [x] Create `classes_api/app.py` with `create_app(rag_chain)` factory function
- [x] Register exception handlers for `VectorStoreError` → 502, `LLMError` → 502, generic `Exception` → 500
- [x] Include query router

## Task 5: Implement API server with uvicorn and PID management

- [x] Create `classes_api/server.py` with `APIServer` class
- [x] Implement programmatic uvicorn launch with config from `API_HOST`, `API_PORT`
- [x] Implement PID file write/remove and SIGINT/SIGTERM signal handlers for graceful shutdown

## Task 6: Integrate --api flag into CLI

- [x] Add `--api` argument to argparse in `main.py`
- [x] Add `run_api()` async function with lazy imports (same pattern as `run_bot`)
- [x] Add validation: `--api` cannot combine with other flags (same as `--bot`)
- [x] Add `uvicorn` and `fastapi` to dependencies in `pyproject.toml`

## Task 7: Update config, .env.example and README

- [x] Add `API_KEY` to `.env.example`
- [x] Update README: document `--api` flag, API usage with curl example, config table with API_KEY/API_HOST/API_PORT
