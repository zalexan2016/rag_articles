import logging
import re
from pathlib import Path

import easyocr
import ftfy

from config import OCR_LANGUAGES, SOURCE_MD_DIR

logger = logging.getLogger(__name__)


class PostProcessor:
    _HYPHEN_TRANSFER_NEWLINE = re.compile(r"(\w) -\n([a-zа-яё])")
    _HYPHEN_TRANSFER_SPACE = re.compile(r"(\w) -([a-zа-яё])")
    _SPACE_BEFORE_PUNCT = re.compile(r" +([.,;:!?])")
    _MULTIPLE_SPACES = re.compile(r" {2,}")
    _MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")
    _NON_PRINTABLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
    _PUA_CHARS = re.compile(r"[\ue000-\uf8ff]")
    _GLYPH_CODES = re.compile(r"/g\d+")
    _IMAGE_TAG = re.compile(r"!\[Image\]\(([^)]+)\)")
    _IMAGE_WITH_CLASS = re.compile(r"(!\[Image\]\(([^)]+)\))\n\n?(\w[\w\s]*)")

    def __init__(self, md_dir: Path = SOURCE_MD_DIR, gpu: bool = False):
        self._md_dir = md_dir
        self._gpu = gpu
        self._ocr_reader: easyocr.Reader | None = None

    def process(self, text: str) -> str:
        logger.info("Starting text post-processing, input length: %s chars", len(text))

        # OCR table images before other transformations change tags
        text = self._ocr_table_images(text)

        text = ftfy.fix_text(text)

        text = self._NON_PRINTABLE.sub("", text)
        text = self._PUA_CHARS.sub("", text)
        text = self._GLYPH_CODES.sub("", text)

        text = self._IMAGE_TAG.sub(r"[image: \1]", text)

        text = self._join_hyphen_transfers(text)

        lines = text.split("\n")
        processed_lines = []

        for line in lines:
            if self._is_skip_line(line):
                processed_lines.append(line)
            else:
                line = self._SPACE_BEFORE_PUNCT.sub(r"\1", line)
                line = self._MULTIPLE_SPACES.sub(" ", line)
                processed_lines.append(line)

        text = "\n".join(processed_lines)

        text = self._MULTIPLE_BLANK_LINES.sub("\n\n", text)

        logger.info("Post-processing complete, output length: %s chars", len(text))
        return text

    def _ocr_table_images(self, text: str) -> str:
        result = []
        last_end = 0

        for match in self._IMAGE_WITH_CLASS.finditer(text):
            img_tag = match.group(1)
            img_path = match.group(2)
            class_label = match.group(3).strip()

            result.append(text[last_end:match.start()])

            if class_label != "Table":
                result.append(match.group(0))
            else:
                abs_path = self._md_dir / img_path
                if not abs_path.exists():
                    logger.warning("Table image not found: %s", abs_path)
                    result.append(match.group(0))
                else:
                    try:
                        ocr_text = self._run_ocr(abs_path)
                        if ocr_text:
                            logger.info("OCR extracted %s chars from table: %s", len(ocr_text), img_path)
                            result.append(f"{img_tag}\n{ocr_text}")
                        else:
                            result.append(match.group(0))
                    except Exception as e:
                        logger.error("OCR failed for '%s': %s", img_path, e)
                        result.append(match.group(0))

            last_end = match.end()

        result.append(text[last_end:])
        return "".join(result)

    def _run_ocr(self, image_path: Path) -> str:
        if self._ocr_reader is None:
            self._ocr_reader = easyocr.Reader(OCR_LANGUAGES, gpu=self._gpu)

        results = self._ocr_reader.readtext(str(image_path))
        lines = [text for _, text, _ in results]
        return "\n".join(lines) if lines else ""

    def _is_skip_line(self, line: str) -> bool:
        stripped = line.strip()
        if stripped.startswith("|"):
            return True
        if stripped.startswith("#"):
            return True
        return False

    def _join_hyphen_transfers(self, text: str) -> str:
        text = self._HYPHEN_TRANSFER_NEWLINE.sub(r"\1\2", text)
        text = self._HYPHEN_TRANSFER_SPACE.sub(r"\1\2", text)
        return text
