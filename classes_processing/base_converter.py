import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

from config import MD_EXTENSION

logger = logging.getLogger(__name__)


@dataclass
class ConversionStats:
    total_found: int = 0
    skipped: int = 0
    converted: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


class BaseConverter(ABC):
    def __init__(self, source_dir: Path, output_dir: Path, source_extension: str):
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._source_extension = source_extension

    @abstractmethod
    def run(self) -> ConversionStats:
        ...

    def _discover_files(self) -> list[Path]:
        if not self._source_dir.exists():
            raise FileNotFoundError("Source directory '%s' does not exist." % self._source_dir)
        return sorted(p for p in self._source_dir.iterdir() if p.suffix == self._source_extension)

    def _filter_unconverted(self, source_files: list[Path]) -> tuple[list[Path], list[Path]]:
        to_convert: list[Path] = []
        skipped: list[Path] = []

        for src_path in source_files:
            md_filename = src_path.stem + MD_EXTENSION
            md_path = self._output_dir / md_filename

            if md_path.exists():
                logger.info("SKIP: '%s' — '%s' exists.", src_path.name, md_filename)
                skipped.append(src_path)
            else:
                to_convert.append(src_path)

        return to_convert, skipped

    def _log_summary(self, stats: ConversionStats) -> None:
        logger.info("--- Conversion Summary ---")
        logger.info("Total found: %d", stats.total_found)
        logger.info("Skipped: %d", stats.skipped)
        logger.info("Converted: %d", stats.converted)
        logger.info("Failed: %d", stats.failed)
        if stats.errors:
            for error in stats.errors:
                logger.error("  %s", error)
