"""
OsintNeoAi Indexer: Central Document Extractor & 5-Tier Fallback Engine
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\extractors\\document_extractor.py
Milestone: M2 (Deep Text Extraction & OCR Engine) — Features 5, 6, 7, 8, 9, 10, 11

Orchestrates the 5-Tier Fallback Ladder:
Tier 1: PyMuPDF Native Digital Text Extraction
Tier 2: Character Density & Printable Glyph Heuristic Verification
Tier 3: 300 DPI Pixmap Rasterization + RapidOCR ONNX Neural Recognition
Tier 4: OpenCV CLAHE Contrast Equalization & Deskewing + 2nd-Pass RapidOCR
Tier 5: Dedicated Format Extractors (TIFF, HTML, DOCX, Images, Emails, Plaintext)
"""

from __future__ import annotations

import email
import gc
import io
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, Generator, List, Optional, Sequence, Set, Tuple, Union

import cv2
import numpy as np
import pymupdf

from config import (
    FileCategory,
    IndexerConfig,
    MIN_DIGITAL_TEXT_DENSITY,
    OCR_CONFIDENCE_THRESHOLD,
    OCR_DPI,
    get_file_category,
    get_mime_type,
)
from connectors.local_crawler import IngestedArtifact, make_file_stream_factory, compute_stream_sha256, detect_mime_type
from extractors.format_extractors import (
    DocxExtractor,
    HtmlDocumentParser,
    ImageExtractor,
    TextExtractor,
    TiffExtractor,
)
from extractors.image_enhancer import EnhancementProfile, ImageEnhancer
from extractors.ocr_engine import OCREngine, OCRPageResult
from normalizers.case_normalizer import extract_case_numbers
from normalizers.date_normalizer import normalize_dates_from_text
from normalizers.entity_normalizer import extract_correspondence_parties
from normalizers.financial_normalizer import extract_financial_amounts

logger = logging.getLogger("osintneoai.extractors.document_extractor")


# ==============================================================================
# 1. Interface Contracts (PROJECT.md M2 ↔ M3)
# ==============================================================================

@dataclass
class ExtractedRecord:
    """
    Canonical extracted artifact record passed from M2 to M3.
    """
    record_id: str               # Deterministic artifact-derived ID or UUID
    artifact_sha256: str         # SHA-256 hex string of raw file
    source_path: str             # Source URI or local file path
    source_type: str             # 'local_file', 'gdrive', 'mailbox', 'archive_member'
    mime_type: str               # Canonical MIME type (e.g. application/pdf)
    normalized_date: Optional[str] # ISO 8601 UTC date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
    raw_date_string: Optional[str] # Unparsed raw date text
    extracted_text: str          # Full normalized text body
    ocr_engine_used: str         # Method tag, e.g. 'pymupdf_native', 'rapidocr_onnx', 'rapidocr_enhanced'
    financial_amounts: List[Dict[str, Any]] # [{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}]
    case_numbers: List[str]      # ["8:23-cr-00108-CJC", "30-2021-01201327-CL-UD-CJC"]
    sender: Optional[str]
    recipients: List[str]
    metadata: Dict[str, Any]


@dataclass
class PageExtractionResult:
    """
    Internal page-level extraction telemetry container.
    """
    page_number: int
    text: str
    extraction_tier: str         # 'tier1_digital', 'tier3_ocr', 'tier4_enhanced_ocr'
    confidence: float
    char_count: int
    printable_ratio: float
    elapse_seconds: float


# ==============================================================================
# 2. DocumentExtractor Core Class
# ==============================================================================

class DocumentExtractor:
    """
    Core Extraction Ladder Orchestrator implementing the 5-tier fallback engine.
    """

    def __init__(
        self,
        config: Optional[IndexerConfig] = None,
        ocr_engine: Optional[OCREngine] = None,
        image_enhancer: Optional[ImageEnhancer] = None,
    ) -> None:
        self.config = config or IndexerConfig.default()
        self.ocr_engine = ocr_engine or OCREngine.get_instance(
            min_confidence=self.config.ocr_confidence_threshold
        )
        self.image_enhancer = image_enhancer or ImageEnhancer(
            clahe_clip_limit=self.config.ocr_confidence_threshold
        )
        # Dedicated Format Extractors
        self.tiff_extractor = TiffExtractor(ocr_engine=self.ocr_engine)
        self.html_parser = HtmlDocumentParser()
        self.docx_extractor = DocxExtractor()
        self.image_extractor = ImageExtractor(ocr_engine=self.ocr_engine, image_enhancer=self.image_enhancer)
        self.text_extractor = TextExtractor()

    def extract(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """
        Main entrypoint: ingests IngestedArtifact, executes 5-tier extraction,
        runs multi-tier normalizers, and returns canonical ExtractedRecord.
        """
        category = get_file_category(artifact.mime_type)
        mime = (artifact.mime_type or "").lower()

        # Route to appropriate extraction pathway
        if category == FileCategory.PDF or mime == "application/pdf":
            return self._extract_pdf(artifact)
        elif mime in ("image/tiff", "image/tif") or artifact.source_uri.lower().endswith((".tif", ".tiff")):
            return self._extract_tiff(artifact)
        elif category == FileCategory.IMAGE:
            return self._extract_image(artifact)
        elif category == FileCategory.DOCX:
            return self._extract_docx(artifact)
        elif category == FileCategory.HTML:
            return self._extract_html(artifact)
        elif category == FileCategory.EMAIL:
            return self._extract_email(artifact)
        elif category in (FileCategory.TEXT, FileCategory.TABULAR):
            return self._extract_text(artifact)
        else:
            return self._extract_fallback(artifact)

    def extract_from_path(self, file_path: Union[str, Path]) -> ExtractedRecord:
        """
        Convenience helper to extract directly from a local file path.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "rb") as f:
            sample = f.read(64)
            f.seek(0)
            sha256_hex, total_bytes = compute_stream_sha256(f, chunk_size=self.config.chunk_size)

        mime = detect_mime_type(path, sample_bytes=sample)
        canonical_path = str(path.resolve())

        artifact = IngestedArtifact(
            artifact_id=sha256_hex,
            source_uri=canonical_path,
            mime_type=mime,
            file_size_bytes=total_bytes,
            raw_stream_factory=make_file_stream_factory(canonical_path),
            metadata={"file_name": path.name}
        )
        return self.extract(artifact)

    def _extract_pdf(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """
        Processes PDF via Tiers 1-4 page-by-page generator with strict memory destruction.
        """
        stream = artifact.raw_stream_factory()
        try:
            pdf_bytes = stream.read()
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        except Exception as e:
            logger.error(f"PyMuPDF failed to open PDF {artifact.source_uri}: {e}")
            return self._build_extracted_record(
                artifact=artifact,
                text_body=f"[ERROR: Corrupted or unreadable PDF: {e}]",
                ocr_engine_used="error",
                page_count=0,
                avg_confidence=0.0,
                metadata={"error": str(e)}
            )
        finally:
            stream.close()

        page_results: List[PageExtractionResult] = []
        methods_used: Set[str] = set()
        total_conf = 0.0

        try:
            total_pages = len(doc)
            for page_idx in range(total_pages):
                try:
                    page = doc[page_idx]

                    # --- TIER 1: PyMuPDF Native Text Extraction ---
                    native_text = page.get_text("text").strip()
                    non_space_chars = len([c for c in native_text if c.isprintable() and not c.isspace()])
                    printable_all = len([c for c in native_text if c.isprintable()])
                    total_chars = len(native_text)
                    printable_ratio = (printable_all / total_chars) if total_chars > 0 else 0.0

                    # --- TIER 2: Density & Glyph Quality Heuristic ---
                    if non_space_chars >= self.config.min_digital_text_density and printable_ratio >= 0.85:
                        page_results.append(PageExtractionResult(
                            page_number=page_idx + 1,
                            text=native_text,
                            extraction_tier="tier1_digital",
                            confidence=1.0,
                            char_count=total_chars,
                            printable_ratio=printable_ratio,
                            elapse_seconds=0.001
                        ))
                        methods_used.add("pymupdf_native")
                        total_conf += 1.0
                    else:
                        # --- TIER 3: 300 DPI Rendering + RapidOCR ---
                        pix = page.get_pixmap(dpi=self.config.ocr_dpi)
                        img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
                        if pix.n == 4:
                            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)
                        elif pix.n == 1:
                            img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2RGB)

                        # Explicitly destroy C-level pixmap
                        del pix

                        ocr_res = self.ocr_engine.ocr_image(img_np, page_number=page_idx + 1)
                        page_method = "rapidocr_onnx"

                        # --- TIER 4: OpenCV CLAHE & Preprocessing (if Tier 3 is weak) ---
                        if (not ocr_res.lines or ocr_res.avg_confidence < self.config.ocr_confidence_threshold):
                            enhanced_img = self.image_enhancer.enhance(img_np, profile=EnhancementProfile.HEAVY)
                            enhanced_ocr_res = self.ocr_engine.ocr_image(enhanced_img, page_number=page_idx + 1)

                            if len(enhanced_ocr_res.full_text) > len(ocr_res.full_text) or enhanced_ocr_res.avg_confidence > ocr_res.avg_confidence:
                                ocr_res = enhanced_ocr_res
                                page_method = "rapidocr_enhanced"
                            del enhanced_img

                        methods_used.add(page_method)

                        # Explicitly destroy numpy image array
                        del img_np

                        page_results.append(PageExtractionResult(
                            page_number=page_idx + 1,
                            text=ocr_res.full_text,
                            extraction_tier="tier4_enhanced_ocr" if page_method == "rapidocr_enhanced" else "tier3_ocr",
                            confidence=ocr_res.avg_confidence,
                            char_count=len(ocr_res.full_text),
                            printable_ratio=1.0 if ocr_res.full_text else 0.0,
                            elapse_seconds=ocr_res.total_time_sec
                        ))
                        total_conf += ocr_res.avg_confidence

                    # Garbage collection every 10 pages
                    if (page_idx + 1) % 10 == 0:
                        gc.collect()
                except Exception as page_err:
                    logger.warning(f"Error reading PDF page {page_idx + 1} of artifact: {page_err}")
                    continue
        finally:
            doc.close()
            gc.collect()

        full_text = "\n\n".join([f"--- [Page {p.page_number}] ---\n{p.text}" for p in page_results])
        avg_doc_conf = (total_conf / len(page_results)) if page_results else 0.0
        primary_method = "+".join(sorted(methods_used)) if methods_used else "pymupdf_native"

        return self._build_extracted_record(
            artifact=artifact,
            text_body=full_text,
            ocr_engine_used=primary_method,
            page_count=len(page_results),
            avg_confidence=round(avg_doc_conf, 4),
            metadata={"pages": [p.__dict__ for p in page_results]}
        )

    def _extract_tiff(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Processes multi-page TIFF images."""
        stream = artifact.raw_stream_factory()
        try:
            res = self.tiff_extractor.extract_from_stream(stream, source_uri=artifact.source_uri)
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=res.full_text,
            ocr_engine_used=res.ocr_engine_used,
            page_count=res.page_count,
            avg_confidence=res.average_confidence,
            metadata=res.metadata
        )

    def _extract_image(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Executes OCR on raster images with EXIF orientation correction and enhancement."""
        stream = artifact.raw_stream_factory()
        try:
            res = self.image_extractor.extract_from_stream(stream, source_uri=artifact.source_uri)
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=res.text,
            ocr_engine_used=res.ocr_engine_used,
            page_count=1,
            avg_confidence=res.confidence,
            metadata={**res.metadata, "dimensions": res.dimensions, "format": res.format, "exif": res.exif_data}
        )

    def _extract_docx(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text, tables, and document properties from DOCX files."""
        stream = artifact.raw_stream_factory()
        try:
            res = self.docx_extractor.extract_from_stream(stream, source_uri=artifact.source_uri)
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=res.text,
            ocr_engine_used=res.ocr_engine_used,
            page_count=1,
            avg_confidence=1.0,
            metadata={
                **res.metadata,
                "title": res.title,
                "author": res.author,
                "created": res.created_date,
                "modified": res.modified_date,
                "comments": [c.__dict__ for c in res.comments]
            }
        )

    def _extract_html(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text body and meta tags from HTML documents."""
        stream = artifact.raw_stream_factory()
        try:
            res = self.html_parser.extract_from_stream(stream, source_uri=artifact.source_uri)
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=res.text,
            ocr_engine_used=res.ocr_engine_used,
            page_count=1,
            avg_confidence=1.0,
            metadata={
                **res.metadata,
                "title": res.title,
                "meta_tags": res.meta_tags,
                "links": res.links,
                "email_addresses": res.email_addresses
            }
        )

    def _extract_email(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts email headers, sender/recipient, subject, and message body from EML/MBOX."""
        stream = artifact.raw_stream_factory()
        try:
            msg = email.message_from_binary_file(stream)
        finally:
            stream.close()

        body_parts: List[str] = []
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        body_parts.append(payload.decode(charset, errors="replace"))
                elif ctype == "text/html" and not body_parts:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or "utf-8"
                        html_str = payload.decode(charset, errors="replace")
                        html_res = self.html_parser.extract_from_bytes(payload, source_uri=artifact.source_uri)
                        body_parts.append(html_res.text)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                body_parts.append(payload.decode(charset, errors="replace"))

        text_body = "\n".join(body_parts).strip()
        headers = {
            "From": msg.get("From"),
            "To": msg.get("To"),
            "Subject": msg.get("Subject"),
            "Date": msg.get("Date"),
            "Message-ID": msg.get("Message-ID")
        }

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body,
            ocr_engine_used="email_parser",
            page_count=1,
            avg_confidence=1.0,
            metadata=headers
        )

    def _extract_text(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Extracts text from plain text, markdown, CSV, or JSON artifacts."""
        stream = artifact.raw_stream_factory()
        try:
            res = self.text_extractor.extract_from_stream(stream, source_uri=artifact.source_uri, mime_type=artifact.mime_type)
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=res.text,
            ocr_engine_used=res.ocr_engine_used,
            page_count=1,
            avg_confidence=1.0,
            metadata={**res.metadata, "encoding": res.encoding_used, "format": res.format_detected}
        )

    def _extract_fallback(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """Fallback extractor for unmapped binary formats."""
        stream = artifact.raw_stream_factory()
        try:
            raw_bytes = stream.read(1024 * 1024)
            text_body = "".join([chr(b) if 32 <= b <= 126 or b in (10, 13, 9) else " " for b in raw_bytes])
        finally:
            stream.close()

        return self._build_extracted_record(
            artifact=artifact,
            text_body=text_body.strip(),
            ocr_engine_used="binary_strings",
            page_count=1,
            avg_confidence=0.5,
            metadata={"status": "fallback_binary_dump"}
        )

    def _build_extracted_record(
        self,
        artifact: IngestedArtifact,
        text_body: str,
        ocr_engine_used: str,
        page_count: int,
        avg_confidence: float,
        metadata: Dict[str, Any]
    ) -> ExtractedRecord:
        """
        Executes date, financial, case docket, and correspondence normalization
        to build the canonical ExtractedRecord for Milestone 3.
        """
        # 1. Date normalization
        norm_date, raw_date = normalize_dates_from_text(text_body, {**(artifact.metadata or {}), **metadata})

        # 2. Financial amounts normalization
        financials = extract_financial_amounts(text_body)

        # 3. Legal case identifiers & court citations
        case_nums = extract_case_numbers(text_body)

        # 4. Sender and recipients metadata
        sender, recipients = extract_correspondence_parties(text_body, {**(artifact.metadata or {}), **metadata})

        # Merge metadata
        merged_meta = dict(artifact.metadata or {})
        merged_meta.update(metadata)
        merged_meta["page_count"] = page_count
        merged_meta["avg_confidence"] = avg_confidence

        return ExtractedRecord(
            record_id=f"rec_{artifact.artifact_id[:16]}",
            artifact_sha256=artifact.artifact_id,
            source_path=artifact.source_uri,
            source_type=self._determine_source_type(artifact.source_uri),
            mime_type=artifact.mime_type,
            normalized_date=norm_date,
            raw_date_string=raw_date,
            extracted_text=text_body,
            ocr_engine_used=ocr_engine_used,
            financial_amounts=financials,
            case_numbers=case_nums,
            sender=sender,
            recipients=recipients,
            metadata=merged_meta
        )

    def _determine_source_type(self, source_uri: str) -> str:
        if source_uri.startswith("http://") or source_uri.startswith("https://") or "drive.google.com" in source_uri:
            return "gdrive"
        elif "zip://" in source_uri or "tar://" in source_uri or "gzip://" in source_uri:
            return "archive_member"
        elif source_uri.endswith(".mbox") or source_uri.endswith(".eml"):
            return "mailbox"
        return "local_file"
