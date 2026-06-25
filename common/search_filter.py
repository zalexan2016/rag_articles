from config import RAG_EXCLUDED_SECTIONS, VECTOR_STORE_TYPE


def build_search_filter() -> dict | None:
    if not RAG_EXCLUDED_SECTIONS:
        return None

    if VECTOR_STORE_TYPE == "qdrant":
        from qdrant_client.models import FieldCondition, Filter, MatchAny
        return Filter(
            must_not=[
                FieldCondition(
                    key="metadata.section",
                    match=MatchAny(any=RAG_EXCLUDED_SECTIONS),
                ),
            ],
        )

    # Chroma / default: MongoDB-style filter
    return {"section": {"$nin": RAG_EXCLUDED_SECTIONS}}
