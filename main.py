import argparse
import logging
import config  # noqa: F401 — sets HF_HUB_OFFLINE before other imports

from langchain_huggingface import HuggingFaceEmbeddings

from classes_processing.pdf_converter import PdfConverter
from classes_processing.pipeline import Pipeline
from common.vector_store_factory import create_vector_store
from config import EMBEDDING_MODEL_NAME

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def run_convert() -> None:
    converter = PdfConverter()
    converter.run()


def run_pipeline() -> None:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = create_vector_store(embeddings)
    pipeline = Pipeline(vector_store)
    pipeline.run()


def run_search(query: str) -> None:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = create_vector_store(embeddings)

    hits = vector_store.similarity_search(query, k=5)

    print(f"\n=== Search: '{query}' ===\n")

    for i, hit in enumerate(hits):
        print(f"[{i+1}]")
        print(f"  text:        {hit.page_content}")
        print(f"  source:      {hit.metadata.get('source')}")
        print(f"  image_paths: {hit.metadata.get('image_paths')}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG pipeline CLI")
    parser.add_argument("--convert-pdf", action="store_true", help="Convert PDF files to Markdown")
    parser.add_argument("--pipeline", action="store_true", help="Run text processing pipeline")
    parser.add_argument("--input", type=str, help="Search query against vector store")
    args = parser.parse_args()

    if not args.convert_pdf and not args.pipeline and not args.input:
        parser.print_help()
        return

    if args.input and (args.convert_pdf or args.pipeline):
        parser.error("--input cannot be combined with --convert-pdf or --pipeline")

    if args.convert_pdf:
        run_convert()

    if args.pipeline:
        run_pipeline()

    if args.input:
        run_search(args.input)


if __name__ == "__main__":
    main()
