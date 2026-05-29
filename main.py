import argparse
import asyncio
import logging
import signal
import sys

import config  # noqa: F401 — loads .env and sets HF_HUB_OFFLINE

from langchain_huggingface import HuggingFaceEmbeddings

from classes_bot.bot import TelegramBot
from classes_bot.retriever import Retriever
from classes_bot.llm_factory import LLMFactory
from classes_bot.rag_chain import RAGChain
from classes_processing.pdf_converter import PdfConverter
from classes_processing.pipeline import Pipeline
from common.vector_store_factory import create_vector_store
from config import EMBEDDING_MODEL_NAME, TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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


async def run_bot() -> None:
    try:
        llm = LLMFactory.create()
    except Exception as e:
        logger.error("Failed to create LLM client: %s", e)
        sys.exit(1)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = create_vector_store(embeddings)
    retriever = Retriever(vector_store)
    rag_chain = RAGChain(retriever, llm)
    bot = TelegramBot(TELEGRAM_BOT_TOKEN, rag_chain)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.stop()))

    await bot.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG pipeline CLI")
    parser.add_argument("--convert-pdf", action="store_true", help="Convert PDF files to Markdown")
    parser.add_argument("--pipeline", action="store_true", help="Run text processing pipeline")
    parser.add_argument("--input", type=str, help="Search query against vector store")
    parser.add_argument("--bot", action="store_true", help="Start Telegram bot")
    args = parser.parse_args()

    if not args.convert_pdf and not args.pipeline and not args.input and not args.bot:
        parser.print_help()
        return

    if args.input and (args.convert_pdf or args.pipeline):
        parser.error("--input cannot be combined with --convert-pdf or --pipeline")

    if args.bot and (args.convert_pdf or args.pipeline or args.input):
        parser.error("--bot cannot be combined with other flags")

    if args.convert_pdf:
        run_convert()

    if args.pipeline:
        run_pipeline()

    if args.input:
        run_search(args.input)

    if args.bot:
        asyncio.run(run_bot())


if __name__ == "__main__":
    main()
