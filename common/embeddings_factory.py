from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL_NAME


def create_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
