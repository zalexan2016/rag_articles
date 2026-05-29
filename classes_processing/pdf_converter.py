import logging
import sys
from pathlib import Path

import pypdfium2 as pdfium
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.base import ImageRefMode

from classes_processing.base_converter import BaseConverter, ConversionStats
from config import PDF_SOURCE_DIR, SOURCE_MD_DIR, IMAGES_MD_DIR, PDF_EXTENSION, MD_EXTENSION, MIN_TEXT_CHARS_PER_PAGE

logger = logging.getLogger(__name__)


class PdfConverter(BaseConverter):
    def __init__(self, source_dir: Path = PDF_SOURCE_DIR, output_dir: Path = SOURCE_MD_DIR, images_dir: Path = IMAGES_MD_DIR):
        super().__init__(source_dir, output_dir, PDF_EXTENSION)
        self._images_dir = images_dir

    def run(self) -> ConversionStats:
        stats = ConversionStats()

        try:
            pdf_files = self._discover_files()
        except FileNotFoundError:
            logger.error("Source directory '%s' does not exist.", self._source_dir)
            sys.exit(1)

        stats.total_found = len(pdf_files)

        if not pdf_files:
            logger.warning("No PDF files found in '%s'.", self._source_dir)
            return stats

        to_convert, skipped = self._filter_unconverted(pdf_files)
        stats.skipped = len(skipped)

        if not to_convert:
            logger.info("All files already converted. Nothing to do.")
            return stats

        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._images_dir.mkdir(parents=True, exist_ok=True)

        for pdf_path in to_convert:
            pages = len(pdfium.PdfDocument(str(pdf_path)))
            logger.info("Processing: %s (%d pages)...", pdf_path.name, pages)
            needs_ocr = self._is_scanned_pdf(pdf_path)
            if needs_ocr:
                logger.info("  Detected as scanned PDF — OCR enabled.")
            try:
                converter = self._make_converter(ocr=needs_ocr, enrichments=True)
                output_path = self._output_dir / (pdf_path.stem + MD_EXTENSION)
                self._convert_and_save(pdf_path, output_path, converter)
                stats.converted += 1
            except Exception as e:
                logger.warning("Enriched conversion failed for '%s': %s. Retrying without enrichments...", pdf_path.name, e)
                try:
                    fallback = self._make_converter(ocr=needs_ocr, enrichments=False)
                    output_path = self._output_dir / (pdf_path.stem + MD_EXTENSION)
                    self._convert_and_save(pdf_path, output_path, fallback)
                    stats.converted += 1
                except Exception as e2:
                    stats.failed += 1
                    stats.errors.append("Failed to convert '%s': %s" % (pdf_path.name, e2))
                    logger.error("Failed to convert '%s': %s", pdf_path.name, e2)

        self._log_summary(stats)
        return stats

    def _is_scanned_pdf(self, pdf_path: Path) -> bool:
        doc = pdfium.PdfDocument(str(pdf_path))
        pages_to_check = min(3, len(doc))
        for i in range(pages_to_check):
            page = doc[i]
            text = page.get_textpage().get_text_range()
            if len(text.strip()) > MIN_TEXT_CHARS_PER_PAGE:
                doc.close()
                return False
        doc.close()
        return True

    def _make_converter(self, ocr: bool, enrichments: bool) -> DocumentConverter:
        return DocumentConverter(
            format_options={
                "pdf": PdfFormatOption(
                    pipeline_options=PdfPipelineOptions(
                        do_ocr=ocr,
                        generate_picture_images=True,
                        generate_page_images=False,
                        images_scale=2.0,
                        do_formula_enrichment=enrichments,
                        do_picture_classification=enrichments,
                        do_picture_description=False,
                    )
                )
            }
        )

    def _convert_and_save(self, pdf_path: Path, output_path: Path, converter: DocumentConverter) -> None:
        conv_res = converter.convert(source=str(pdf_path))
        artifacts_relative = self._images_dir.relative_to(self._output_dir)
        conv_res.document.save_as_markdown(
            filename=output_path,
            artifacts_dir=artifacts_relative,
            image_mode=ImageRefMode.REFERENCED,
        )
