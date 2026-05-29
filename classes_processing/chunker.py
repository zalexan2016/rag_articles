import json
import logging
import re
from io import BytesIO

from docling.chunking import HybridChunker
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import DocumentStream
from docling.document_converter import DocumentConverter
from langchain_core.documents import Document

from config import EMBEDDING_MODEL_NAME, MAX_CHUNK_TOKENS, PDF_EXTENSION, PDF_SOURCE_DIR

logger = logging.getLogger(__name__)

IMAGE_PATTERN = re.compile(r'\[image: ([^\]]+)\]')


class Chunker:
    def __init__(self, max_tokens: int = MAX_CHUNK_TOKENS, tokenizer: str = EMBEDDING_MODEL_NAME):
        self._chunker = HybridChunker(
            tokenizer=tokenizer,
            max_tokens=max_tokens,
        )
        self._converter = DocumentConverter(allowed_formats=[InputFormat.MD])

    def chunk(self, text: str, md_filename: str) -> list[Document]:
        source_pdf = str(PDF_SOURCE_DIR / md_filename.replace(".md", PDF_EXTENSION))

        dl_doc = self._text_to_docling_document(text, md_filename)
        raw_chunks = list(self._chunker.chunk(dl_doc))

        documents = []
        for chunk in raw_chunks:
            image_paths = self._extract_image_paths(chunk.text)
            doc = Document(
                page_content=chunk.text,
                metadata={
                    "source": source_pdf,
                    "image_paths": json.dumps(image_paths),
                },
            )
            documents.append(doc)

        logger.info("Created %s chunks from '%s'", len(documents), md_filename)
        return documents

    def _text_to_docling_document(self, text: str, filename: str):
        stream = DocumentStream(
            name=filename,
            stream=BytesIO(text.encode("utf-8")),
        )
        result = self._converter.convert(stream)
        return result.document

    def _extract_image_paths(self, text: str) -> list[str]:
        return IMAGE_PATTERN.findall(text)
