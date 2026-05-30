import logging
from dataclasses import dataclass, field

from langchain_core.vectorstores import VectorStore

from classes_processing.chunker import Chunker
from classes_processing.post_processor import PostProcessor
from classes_processing.processing_log import ProcessingLog
from config import MD_EXTENSION, PROCESSING_LOG_PATH, SOURCE_MD_DIR, UPSERT_BATCH_SIZE

logger = logging.getLogger(__name__)


@dataclass
class PipelineStats:
    total_found: int = 0
    skipped: int = 0
    processed: int = 0
    failed: int = 0
    total_chunks: int = 0
    errors: list[str] = field(default_factory=list)


class Pipeline:
    def __init__(self, vector_store: VectorStore):
        self._vector_store = vector_store
        self._post_processor = PostProcessor()
        self._chunker = Chunker()
        self._log = ProcessingLog(PROCESSING_LOG_PATH)

    def run(self) -> PipelineStats:
        stats = PipelineStats()

        if not SOURCE_MD_DIR.exists():
            logger.error("Source directory '%s' does not exist.", SOURCE_MD_DIR)
            return stats

        md_files = sorted(
            f for f in SOURCE_MD_DIR.iterdir()
            if f.is_file() and f.suffix == MD_EXTENSION
        )
        stats.total_found = len(md_files)

        if not md_files:
            logger.warning("No MD files found in '%s'.", SOURCE_MD_DIR)
            return stats

        files_to_process: list[tuple[str, str]] = []
        for md_path in md_files:
            filename = md_path.name
            try:
                content = md_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error("Failed to read file '%s': %s", filename, e)
                stats.failed += 1
                stats.errors.append(f"Read error: {filename}: {e}")
                continue

            content_hash = ProcessingLog.compute_hash(content)

            if self._log.is_processed(filename, content_hash):
                logger.info("Skipping '%s' — already processed.", filename)
                stats.skipped += 1
            else:
                files_to_process.append((filename, content))

        if not files_to_process:
            logger.info(
                "No new files require processing. All %s files are up to date.",
                stats.total_found,
            )
            self._log_summary(stats)
            return stats

        for idx, (filename, content) in enumerate(files_to_process, start=1):
            logger.info("Processing '%s' (%s/%s)...", filename, idx, len(files_to_process))
            try:
                processed_text = self._post_processor.process(content)
            except Exception as e:
                logger.error("Failed to post-process '%s': %s", filename, e)
                stats.failed += 1
                stats.errors.append(f"Post-processing error: {filename}: {e}")
                continue

            try:
                chunks = self._chunker.chunk(processed_text, filename)
            except Exception as e:
                logger.error("Failed to chunk '%s': %s", filename, e)
                stats.failed += 1
                stats.errors.append(f"Chunking error: {filename}: {e}")
                continue

            try:
                for i in range(0, len(chunks), UPSERT_BATCH_SIZE):
                    batch = chunks[i:i + UPSERT_BATCH_SIZE]
                    self._vector_store.add_documents(batch)
            except Exception as e:
                logger.error("Failed to add documents to vector store for '%s': %s", filename, e)
                stats.failed += 1
                stats.errors.append(f"Vector store error: {filename}: {e}")
                continue

            content_hash = ProcessingLog.compute_hash(content)
            try:
                self._log.update(filename, content_hash)
            except Exception as e:
                logger.warning("Failed to update processing log for '%s': %s", filename, e)

            stats.processed += 1
            stats.total_chunks += len(chunks)

        self._log_summary(stats)
        return stats

    def _log_summary(self, stats: PipelineStats) -> None:
        logger.info("--- Pipeline Summary ---")
        logger.info(
            "Total found: %s, Skipped: %s, Processed: %s, Failed: %s",
            stats.total_found,
            stats.skipped,
            stats.processed,
            stats.failed,
        )
