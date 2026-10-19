"""
OsintNeoAi Indexer: Document Extraction & Neural OCR Package
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\extractors\\__init__.py
Milestone: M2 (Deep Text Extraction & OCR Engine)

Exposes the 5-Tier Fallback DocumentExtractor, OCREngine, ImageEnhancer,
and format-specific extractors (TIFF, HTML, DOCX, Image, Text).
"""

from extractors.ocr_engine import (
    OCRPoint,
    OCRLine,
    OCRPageResult,
    OCREngine,
    RapidOCREngine,
)
from extractors.image_enhancer import (
    EnhancementProfile,
    ImageEnhancer,
)
from extractors.format_extractors import (
    TiffPageResult,
    TiffExtractionResult,
    TiffExtractor,
    HtmlExtractionResult,
    HtmlDocumentParser,
    DocxComment,
    DocxExtractionResult,
    DocxExtractor,
    ImageExtractionResult,
    ImageExtractor,
    TextExtractionResult,
    TextExtractor,
)
from extractors.document_extractor import (
    ExtractedRecord,
    PageExtractionResult,
    DocumentExtractor,
)

__all__ = [
    "OCRPoint",
    "OCRLine",
    "OCRPageResult",
    "OCREngine",
    "RapidOCREngine",
    "EnhancementProfile",
    "ImageEnhancer",
    "TiffPageResult",
    "TiffExtractionResult",
    "TiffExtractor",
    "HtmlExtractionResult",
    "HtmlDocumentParser",
    "DocxComment",
    "DocxExtractionResult",
    "DocxExtractor",
    "ImageExtractionResult",
    "ImageExtractor",
    "TextExtractionResult",
    "TextExtractor",
    "ExtractedRecord",
    "PageExtractionResult",
    "DocumentExtractor",
]
