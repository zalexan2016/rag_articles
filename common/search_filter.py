from config import RAG_EXCLUDED_SECTIONS


def build_search_filter() -> dict | None:
    if RAG_EXCLUDED_SECTIONS:
        return {"section": {"$nin": RAG_EXCLUDED_SECTIONS}}
    return None
