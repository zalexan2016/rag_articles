import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ProcessingLog:
    def __init__(self, log_path: Path):
        self._log_path = log_path
        self._data: dict[str, str] = {}
        if self._log_path.exists():
            with open(self._log_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            logger.info("Loaded processing log from '%s' with %s entries", self._log_path, len(self._data))
        else:
            logger.info("Processing log '%s' not found, starting fresh", self._log_path)

    def is_processed(self, filename: str, content_hash: str) -> bool:
        stored_hash = self._data.get(filename)
        if stored_hash == content_hash:
            logger.debug("File '%s' already processed with hash %s", filename, content_hash)
            return True
        return False

    def update(self, filename: str, content_hash: str) -> None:
        self._data[filename] = content_hash
        with open(self._log_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        logger.info("Updated processing log: '%s' -> %s", filename, content_hash)

    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()
