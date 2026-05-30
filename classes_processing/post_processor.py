import logging
import re

import ftfy

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

    def process(self, text: str) -> str:
        logger.info("Starting text post-processing, input length: %s chars", len(text))

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
