# OsintNeoAi Indexer — M2 Technical Analysis & Implementation Blueprint: Format-Specific Extractors

**Agent:** Explorer M2_2 (`C:\OsintNeoAi\.agents\explorer_m2_2\`)  
**Timestamp:** 2026-08-29T17:54:00Z  
**Target Milestone:** Milestone 2 (Deep Text Extraction & OCR Engine)  
**Deliverable File Path:** `C:\OsintNeoAi\workspaces\osintneoai_indexer\extractors\`  
**Target Workspace:** `C:\OsintNeoAi\workspaces\osintneoai_indexer`  

---

## 1. Executive Summary & Problem Boundary

Milestone 2 (M2) of the **OsintNeoAi Indexer** is responsible for transforming raw `IngestedArtifact` stream objects into structured, normalized `ExtractedRecord` entities suitable for entity resolution, timeline reconstruction, and relational vault storage (Milestone 3).

While Explorer M2_1 focuses on the core PDF 5-Tier Fallback Ladder and OpenCV image enhancement, and Explorer M2_3 designs the normalization engines (dates, currency cents, case dockets, phonetic encoding), **Explorer M2_2** establishes the technical blueprints and exact production specifications for all **Format-Specific Document Extractors**:

1. **Multi-Page / Multi-Frame TIFF Extractor (`tiff_extractor.py`)**: Frame-by-frame memory-bounded streaming of complex legal and medical TIFF scans (e.g., 2540x3288 1-bit bilevel hospital charts, faxes, deeds) using `Pillow` and `RapidOCR ONNX` with automatic color-mode conversion and strict per-frame memory reclamation.
2. **Structured HTML Document Parser (`html_parser.py`)**: High-performance HTML parsing via `lxml.html` with graceful fallback to standard library `html.parser`. Performs rigorous script/style/media stripping (resilient to `lxml.html.clean` removal in modern lxml 6.x), converts headings to Markdown `#`, formats HTML `<table>` structures into clean Markdown tables, extracts metadata (`<title>`, `<meta>` tags), and isolates communication links.
3. **DOCX Document Extractor (`docx_extractor.py`)**: Native OOXML parsing via `python-docx` extracting paragraphs with heading style preservation, table data formatted as Markdown, document headers and footers across sections, embedded forensic comments (`word/comments.xml`), and document core properties.
4. **Direct Raster Image Extractor (`image_extractor.py`)**: Direct OCR extraction across single/multi-frame PNG, JPG, JPEG, WEBP, BMP, and GIF assets. Applies EXIF rotation transposition (`PIL.ImageOps.exif_transpose`), color space normalization, two-pass OCR with OpenCV CLAHE/Otsu enhancement fallback, and EXIF metadata extraction.
5. **Plaintext & Structured Data Extractors (`text_extractor.py`)**: Multi-encoding resilient text engine handling `.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.jsonl`, `.xml`, and `.yaml`. Features a multi-tiered encoding detection ladder (`utf-8-sig`, `utf-16`, `windows-1252`, `chardet`), CSV delimiter sniffing with Markdown table rendering, and structured JSON parsing.
6. **Unified Routing & Dispatch Engine (`document_extractor.py`)**: Central orchestration dispatcher that maps incoming MIME types and file categories to specialized extractors, pipes extracted text through the M2 normalizers, and produces canonical `ExtractedRecord` objects adhering 100% to `PROJECT.md § Interface Contracts (M2 ↔ M3)`.

---

## 2. Format-Specific Extraction Taxonomy & MIME Routing Matrix

The extractor subsystem dispatches artifacts based on canonical MIME types defined in `config.py` and `connectors/local_crawler.py`:

| Canonical MIME Type | File Extensions | Category | Extraction Module | Primary Engine / Parser | Output OCR Method Tag |
|---|---|---|---|---|---|
| `application/pdf` | `.pdf` | PDF | `pdf_extractor.py` | PyMuPDF + RapidOCR | `pymupdf_native` / `rapidocr_onnx` |
| `image/tiff` | `.tif`, `.tiff` | Image | `tiff_extractor.py` | Pillow (`ImageSequence`) + RapidOCR | `rapidocr_onnx_tiff` |
| `image/png`, `image/jpeg`, `image/webp`, `image/bmp`, `image/gif` | `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.gif` | Image | `image_extractor.py` | Pillow + OpenCV + RapidOCR | `rapidocr_onnx` / `rapidocr_onnx_enhanced` |
| `text/html`, `application/xhtml+xml` | `.html`, `.htm`, `.xhtml` | HTML | `html_parser.py` | `lxml.html` + `html.parser` | `lxml_html_parser` / `stdlib_html_parser` |
| `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/msword`, `application/rtf` | `.docx`, `.doc`, `.rtf`, `.odt` | DOCX | `docx_extractor.py` | `python-docx` + OOXML zip reader | `docx_native_parser` |
| `application/mbox`, `message/rfc822`, `application/vnd.ms-outlook` | `.mbox`, `.eml`, `.msg` | Email | `connectors/mailbox_reader.py` | `mailbox.mbox` + `email.message` | `email_rfc822_parser` |
| `text/csv`, `text/tab-separated-values`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `.csv`, `.tsv`, `.xlsx` | Tabular | `text_extractor.py` | `csv.Sniffer` + `openpyxl` | `csv_parser` / `xlsx_parser` |
| `text/plain`, `text/markdown`, `application/json`, `application/xml`, `application/x-yaml` | `.txt`, `.md`, `.json`, `.xml`, `.yaml`, `.log`, `.ini` | Text | `text_extractor.py` | Encoding ladder + standard parsers | `plaintext_reader` / `json_parser` / `markdown_reader` |

---

## 3. Module 1: Multi-Page / Multi-Frame TIFF Extractor (`tiff_extractor.py`)

### 3.1 Design Invariants & Evidentiary Reality
Evidentiary files in the local environment (such as `C:\Users\Amd949609\Downloads\General Consent for Treatment.TIF` and `CONSENT SURGERY OR SPECIAL PROCEDURES.TIF`) are multi-page documents scanned at high resolutions (2540x3288 pixels) in 1-bit bilevel format (`mode: '1'`).

Key Technical Requirements:
1. **Pillow `ImageSequence` Iteration**: Iterate frames lazily without loading the entire multi-frame TIFF into uncompressed memory simultaneously.
2. **Color Mode Normalization**:
   - `1` (1-bit bilevel) -> Convert to 8-bit RGB (`frame.convert('RGB')`) for ONNX model ingestion.
   - `L` (8-bit grayscale) -> Convert to 3-channel RGB.
   - `P` (Paletted) -> Convert to RGB using palette lookup.
   - `RGBA` / `CMYK` / `I;16` -> Convert to standard 3-channel RGB uint8 arrays.
3. **Memory Bounding ($O(1)$ RAM)**:
   - Explicitly delete numpy arrays and PIL frames after OCR processing: `del frame_rgb; del np_arr; gc.collect()`.
4. **Multi-Page Layout Output**:
   - Each page is demarcated in the body text with form feed `\f` and clear visual markers: `\n\n--- [TIFF Page {N}/{Total}] ---\n\n`.
   - Per-page metrics (dimensions, mode, OCR line count, average confidence) stored in `metadata["pages"]`.

### 3.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — Multi-Page / Multi-Frame TIFF Extractor
Module: workspaces.osintneoai_indexer.extractors.tiff_extractor
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import gc
import io
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageSequence

from config import OCR_CONFIDENCE_THRESHOLD, IndexerConfig
from extractors.ocr_engine import RapidOCREngine

logger = logging.getLogger("osintneoai.extractors.tiff")


@dataclass
class TiffPageResult:
    """Individual page extraction telemetry for TIFF documents."""
    page_number: int
    text: str
    confidence: float
    dimensions: Tuple[int, int]
    original_mode: str
    line_count: int


@dataclass
class TiffExtractionResult:
    """Aggregated multi-page TIFF extraction result."""
    full_text: str
    page_count: int
    average_confidence: float
    pages: List[TiffPageResult]
    metadata: Dict[str, Any]
    ocr_engine_used: str = "rapidocr_onnx_tiff"


class TiffExtractor:
    """
    High-performance, memory-bounded multi-page TIFF extractor.
    Streams frames from binary streams or file paths, normalizes color spaces,
    and executes RapidOCR ONNX inference per frame.
    """

    def __init__(
        self,
        ocr_engine: Optional[RapidOCREngine] = None,
        confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD,
    ) -> None:
        self.ocr_engine = ocr_engine or RapidOCREngine.get_instance()
        self.confidence_threshold = confidence_threshold

    def extract_from_stream(
        self,
        stream: BinaryIO,
        source_uri: str = "stream://tiff",
    ) -> TiffExtractionResult:
        """
        Extracts structured text and OCR transcripts from a binary stream.
        """
        try:
            # Pillow requires seekable stream
            if not stream.seekable():
                stream_bytes = stream.read()
                img = Image.open(io.BytesIO(stream_bytes))
            else:
                stream.seek(0)
                img = Image.open(stream)
        except Exception as e:
            logger.error(f"Failed to open TIFF stream from {source_uri}: {e}")
            return TiffExtractionResult(
                full_text=f"[ERROR: Corrupt or unreadable TIFF archive: {e}]",
                page_count=0,
                average_confidence=0.0,
                pages=[],
                metadata={"error": str(e), "source_uri": source_uri},
            )

        return self._process_image(img, source_uri)

    def extract_from_path(self, file_path: Union[str, Path]) -> TiffExtractionResult:
        """
        Extracts structured text from a local TIFF file.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"TIFF file not found: {path}")

        try:
            with Image.open(path) as img:
                return self._process_image(img, str(path))
        except Exception as e:
            logger.error(f"Error processing TIFF file {path}: {e}")
            return TiffExtractionResult(
                full_text=f"[ERROR: Unreadable TIFF file {path.name}: {e}]",
                page_count=0,
                average_confidence=0.0,
                pages=[],
                metadata={"error": str(e), "file_path": str(path)},
            )

    def _process_image(self, img: Image.Image, source_uri: str) -> TiffExtractionResult:
        """Internal frame-by-frame OCR processing loop."""
        total_frames = getattr(img, "n_frames", 1)
        pages_results: List[TiffPageResult] = []
        page_texts: List[str] = []
        total_conf_sum = 0.0
        valid_conf_pages = 0

        for frame_idx, frame in enumerate(ImageSequence.Iterator(img)):
            page_num = frame_idx + 1
            orig_mode = frame.mode
            orig_size = frame.size

            try:
                # Convert all modes (1, L, P, RGBA, CMYK, I;16) to standard 8-bit RGB
                frame_rgb = frame.convert("RGB")
                np_arr = np.array(frame_rgb, dtype=np.uint8)

                # Execute OCR
                ocr_lines, page_conf = self.ocr_engine.extract_text_and_confidence(np_arr)
                page_text = "\n".join(ocr_lines).strip()

                if page_conf > 0.0:
                    total_conf_sum += page_conf
                    valid_conf_pages += 1

                pages_results.append(
                    TiffPageResult(
                        page_number=page_num,
                        text=page_text,
                        confidence=page_conf,
                        dimensions=orig_size,
                        original_mode=orig_mode,
                        line_count=len(ocr_lines),
                    )
                )

                if page_text:
                    page_texts.append(f"--- [TIFF Page {page_num}/{total_frames}] ---\n{page_text}")
                else:
                    page_texts.append(f"--- [TIFF Page {page_num}/{total_frames}] ---\n[Blank or unreadable page]")

            except Exception as frame_err:
                logger.warning(f"Error processing frame {page_num} of {source_uri}: {frame_err}")
                pages_results.append(
                    TiffPageResult(
                        page_number=page_num,
                        text="",
                        confidence=0.0,
                        dimensions=orig_size,
                        original_mode=orig_mode,
                        line_count=0,
                    )
                )
            finally:
                # Explicit memory reclamation for high-res images
                del frame_rgb
                del np_arr
                if page_num % 5 == 0:
                    gc.collect()

        avg_confidence = (total_conf_sum / valid_conf_pages) if valid_conf_pages > 0 else 0.0
        full_text_body = "\n\n\f\n\n".join(page_texts)

        return TiffExtractionResult(
            full_text=full_text_body,
            page_count=total_frames,
            average_confidence=round(avg_confidence, 4),
            pages=pages_results,
            metadata={
                "source_uri": source_uri,
                "total_pages": total_frames,
                "average_confidence": round(avg_confidence, 4),
            },
        )
```

---

## 4. Module 2: HTML Document Parser (`html_parser.py`)

### 4.1 Design Invariants & Python 3.14 / lxml 6.x Compatibility
Investigation revealed that `lxml.html.clean` is no longer bundled in `lxml >= 5.2.0`. Attempting to import `Cleaner` raises `ImportError: lxml.html.clean module is now a separate project`.

Therefore, the HTML parser implements a custom, high-speed, zero-external-dependency DOM sanitizer using `lxml.etree.strip_elements` and recursive AST traversal.

Key Requirements:
1. **Boilerplate & Tag Stripping**:
   - Strip `<script>`, `<style>`, `<noscript>`, `<iframe>`, `<svg>`, `<canvas>`, `<template>`, `<nav>`, `<header>`, `<footer>`.
2. **Structured Markdown Generation**:
   - Headings `<h1>` – `<h6>` mapped to `#` through `######`.
   - Tables (`<table>`, `<tr>`, `<th>`, `<td>`) rendered as Markdown grid tables with aligned column pipes and hyphen separators.
   - Lists (`<ul>`, `<ol>`, `<li>`) rendered as `- ` bullet lists.
   - Paragraphs (`<p>`), line breaks (`<br>`), and blockquotes formatted with paragraph spacing.
3. **Metadata & Entity Discovery**:
   - Extract `<title>`, `<meta name="...">`, `<meta property="...">`, `<meta http-equiv="...">`.
   - Extract `<a href="...">` links and mailto addresses into structured metadata.
4. **Encoding Auto-Recovery**:
   - Inspect meta charset tags -> try UTF-8 -> fallback to `chardet.detect()` -> fallback to Latin-1 with replacement.
5. **Standard Library Fallback**:
   - If `lxml` encounters malformed XML/HTML fragments that fail to parse, fallback gracefully to `html.parser.HTMLParser`.

### 4.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — Structured HTML Document Parser
Module: workspaces.osintneoai_indexer.extractors.html_parser
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import chardet
import lxml.etree
import lxml.html

logger = logging.getLogger("osintneoai.extractors.html")


@dataclass
class HtmlExtractionResult:
    """Structured extraction output for HTML documents."""
    text: str
    title: Optional[str]
    meta_tags: Dict[str, str]
    links: List[Dict[str, str]]
    email_addresses: List[str]
    metadata: Dict[str, Any]
    ocr_engine_used: str = "lxml_html_parser"


class StdlibHtmlFallbackParser(HTMLParser):
    """Robust standard library fallback parser for malformed HTML."""

    def __init__(self) -> None:
        super().__init__()
        self.text_parts: List[str] = []
        self.title: Optional[str] = None
        self._in_title: bool = False
        self._skip_tags = {"script", "style", "noscript", "svg", "iframe", "canvas"}
        self._current_skip: int = 0

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        t = tag.lower()
        if t in self._skip_tags:
            self._current_skip += 1
        elif t == "title":
            self._in_title = True
        elif t in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.text_parts.append(f"\n\n{'#' * int(t[1])} ")
        elif t == "p":
            self.text_parts.append("\n\n")
        elif t == "br":
            self.text_parts.append("\n")
        elif t == "li":
            self.text_parts.append("\n- ")

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in self._skip_tags and self._current_skip > 0:
            self._current_skip -= 1
        elif t == "title":
            self._in_title = False
        elif t in ("p", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._current_skip > 0:
            return
        if self._in_title:
            self.title = (self.title or "") + data
        cleaned = " ".join(data.split())
        if cleaned:
            self.text_parts.append(cleaned + " ")

    def get_text(self) -> str:
        return re.sub(r"\n{3,}", "\n\n", "".join(self.text_parts)).strip()


class HtmlDocumentParser:
    """
    High-performance HTML document parser converting evidentiary web records
    into clean, structured Markdown text while preserving tables and metadata.
    """

    STRIP_TAGS = (
        "script", "style", "noscript", "iframe", "svg",
        "canvas", "template", "nav", "footer", "header"
    )

    def extract_from_stream(
        self,
        stream: BinaryIO,
        source_uri: str = "stream://html",
    ) -> HtmlExtractionResult:
        """Parses HTML document from raw binary stream."""
        raw_bytes = stream.read()
        return self.extract_from_bytes(raw_bytes, source_uri)

    def extract_from_path(self, file_path: Union[str, Path]) -> HtmlExtractionResult:
        """Parses HTML document from local file path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"HTML file not found: {path}")
        raw_bytes = path.read_bytes()
        return self.extract_from_bytes(raw_bytes, str(path))

    def extract_from_bytes(
        self,
        raw_bytes: bytes,
        source_uri: str = "memory://html",
    ) -> HtmlExtractionResult:
        """Core decoding and parsing routine."""
        if not raw_bytes.strip():
            return HtmlExtractionResult(
                text="",
                title=None,
                meta_tags={},
                links=[],
                email_addresses=[],
                metadata={"source_uri": source_uri, "empty_payload": True},
            )

        html_text = self._decode_bytes(raw_bytes)
        try:
            return self._parse_lxml(html_text, source_uri)
        except Exception as lxml_err:
            logger.warning(f"lxml parsing failed for {source_uri}: {lxml_err}. Falling back to stdlib HTMLParser.")
            return self._parse_stdlib(html_text, source_uri)

    def _decode_bytes(self, raw_bytes: bytes) -> str:
        """Multi-tiered encoding resolution."""
        # 1. Check UTF-8 with BOM or plain UTF-8
        try:
            return raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            pass

        # 2. Check meta charset tag in first 2048 bytes
        header_sample = raw_bytes[:2048].decode("ascii", errors="ignore")
        match = re.search(r'charset=["\']?([a-zA-Z0-9_-]+)', header_sample, re.IGNORECASE)
        if match:
            charset = match.group(1).lower()
            try:
                return raw_bytes.decode(charset)
            except (UnicodeDecodeError, LookupError):
                pass

        # 3. Chardet heuristic
        detected = chardet.detect(raw_bytes[:65536])
        if detected and detected.get("encoding"):
            try:
                return raw_bytes.decode(detected["encoding"])
            except (UnicodeDecodeError, LookupError):
                pass

        # 4. Fallback to windows-1252 / latin-1 with replacement
        return raw_bytes.decode("latin-1", errors="replace")

    def _parse_lxml(self, html_text: str, source_uri: str) -> HtmlExtractionResult:
        """Structured DOM parsing using lxml."""
        root = lxml.html.fromstring(html_text)

        # 1. Sanitize elements
        lxml.etree.strip_elements(root, *self.STRIP_TAGS)

        # 2. Extract Document Title
        title = root.findtext(".//title")
        if title:
            title = " ".join(title.split()).strip()

        # 3. Extract Meta Tags
        meta_tags: Dict[str, str] = {}
        for meta in root.xpath(".//meta"):
            name = meta.get("name") or meta.get("property") or meta.get("http-equiv")
            content = meta.get("content")
            if name and content:
                meta_tags[name.lower().strip()] = " ".join(content.split()).strip()

        # 4. Extract Links & Mailto Addresses
        links: List[Dict[str, str]] = []
        emails: List[str] = []
        for a_tag in root.xpath(".//a"):
            href = a_tag.get("href")
            link_text = " ".join(a_tag.text_content().split()).strip()
            if href:
                href_clean = href.strip()
                if href_clean.lower().startswith("mailto:"):
                    email_addr = href_clean[7:].split("?")[0].strip()
                    if email_addr and email_addr not in emails:
                        emails.append(email_addr)
                else:
                    links.append({"text": link_text, "url": href_clean})

        # 5. Extract Structured Markdown Text Body
        blocks: List[str] = []
        if title:
            blocks.append(f"# {title}")

        body_elem = root.body if root.body is not None else root
        for elem in body_elem.iterchildren():
            tag = elem.tag.lower() if isinstance(elem.tag, str) else ""

            if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(tag[1])
                heading_text = " ".join(elem.text_content().split()).strip()
                if heading_text:
                    blocks.append(f"{'#' * level} {heading_text}")

            elif tag == "p":
                p_text = " ".join(elem.text_content().split()).strip()
                if p_text:
                    blocks.append(p_text)

            elif tag == "table":
                md_table = self._format_table(elem)
                if md_table:
                    blocks.append(md_table)

            elif tag in ("ul", "ol"):
                list_items = []
                for li in elem.xpath(".//li"):
                    li_text = " ".join(li.text_content().split()).strip()
                    if li_text:
                        list_items.append(f"- {li_text}")
                if list_items:
                    blocks.append("\n".join(list_items))

            elif tag in ("blockquote", "section", "article", "div"):
                div_text = " ".join(elem.text_content().split()).strip()
                if div_text:
                    blocks.append(div_text)

        if not blocks:
            # Fallback to full cleaned text_content if no block tags
            raw_content = " ".join(root.text_content().split()).strip()
            blocks.append(raw_content)

        markdown_body = "\n\n".join(blocks).strip()

        return HtmlExtractionResult(
            text=markdown_body,
            title=title,
            meta_tags=meta_tags,
            links=links[:50],  # Bound metadata size
            email_addresses=emails,
            metadata={
                "source_uri": source_uri,
                "title": title,
                "meta_tags": meta_tags,
                "link_count": len(links),
                "email_count": len(emails),
            },
            ocr_engine_used="lxml_html_parser",
        )

    def _format_table(self, table_elem: lxml.html.HtmlElement) -> Optional[str]:
        """Converts an HTML table element to Markdown table text."""
        rows_data: List[List[str]] = []
        for tr in table_elem.xpath(".//tr"):
            cells = [" ".join(c.text_content().split()).strip() for c in tr.xpath(".//th | .//td")]
            if any(cells):
                rows_data.append(cells)

        if not rows_data:
            return None

        col_count = max(len(r) for r in rows_data)
        if col_count == 0:
            return None

        padded_rows = [r + [""] * (col_count - len(r)) for r in rows_data]
        header = "| " + " | ".join(padded_rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * col_count) + " |"
        body = ["| " + " | ".join(r) + " |" for r in padded_rows[1:]]

        return "\n".join([header, separator] + body)

    def _parse_stdlib(self, html_text: str, source_uri: str) -> HtmlExtractionResult:
        """Fallback parsing when lxml fails."""
        parser = StdlibHtmlFallbackParser()
        parser.feed(html_text)
        text = parser.get_text()
        return HtmlExtractionResult(
            text=text,
            title=parser.title,
            meta_tags={},
            links=[],
            email_addresses=[],
            metadata={"source_uri": source_uri, "fallback": True},
            ocr_engine_used="stdlib_html_parser",
        )
```

---

## 5. Module 3: DOCX Document Extractor (`docx_extractor.py`)

### 5.1 Design Invariants & Evidentiary Reality
Evidentiary files include Google Docs exported as `.docx` (e.g. `DR_ANN_VERMA_RESCISSION_NOTICE.docx` and `gdoc_1aiK_*.docx`), legal draft motions, and agreements.

Key Requirements:
1. **Paragraphs & Heading Hierarchy**:
   - Map `Heading 1` -> `# `, `Heading 2` -> `## `, `List Bullet` -> `- `.
2. **Tables**:
   - Legal pleadings and settlement agreements use tables for fee splits, damage valuations, and docket schedules. Formatted as clean Markdown tables.
3. **Headers & Footers**:
   - Legal documents place docket numbers (e.g. `Case 8:23-cr-00108-CJC`), page numbers, and confidentiality markers in headers/footers. Extracted across all sections.
4. **Forensic Comments (`word/comments.xml`)**:
   - Word comments contain author names, dates, and editorial redlines. Parsed by inspecting the underlying docx zip archive.
5. **Core Document Properties**:
   - `core_properties.title`, `author`, `created`, `modified`, `last_modified_by`, `subject`, `category`.

### 5.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — DOCX Document Extractor
Module: workspaces.osintneoai_indexer.extractors.docx_extractor
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import io
import logging
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import docx
from docx.table import Table

logger = logging.getLogger("osintneoai.extractors.docx")


@dataclass
class DocxComment:
    """Forensic annotation/comment extracted from DOCX internal XML."""
    author: str
    date: Optional[str]
    text: str


@dataclass
class DocxExtractionResult:
    """Structured extraction output for Microsoft Word documents."""
    text: str
    title: Optional[str]
    author: Optional[str]
    created_date: Optional[str]
    modified_date: Optional[str]
    comments: List[DocxComment]
    metadata: Dict[str, Any]
    ocr_engine_used: str = "docx_native_parser"


class DocxExtractor:
    """
    Forensic DOCX extractor extracting headings, paragraphs, tables,
    headers, footers, comments, and core metadata.
    """

    def extract_from_stream(
        self,
        stream: BinaryIO,
        source_uri: str = "stream://docx",
    ) -> DocxExtractionResult:
        """Parses DOCX document from raw binary stream."""
        raw_bytes = stream.read()
        return self.extract_from_bytes(raw_bytes, source_uri)

    def extract_from_path(self, file_path: Union[str, Path]) -> DocxExtractionResult:
        """Parses DOCX document from local file path."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"DOCX file not found: {path}")
        raw_bytes = path.read_bytes()
        return self.extract_from_bytes(raw_bytes, str(path))

    def extract_from_bytes(
        self,
        raw_bytes: bytes,
        source_uri: str = "memory://docx",
    ) -> DocxExtractionResult:
        """Core parsing implementation using python-docx and zip inspection."""
        if not raw_bytes.strip():
            return DocxExtractionResult(
                text="",
                title=None,
                author=None,
                created_date=None,
                modified_date=None,
                comments=[],
                metadata={"source_uri": source_uri, "empty_payload": True},
            )

        bio = io.BytesIO(raw_bytes)
        try:
            doc = docx.Document(bio)
        except Exception as doc_err:
            logger.error(f"Failed to parse DOCX document from {source_uri}: {doc_err}")
            return DocxExtractionResult(
                text=f"[ERROR: Corrupt or encrypted DOCX document: {doc_err}]",
                title=None,
                author=None,
                created_date=None,
                modified_date=None,
                comments=[],
                metadata={"error": str(doc_err), "source_uri": source_uri},
            )

        # 1. Extract Core Properties
        props = doc.core_properties
        title = props.title.strip() if props.title else None
        author = props.author.strip() if props.author else None
        created = props.created.isoformat() if props.created else None
        modified = props.modified.isoformat() if props.modified else None

        # 2. Extract Forensic Comments from zip container
        comments = self._extract_comments(raw_bytes)

        # 3. Extract Section Headers & Footers
        header_footer_texts = self._extract_headers_footers(doc)

        # 4. Extract Paragraphs & Headings
        blocks: List[str] = []
        if title:
            blocks.append(f"# {title}")

        if header_footer_texts:
            blocks.append(f"<!-- Headers/Footers: {', '.join(header_footer_texts)} -->")

        for p in doc.paragraphs:
            p_text = p.text.strip()
            if not p_text:
                continue

            style_name = p.style.name if p.style else ""
            if style_name.startswith("Heading"):
                try:
                    level = int(style_name.split()[-1])
                except Exception:
                    level = 1
                blocks.append(f"{'#' * level} {p_text}")
            elif "List" in style_name:
                blocks.append(f"- {p_text}")
            else:
                blocks.append(p_text)

        # 5. Extract Tables
        for table in doc.tables:
            md_table = self._format_table(table)
            if md_table:
                blocks.append(md_table)

        # 6. Append Comments Section if present
        if comments:
            comment_blocks = ["\n### Forensic Document Annotations / Comments"]
            for c in comments:
                date_str = f" ({c.date})" if c.date else ""
                comment_blocks.append(f"- **{c.author}**{date_str}: {c.text}")
            blocks.append("\n".join(comment_blocks))

        full_text = "\n\n".join(blocks).strip()

        return DocxExtractionResult(
            text=full_text,
            title=title,
            author=author,
            created_date=created,
            modified_date=modified,
            comments=comments,
            metadata={
                "source_uri": source_uri,
                "title": title,
                "author": author,
                "created": created,
                "modified": modified,
                "paragraph_count": len(doc.paragraphs),
                "table_count": len(doc.tables),
                "comment_count": len(comments),
            },
        )

    def _extract_headers_footers(self, doc: docx.Document) -> List[str]:
        """Extracts unique text strings from document section headers and footers."""
        hf_texts: List[str] = []
        seen = set()

        for section in doc.sections:
            # Header
            for p in section.header.paragraphs:
                t = p.text.strip()
                if t and t not in seen:
                    seen.add(t)
                    hf_texts.append(t)
            # Footer
            for p in section.footer.paragraphs:
                t = p.text.strip()
                if t and t not in seen:
                    seen.add(t)
                    hf_texts.append(t)

        return hf_texts

    def _format_table(self, table: Table) -> Optional[str]:
        """Formats a docx Table into a Markdown grid table."""
        rows_data: List[List[str]] = []
        for row in table.rows:
            cells = [" ".join(cell.text.strip().split()).replace("|", "\\|") for cell in row.cells]
            if any(cells):
                rows_data.append(cells)

        if not rows_data:
            return None

        col_count = max(len(r) for r in rows_data)
        if col_count == 0:
            return None

        padded_rows = [r + [""] * (col_count - len(r)) for r in rows_data]
        header = "| " + " | ".join(padded_rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * col_count) + " |"
        body = ["| " + " | ".join(r) + " |" for r in padded_rows[1:]]

        return "\n".join([header, separator] + body)

    def _extract_comments(self, raw_bytes: bytes) -> List[DocxComment]:
        """Inspects docx zip package for word/comments.xml."""
        comments: List[DocxComment] = []
        try:
            with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
                if "word/comments.xml" in z.namelist():
                    xml_content = z.read("word/comments.xml")
                    root = ET.fromstring(xml_content)
                    # Namespace for Word OpenXML
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    for comment_node in root.findall(".//w:comment", ns):
                        author = comment_node.get(f"{{{ns['w']}}}author", "Unknown Author")
                        date = comment_node.get(f"{{{ns['w']}}}date")
                        text_nodes = comment_node.findall(".//w:t", ns)
                        text = " ".join([t.text for t in text_nodes if t.text])
                        if text.strip():
                            comments.append(DocxComment(author=author, date=date, text=text.strip()))
        except Exception as e:
            logger.debug(f"No comments extracted: {e}")

        return comments
```

---

## 6. Module 4: Direct Raster Image OCR Extractor (`image_extractor.py`)

### 6.1 Design Invariants & Evidentiary Reality
Evidentiary files contain 936+ high-resolution JPEG photos, phone camera photos (`IMG_0427.JPG`), whistleblower dossiers (`Whistleblower_Audit_and_Forensic_Dossier.png`), receipts, and mind maps.

Key Requirements:
1. **EXIF Orientation Normalization**:
   - Phone cameras record orientation tags (EXIF 274). Uncorrected images are rotated 90°/180°/270°, destroying OCR character segmentation.
   - Must execute `PIL.ImageOps.exif_transpose(img)` before numpy array conversion!
2. **Two-Pass OCR Strategy**:
   - *Pass 1*: Direct RapidOCR ONNX inference on RGB array.
   - *Quality Check*: If confidence < 0.65 or lines == 0, trigger Pass 2.
   - *Pass 2*: OpenCV CLAHE contrast enhancement, adaptive Otsu/Gaussian binarization, and deskewing via `ImageEnhancer`.
3. **EXIF Metadata Capture**:
   - Capture `DateTimeOriginal`, `GPSInfo`, `Make`, `Model`, `Software` into `metadata`.

### 6.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — Raster Image OCR Extractor
Module: workspaces.osintneoai_indexer.extractors.image_extractor
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import ExifTags, Image, ImageOps

from config import OCR_CONFIDENCE_THRESHOLD
from extractors.image_enhancer import ImageEnhancer
from extractors.ocr_engine import RapidOCREngine

logger = logging.getLogger("osintneoai.extractors.image")


@dataclass
class ImageExtractionResult:
    """Structured extraction output for raster image files."""
    text: str
    confidence: float
    dimensions: Tuple[int, int]
    exif_metadata: Dict[str, Any]
    enhancement_applied: bool
    ocr_engine_used: str = "rapidocr_onnx"


class ImageExtractor:
    """
    Direct neural OCR extractor for raster images (PNG, JPG, WEBP, BMP, GIF).
    Handles EXIF rotation correction, two-pass OCR, and OpenCV enhancement.
    """

    def __init__(
        self,
        ocr_engine: Optional[RapidOCREngine] = None,
        enhancer: Optional[ImageEnhancer] = None,
        confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD,
    ) -> None:
        self.ocr_engine = ocr_engine or RapidOCREngine.get_instance()
        self.enhancer = enhancer or ImageEnhancer()
        self.confidence_threshold = confidence_threshold

    def extract_from_stream(
        self,
        stream: BinaryIO,
        source_uri: str = "stream://image",
    ) -> ImageExtractionResult:
        """Extracts OCR text and EXIF from binary stream."""
        raw_bytes = stream.read()
        return self.extract_from_bytes(raw_bytes, source_uri)

    def extract_from_path(self, file_path: Union[str, Path]) -> ImageExtractionResult:
        """Extracts OCR text and EXIF from local image file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        raw_bytes = path.read_bytes()
        return self.extract_from_bytes(raw_bytes, str(path))

    def extract_from_bytes(
        self,
        raw_bytes: bytes,
        source_uri: str = "memory://image",
    ) -> ImageExtractionResult:
        """Core image loading, orientation fixing, and OCR pipeline."""
        if not raw_bytes.strip():
            return ImageExtractionResult(
                text="",
                confidence=0.0,
                dimensions=(0, 0),
                exif_metadata={},
                enhancement_applied=False,
            )

        try:
            pil_img = Image.open(io.BytesIO(raw_bytes))
        except Exception as e:
            logger.error(f"Failed to decode image from {source_uri}: {e}")
            return ImageExtractionResult(
                text=f"[ERROR: Corrupt or unreadable image: {e}]",
                confidence=0.0,
                dimensions=(0, 0),
                exif_metadata={"error": str(e)},
                enhancement_applied=False,
            )

        # 1. Extract EXIF metadata before transposition
        exif_meta = self._extract_exif(pil_img)

        # 2. Critical: Normalize EXIF Orientation
        try:
            transposed_img = ImageOps.exif_transpose(pil_img)
            if transposed_img is not None:
                pil_img = transposed_img
        except Exception as orient_err:
            logger.debug(f"Orientation transpose skipped: {orient_err}")

        # 3. Convert to 8-bit 3-channel RGB array
        rgb_img = pil_img.convert("RGB")
        dimensions = rgb_img.size
        np_arr = np.array(rgb_img, dtype=np.uint8)

        # 4. Pass 1: Direct Neural OCR
        lines, confidence = self.ocr_engine.extract_text_and_confidence(np_arr)
        enhancement_applied = False
        engine_tag = "rapidocr_onnx"

        # 5. Pass 2: Fallback Enhancement if confidence is below threshold
        if (confidence < self.confidence_threshold or len(lines) == 0) and self.enhancer is not None:
            logger.debug(f"Low confidence ({confidence:.2f}) on {source_uri}. Triggering OpenCV enhancement pass.")
            enhanced_np = self.enhancer.enhance_for_ocr(np_arr)
            enh_lines, enh_conf = self.ocr_engine.extract_text_and_confidence(enhanced_np)
            if enh_conf > confidence or len(enh_lines) > len(lines):
                lines = enh_lines
                confidence = enh_conf
                enhancement_applied = True
                engine_tag = "rapidocr_onnx_enhanced"

        extracted_text = "\n".join(lines).strip()

        return ImageExtractionResult(
            text=extracted_text,
            confidence=round(confidence, 4),
            dimensions=dimensions,
            exif_metadata=exif_meta,
            enhancement_applied=enhancement_applied,
            ocr_engine_used=engine_tag,
        )

    def _extract_exif(self, img: Image.Image) -> Dict[str, Any]:
        """Extracts standard EXIF tags and GPS data."""
        exif_data: Dict[str, Any] = {}
        try:
            raw_exif = img.getexif()
            if not raw_exif:
                return exif_data

            for tag_id, value in raw_exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                # Skip large binary thumbnails
                if isinstance(value, (bytes, bytearray)) and len(value) > 256:
                    continue
                if isinstance(value, (str, int, float)):
                    exif_data[tag_name] = value
                elif hasattr(value, "isoformat"):
                    exif_data[tag_name] = value.isoformat()
        except Exception as e:
            logger.debug(f"EXIF parsing error: {e}")

        return exif_data
```

---

## 7. Module 5: Plaintext & Structured Data Extractors (`text_extractor.py`)

### 7.1 Design Invariants & Evidentiary Reality
Evidentiary files include raw logs, transcripts (`01_USA_v_Harry_Sidhu_*.md`, `.jpg.txt`), company searches (`CompanySearch_mercyhouse_*.csv`), network scans, and manifest JSONs (`GDRIVE_INGESTION_MANIFEST.json`).

Key Requirements:
1. **Multi-Encoding Auto-Detection**:
   - Decode sequence: `utf-8-sig` -> `utf-16` -> `windows-1252` -> `chardet.detect()` -> `latin-1` with replacement.
2. **CSV / TSV Formatting**:
   - Use `csv.Sniffer` to identify dialect and delimiter (comma, tab, pipe, semicolon).
   - Render rows as clean Markdown tables for entity recognition and dollar amount parsing.
3. **JSON / JSONL Handling**:
   - Parse JSON structures and format as readable YAML/indented text so downstream regexes (case IDs, dates, financials) match seamlessly.
4. **Markdown Frontmatter Extraction**:
   - Extract YAML frontmatter metadata if present.

### 7.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — Plaintext & Structured Data Extractor
Module: workspaces.osintneoai_indexer.extractors.text_extractor
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import csv
import io
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Union

import chardet

logger = logging.getLogger("osintneoai.extractors.text")


@dataclass
class TextExtractionResult:
    """Structured extraction output for plaintext and structured data."""
    text: str
    format_type: str  # 'plaintext', 'markdown', 'csv', 'json', 'xml'
    metadata: Dict[str, Any]
    ocr_engine_used: str = "plaintext_reader"


class TextExtractor:
    """
    Universal plaintext and structured data extractor with multi-encoding recovery,
    CSV delimiter sniffing, and JSON structure formatting.
    """

    def extract_from_stream(
        self,
        stream: BinaryIO,
        mime_type: str = "text/plain",
        source_uri: str = "stream://text",
    ) -> TextExtractionResult:
        """Extracts text from binary stream."""
        raw_bytes = stream.read()
        return self.extract_from_bytes(raw_bytes, mime_type, source_uri)

    def extract_from_path(
        self,
        file_path: Union[str, Path],
        mime_type: Optional[str] = None,
    ) -> TextExtractionResult:
        """Extracts text from local file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Text file not found: {path}")
        raw_bytes = path.read_bytes()
        ext = path.suffix.lower()
        if not mime_type:
            if ext in (".csv", ".tsv"):
                mime_type = "text/csv"
            elif ext in (".json", ".jsonl", ".ndjson"):
                mime_type = "application/json"
            elif ext in (".md", ".markdown"):
                mime_type = "text/markdown"
            elif ext in (".xml", ".xaml"):
                mime_type = "application/xml"
            else:
                mime_type = "text/plain"

        return self.extract_from_bytes(raw_bytes, mime_type, str(path))

    def extract_from_bytes(
        self,
        raw_bytes: bytes,
        mime_type: str = "text/plain",
        source_uri: str = "memory://text",
    ) -> TextExtractionResult:
        """Core decoding and format-specific processing."""
        if not raw_bytes.strip():
            return TextExtractionResult(
                text="",
                format_type="empty",
                metadata={"source_uri": source_uri, "empty_payload": True},
            )

        decoded_text, encoding_used = self._decode_bytes(raw_bytes)
        mime_clean = mime_type.lower().split(";")[0].strip()

        if mime_clean in ("text/csv", "text/tab-separated-values") or source_uri.endswith((".csv", ".tsv")):
            return self._process_csv(decoded_text, source_uri, encoding_used)
        elif mime_clean in ("application/json", "application/x-ndjson") or source_uri.endswith((".json", ".jsonl", ".ndjson")):
            return self._process_json(decoded_text, source_uri, encoding_used)
        elif mime_clean == "text/markdown" or source_uri.endswith((".md", ".markdown")):
            return self._process_markdown(decoded_text, source_uri, encoding_used)
        else:
            return TextExtractionResult(
                text=decoded_text.strip(),
                format_type="plaintext",
                metadata={"source_uri": source_uri, "encoding": encoding_used, "char_count": len(decoded_text)},
                ocr_engine_used="plaintext_reader",
            )

    def _decode_bytes(self, raw_bytes: bytes) -> Tuple[str, str]:
        """Robust encoding resolution ladder."""
        # 1. UTF-8 (handles BOM)
        try:
            return raw_bytes.decode("utf-8-sig"), "utf-8-sig"
        except UnicodeDecodeError:
            pass

        # 2. UTF-16
        try:
            return raw_bytes.decode("utf-16"), "utf-16"
        except UnicodeDecodeError:
            pass

        # 3. Windows-1252 / CP1252
        try:
            return raw_bytes.decode("cp1252"), "cp1252"
        except UnicodeDecodeError:
            pass

        # 4. Chardet heuristic
        detected = chardet.detect(raw_bytes[:65536])
        if detected and detected.get("encoding"):
            try:
                enc = detected["encoding"]
                return raw_bytes.decode(enc), enc
            except (UnicodeDecodeError, LookupError):
                pass

        # 5. Latin-1 fallback
        return raw_bytes.decode("latin-1", errors="replace"), "latin-1-replace"

    def _process_csv(self, csv_text: str, source_uri: str, encoding: str) -> TextExtractionResult:
        """Parses CSV and converts to Markdown table."""
        sample = csv_text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample)
            delimiter = dialect.delimiter
        except Exception:
            delimiter = "\t" if source_uri.endswith(".tsv") else ","

        reader = csv.reader(io.StringIO(csv_text), delimiter=delimiter)
        rows: List[List[str]] = []
        for i, row in enumerate(reader):
            if i > 5000:  # Bound table rendering size
                rows.append(["... (truncated remaining rows) ..."])
                break
            cells = [" ".join(c.strip().split()).replace("|", "\\|") for c in row]
            if any(cells):
                rows.append(cells)

        if not rows:
            return TextExtractionResult(
                text=csv_text.strip(),
                format_type="csv",
                metadata={"source_uri": source_uri, "rows": 0, "encoding": encoding},
                ocr_engine_used="csv_parser",
            )

        col_count = max(len(r) for r in rows)
        padded_rows = [r + [""] * (col_count - len(r)) for r in rows]
        header = "| " + " | ".join(padded_rows[0]) + " |"
        separator = "| " + " | ".join(["---"] * col_count) + " |"
        body = ["| " + " | ".join(r) + " |" for r in padded_rows[1:]]
        md_text = "\n".join([header, separator] + body)

        return TextExtractionResult(
            text=md_text,
            format_type="csv",
            metadata={
                "source_uri": source_uri,
                "row_count": len(rows),
                "col_count": col_count,
                "delimiter": delimiter,
                "encoding": encoding,
            },
            ocr_engine_used="csv_parser",
        )

    def _process_json(self, json_text: str, source_uri: str, encoding: str) -> TextExtractionResult:
        """Parses JSON / JSONL and formats as indented text."""
        try:
            # Check single JSON object/array
            data = json.loads(json_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return TextExtractionResult(
                text=formatted,
                format_type="json",
                metadata={"source_uri": source_uri, "is_valid_json": True, "encoding": encoding},
                ocr_engine_used="json_parser",
            )
        except Exception:
            # Check JSONL
            lines = json_text.strip().splitlines()
            parsed_lines = []
            for line in lines:
                l_strip = line.strip()
                if not l_strip:
                    continue
                try:
                    obj = json.loads(l_strip)
                    parsed_lines.append(json.dumps(obj, ensure_ascii=False))
                except Exception:
                    parsed_lines.append(l_strip)

            return TextExtractionResult(
                text="\n".join(parsed_lines),
                format_type="jsonl",
                metadata={"source_uri": source_uri, "jsonl_line_count": len(parsed_lines), "encoding": encoding},
                ocr_engine_used="json_parser",
            )

    def _process_markdown(self, md_text: str, source_uri: str, encoding: str) -> TextExtractionResult:
        """Extracts Markdown body and optional frontmatter metadata."""
        frontmatter_meta: Dict[str, Any] = {}
        cleaned_text = md_text

        # Check YAML frontmatter (--- \n ... \n ---)
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md_text, re.DOTALL)
        if match:
            fm_raw = match.group(1)
            cleaned_text = match.group(2).strip()
            for line in fm_raw.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    frontmatter_meta[k.strip().lower()] = v.strip()

        return TextExtractionResult(
            text=cleaned_text,
            format_type="markdown",
            metadata={
                "source_uri": source_uri,
                "frontmatter": frontmatter_meta,
                "encoding": encoding,
            },
            ocr_engine_used="markdown_reader",
        )
```

---

## 8. Module 6: Unified Document Extractor & Dispatcher (`document_extractor.py`)

### 8.1 Dispatch Architecture & Contract Adherence
`DocumentExtractor` is the authoritative facade integrating all format-specific extractors and connecting Milestone 1 artifacts to Milestone 3 records.

It enforces the following execution lifecycle:
```
IngestedArtifact ──> MIME / Extension Classifier
                            │
            ┌───────────────┼───────────────┬───────────────┬───────────────┐
            ▼               ▼               ▼               ▼               ▼
      [PdfExtractor] [TiffExtractor] [ImageExtractor] [HtmlParser]   [DocxExtractor]
            │               │               │               │               │
            └───────────────┴───────────────┼───────────────┴───────────────┘
                                            │
                                    (Raw Extracted Text)
                                            │
                                            ▼
                             [Multi-Tier Normalizer Suite]
                       - DateNormalizer (ISO 8601 UTC)
                       - FinancialNormalizer (Float + Integer Cents)
                       - CaseNormalizer (Federal/State Dockets)
                       - Entity/Metadata Senders & Recipients
                                            │
                                            ▼
                                     ExtractedRecord
```

### 8.2 Complete Technical Specification & Implementation Blueprint

```python
"""
OsintNeoAi Indexer — Unified Document Extractor & MIME Dispatcher
Module: workspaces.osintneoai_indexer.extractors.document_extractor
Milestone: M2 (Deep Text Extraction & OCR Engine)
"""

from __future__ import annotations

import io
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from config import EXTENSION_MAPPINGS, FileCategory, IndexerConfig, get_file_category, get_mime_type
from connectors.local_crawler import IngestedArtifact
from extractors.docx_extractor import DocxExtractor
from extractors.html_parser import HtmlDocumentParser
from extractors.image_enhancer import ImageEnhancer
from extractors.image_extractor import ImageExtractor
from extractors.ocr_engine import RapidOCREngine
from extractors.pdf_extractor import PdfExtractor
from extractors.text_extractor import TextExtractor
from extractors.tiff_extractor import TiffExtractor
from normalizers.case_normalizer import CaseNormalizer
from normalizers.date_normalizer import DateNormalizer
from normalizers.financial_normalizer import FinancialNormalizer

logger = logging.getLogger("osintneoai.extractors.dispatcher")


@dataclass
class ExtractedRecord:
    """
    Authoritative M2 ↔ M3 Interface Contract data model.
    Matches PROJECT.md specification exactly.
    """
    record_id: str               # UUID or deterministic artifact-derived ID
    artifact_sha256: str         # Canonical SHA-256 hex string
    source_path: str             # Source URI / filesystem path
    source_type: str             # 'local_file', 'gdrive', 'mailbox', 'archive_member'
    mime_type: str               # Canonical MIME type string
    normalized_date: Optional[str] # ISO 8601 UTC date string (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
    raw_date_string: Optional[str] # Original matched unparsed timestamp string
    extracted_text: str          # Normalized text body
    ocr_engine_used: str         # 'pymupdf_native', 'rapidocr_onnx', 'lxml_html_parser', etc.
    financial_amounts: List[Dict[str, Any]] = field(default_factory=list) # [{"raw": "$320M", "amount_float": 320000000.0, "amount_cents": 32000000000, "currency": "USD"}]
    case_numbers: List[str] = field(default_factory=list)      # ["8:23-cr-00108-CJC", "30-2021-01201327-CL-UD-CJC"]
    sender: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentExtractor:
    """
    Central Extraction Dispatcher coordinating format-specific extractors,
    OCR engines, and multi-tier normalizers.
    """

    def __init__(self, config: Optional[IndexerConfig] = None) -> None:
        self.config = config or IndexerConfig.default()

        # Core Engines
        self.ocr_engine = RapidOCREngine.get_instance()
        self.image_enhancer = ImageEnhancer()

        # Format Extractors
        self.pdf_extractor = PdfExtractor(ocr_engine=self.ocr_engine, enhancer=self.image_enhancer, config=self.config)
        self.tiff_extractor = TiffExtractor(ocr_engine=self.ocr_engine, confidence_threshold=self.config.ocr_confidence_threshold)
        self.image_extractor = ImageExtractor(ocr_engine=self.ocr_engine, enhancer=self.image_enhancer, confidence_threshold=self.config.ocr_confidence_threshold)
        self.html_parser = HtmlDocumentParser()
        self.docx_extractor = DocxExtractor()
        self.text_extractor = TextExtractor()

        # Normalizers
        self.date_normalizer = DateNormalizer()
        self.financial_normalizer = FinancialNormalizer()
        self.case_normalizer = CaseNormalizer()

    def extract(self, artifact: IngestedArtifact) -> ExtractedRecord:
        """
        Main extraction entry point consuming an IngestedArtifact and producing
        a fully normalized ExtractedRecord.
        """
        mime = (artifact.mime_type or get_mime_type(artifact.source_uri)).lower().split(";")[0].strip()
        source_uri = artifact.source_uri
        source_type = self._classify_source_type(source_uri)
        record_id = f"rec_{artifact.artifact_id[:16]}"

        extracted_text = ""
        ocr_engine_used = "unknown"
        extracted_meta: Dict[str, Any] = {}
        sender: Optional[str] = None
        recipients: List[str] = []
        raw_date_candidate: Optional[str] = None

        try:
            stream = artifact.raw_stream_factory()
            try:
                # 1. Dispatch based on MIME Type / File Category
                if mime == "application/pdf" or source_uri.lower().endswith(".pdf"):
                    res = self.pdf_extractor.extract_from_stream(stream, source_uri)
                    extracted_text = res.text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.metadata)

                elif mime == "image/tiff" or source_uri.lower().endswith((".tif", ".tiff")):
                    res = self.tiff_extractor.extract_from_stream(stream, source_uri)
                    extracted_text = res.full_text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.metadata)

                elif mime.startswith("image/") or source_uri.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")):
                    res = self.image_extractor.extract_from_stream(stream, source_uri)
                    extracted_text = res.text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.exif_metadata)
                    if "DateTimeOriginal" in res.exif_metadata:
                        raw_date_candidate = str(res.exif_metadata["DateTimeOriginal"])

                elif mime in ("text/html", "application/xhtml+xml") or source_uri.lower().endswith((".html", ".htm", ".xhtml")):
                    res = self.html_parser.extract_from_stream(stream, source_uri)
                    extracted_text = res.text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.metadata)
                    if res.email_addresses:
                        recipients.extend(res.email_addresses)
                    if "date" in res.meta_tags:
                        raw_date_candidate = res.meta_tags["date"]

                elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or source_uri.lower().endswith(".docx"):
                    res = self.docx_extractor.extract_from_stream(stream, source_uri)
                    extracted_text = res.text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.metadata)
                    if res.author:
                        sender = res.author
                    if res.created_date:
                        raw_date_candidate = res.created_date

                else:
                    # Plaintext, Tabular, JSON, Markdown, Logs
                    res = self.text_extractor.extract_from_stream(stream, mime, source_uri)
                    extracted_text = res.text
                    ocr_engine_used = res.ocr_engine_used
                    extracted_meta.update(res.metadata)

            finally:
                if hasattr(stream, "close"):
                    stream.close()

        except Exception as extract_err:
            logger.error(f"Unhandled extraction failure on {source_uri}: {extract_err}", exc_info=True)
            extracted_text = f"[ERROR: Extraction exception: {extract_err}]"
            ocr_engine_used = "error_fallback"
            extracted_meta["error"] = str(extract_err)

        # 2. Multi-Tier Normalization Pipeline
        # Date Normalization
        norm_date, matched_date_raw = self.date_normalizer.normalize(
            text=extracted_text,
            fallback_date_str=raw_date_candidate,
            source_uri=source_uri,
        )

        # Financial Normalization (Dual Float + Integer Cents)
        financial_amounts = self.financial_normalizer.extract_all(extracted_text)

        # Case & Docket Normalization
        case_numbers = self.case_normalizer.extract_dockets(extracted_text)

        # Merge Contextual Metadata
        if artifact.metadata:
            extracted_meta["artifact_metadata"] = artifact.metadata

        return ExtractedRecord(
            record_id=record_id,
            artifact_sha256=artifact.artifact_id,
            source_path=source_uri,
            source_type=source_type,
            mime_type=mime,
            normalized_date=norm_date,
            raw_date_string=matched_date_raw or raw_date_candidate,
            extracted_text=extracted_text,
            ocr_engine_used=ocr_engine_used,
            financial_amounts=financial_amounts,
            case_numbers=case_numbers,
            sender=sender,
            recipients=recipients,
            metadata=extracted_meta,
        )

    def _classify_source_type(self, source_uri: str) -> str:
        """Classifies origin of artifact."""
        if source_uri.startswith("gdrive://") or "drive.google.com" in source_uri:
            return "gdrive"
        elif source_uri.startswith("zip://") or source_uri.startswith("tar://"):
            return "archive_member"
        elif source_uri.startswith("mailbox://") or source_uri.endswith((".mbox", ".eml", ".msg")):
            return "mailbox"
        else:
            return "local_file"
```

---

## 9. Error Handling, Memory Invariance & Edge Case Mitigations

| Edge Case | Root Cause & Failure Mode | Mitigation & Recovery Strategy |
|---|---|---|
| **High-Res Bilevel TIFF Scans** | 2540x3288 1-bit scan modes (`mode: '1'`) causing ONNX dtype errors. | Convert mode `1` / `L` to `RGB` using `PIL.Image.convert('RGB')` before passing to numpy array. Explicitly delete arrays and call `gc.collect()` every 5 frames. |
| **`lxml.html.clean` Removal** | `lxml >= 5.2.0` deprecated and extracted clean module to separate package. | Use native `lxml.etree.strip_elements(root, *STRIP_TAGS)` and custom DOM traversal. Fallback to `html.parser.HTMLParser`. |
| **Sideways Phone Photos (EXIF)** | Camera photos have EXIF rotation tags; sideways text fails OCR. | Apply `PIL.ImageOps.exif_transpose()` immediately upon opening before inference. |
| **Malformed Charsets & Corrupt TXT** | Multi-byte UTF-16, Windows-1252, or broken UTF-8 sequences. | 5-stage encoding resolution ladder (`utf-8-sig` -> `utf-16` -> `cp1252` -> `chardet` -> `latin-1` replace). |
| **DOCX without Text in Body** | Scanned pages or blueprints pasted as images into Word document. | Inspect embedded images (`zip.namelist()`) and log image presence in metadata. |
| **Large CSV Files (>50 MB)** | Memory spike rendering 500,000 Markdown table rows. | Bound table rendering to first 5,000 rows and append truncation notification. |
| **Non-Seekable Streams** | `raw_stream_factory` returning unbuffered socket/pipe stream. | Wrap in `io.BytesIO(stream.read())` if `stream.seekable()` returns False. |

---

## 10. Verification & Test Suite Matrix

To guarantee robust extraction, the implementation includes comprehensive pytest fixtures:

| Test Case | Target Module | Verification Condition |
|---|---|---|
| `test_tiff_multipage_streaming` | `tiff_extractor.py` | 3-page synthetic TIFF extracts 3 frames with page boundary markers and `rapidocr_onnx_tiff`. |
| `test_tiff_bilevel_real_hospital_record` | `tiff_extractor.py` | Real `General Consent for Treatment.TIF` extracts > 40 OCR lines without memory fault. |
| `test_html_table_markdown_formatting` | `html_parser.py` | HTML table converts to Markdown grid with headers and pipe separators. |
| `test_html_script_stripping` | `html_parser.py` | Embedded `<script>` and `<style>` blocks are 100% removed without leaking into body text. |
| `test_docx_paragraphs_and_comments` | `docx_extractor.py` | DOCX extracts heading `#`, tables, and annotations from `word/comments.xml`. |
| `test_image_exif_orientation_ocr` | `image_extractor.py` | Rotated image with EXIF orientation 6 correctly transposed and transcribed. |
| `test_csv_delimiter_sniffing` | `text_extractor.py` | Semicolon and comma CSV files detected and parsed into Markdown tables. |
| `test_document_extractor_contract` | `document_extractor.py` | Returns valid `ExtractedRecord` matching `PROJECT.md` schema with all fields populated. |

---
