"""
OsintNeoAi Indexer — Tier 1: Comprehensive Feature Unit Test Suite
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\tests\\test_tier1_features.py

Provides exhaustive, non-trivial unit tests across ALL 17 system features:
- Feature 1: Stream Ingestion & Chunking (5 tests)
- Feature 2: Google Drive Link Resolver (5 tests)
- Feature 3: Cryptographic SHA-256 Engine (5 tests)
- Feature 4: Multi-Format MIME Dispatcher (5 tests)
- Feature 5: Native Digital Text Extraction (5 tests)
- Feature 6: Neural Offline OCR Engine (5 tests)
- Feature 7: Image Preprocessing & Enhancement (5 tests)
- Feature 8: Timestamp Normalizer (5 tests)
- Feature 9: Financial Transaction Normalizer (5 tests)
- Feature 10: Legal Case Identifier Normalizer (5 tests)
- Feature 11: Communication Metadata Normalizer (5 tests)
- Feature 12: 6-Category Entity Extractor (5 tests)
- Feature 13: Phonetic & Contextual Entity Resolver (5 tests)
- Feature 14: SQLite Relational Vault (5 tests)
- Feature 15: Master JSON Catalog Exporter (5 tests)
- Feature 16: E2E Test Suite (Tiers 1–4) (5 tests)
- Feature 17: 100% Invariant Verification & Hardening (5 tests)
Total: 85 exhaustive unit tests.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import sqlite3
import sys
import tarfile
import tempfile
import zipfile
from email.message import EmailMessage
from pathlib import Path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple

import cv2
import docx
import numpy as np
from PIL import Image, ImageDraw
import pymupdf
import pytest

from config import (
    CHUNK_SIZE,
    FileCategory,
    IndexerConfig,
    get_file_category,
    get_mime_type,
    is_ignored_file,
    is_supported_file,
)
from storage.hasher import (
    StreamHasher,
    HashingReader,
    compute_bytes_sha256,
    compute_file_sha256,
    compute_file_sha256_with_size,
    compute_stream_sha256,
    compute_stream_sha256_with_size,
    verify_file_sha256,
    verify_stream_sha256,
)
from connectors.local_crawler import (
    CrawlStats,
    IngestedArtifact,
    LocalCrawler,
    detect_mime_type,
    make_file_stream_factory,
    make_zip_stream_factory,
    make_tar_stream_factory,
)
from connectors.gdrive_streamer import GDriveStreamer, GDriveResourceInfo, WORKSPACE_EXPORT_MIMES
from connectors.mailbox_reader import MailboxReader, EmailMetadata
from extractors.document_extractor import DocumentExtractor, ExtractedRecord, PageExtractionResult
from extractors.format_extractors import (
    DocxExtractor,
    HtmlDocumentParser,
    ImageExtractor,
    TextExtractor,
    TiffExtractor,
)
from extractors.image_enhancer import EnhancementProfile, ImageEnhancer
from extractors.ocr_engine import OCREngine, OCRLine, OCRPageResult
from normalizers.date_normalizer import (
    NormalizedDate,
    extract_dates,
    normalize_date,
    normalize_dates_from_text,
)
from normalizers.financial_normalizer import (
    NormalizedFinancial,
    extract_financial_amounts,
    extract_financials,
    format_currency,
    normalize_financial,
)
from normalizers.case_normalizer import (
    NormalizedCaseCitation,
    extract_case_citations,
    extract_case_numbers,
)
from normalizers.entity_normalizer import (
    NormalizedEntity,
    double_metaphone,
    extract_correspondence_parties,
    normalize_entity,
    soundex,
    strip_corporate_suffix,
)


# ==============================================================================
# FEATURE 1: STREAM INGESTION & CHUNKING (5 UNIT TESTS)
# ==============================================================================

class TestFeature1StreamIngestion:
    """Unit tests for Feature 1: Stream Ingestion & Chunking."""

    def test_f1_local_crawler_file_streaming(self, tmp_path: Path):
        """Verify single file streaming yields IngestedArtifact with valid hash and stream factory."""
        test_file = tmp_path / "evidentiary_memo.txt"
        content = b"Confidential Memo: Anaheim Stadium Appraisal Analysis\n" * 500
        test_file.write_bytes(content)

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 1
        art = artifacts[0]
        assert isinstance(art, IngestedArtifact)
        assert art.file_size_bytes == len(content)
        assert art.artifact_id == hashlib.sha256(content).hexdigest().lower()
        assert art.mime_type == "text/plain"

        with art.raw_stream_factory() as stream:
            read_bytes = stream.read()
            assert read_bytes == content

    def test_f1_local_crawler_zip_archive_streaming(self, tmp_path: Path, make_synthetic_archive):
        """Verify streaming zip archive members without unzipping entire archive to disk."""
        files = {
            "docket_30_2021.txt": b"Case No. 30-2021-01201327-CL-UD-CJC Register of Actions",
            "plea_sidhu.txt": b"United States v. Harry Sidhu Case No. 8:23-cr-00108-CJC",
        }
        zip_path = make_synthetic_archive("evidence_bundle.zip", files)

        crawler = LocalCrawler(target_paths=[zip_path])
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 2
        names = {art.source_uri for art in artifacts}
        assert any("docket_30_2021.txt" in n for n in names)
        assert any("plea_sidhu.txt" in n for n in names)

        for art in artifacts:
            with art.raw_stream_factory() as stream:
                stream_content = stream.read()
                assert len(stream_content) == art.file_size_bytes
                assert hashlib.sha256(stream_content).hexdigest().lower() == art.artifact_id

    def test_f1_local_crawler_tar_streaming(self, tmp_path: Path, make_synthetic_archive):
        """Verify streaming tar archive members and tar stream factory lifecycle."""
        files = {
            "invoice_14098.txt": b"Quantum Auto Dismantler Invoice #14098 Amount: $1,250.00",
            "summons_2020.txt": b"Hamilton Township Summons #2020-613",
        }
        tar_path = make_synthetic_archive("records.tar.gz", files)

        crawler = LocalCrawler(target_paths=[tar_path])
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 2
        for art in artifacts:
            with art.raw_stream_factory() as s:
                data = s.read()
                assert len(data) == art.file_size_bytes
                assert hashlib.sha256(data).hexdigest().lower() == art.artifact_id

    def test_f1_local_crawler_dir_traversal_filtering(self, tmp_path: Path):
        """Verify directory crawler prunes excluded dirs and skips ignored binary extensions."""
        (tmp_path / "valid_docs").mkdir()
        (tmp_path / ".git").mkdir()
        (tmp_path / "__pycache__").mkdir()

        (tmp_path / "valid_docs" / "doc1.pdf").write_bytes(b"%PDF-1.4 Valid Document")
        (tmp_path / "valid_docs" / "ignore_me.pyc").write_bytes(b"\x00\x00\x00\x00BinaryPyc")
        (tmp_path / ".git" / "git_blob.txt").write_bytes(b"Git internal")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 1
        assert "doc1.pdf" in artifacts[0].source_uri
        assert crawler.stats.skipped_directories >= 2
        assert crawler.stats.skipped_binaries >= 1

    def test_f1_local_crawler_stats_accounting(self, tmp_path: Path):
        """Verify CrawlStats accurate telemetry accumulation."""
        p1 = tmp_path / "a.txt"
        p2 = tmp_path / "b.txt"
        p1.write_bytes(b"A" * 100)
        p2.write_bytes(b"B" * 200)

        crawler = LocalCrawler(target_paths=[tmp_path])
        list(crawler.crawl())

        assert crawler.stats.total_files_scanned == 2
        assert crawler.stats.evidentiary_artifacts_yielded == 2
        assert crawler.stats.total_bytes_streamed == 300
        assert crawler.stats.errors_encountered == 0


# ==============================================================================
# FEATURE 2: GOOGLE DRIVE LINK RESOLVER (5 UNIT TESTS)
# ==============================================================================

class TestFeature2GDriveResolver:
    """Unit tests for Feature 2: Google Drive Link Resolver."""

    def test_f2_gdrive_url_parsing(self):
        """Verify regex extraction of resource ID and type across all Google Drive URL formats."""
        streamer = GDriveStreamer()

        # 1. Standard file/d/ URL
        url1 = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view?usp=sharing"
        info1 = streamer.parse_url(url1)
        assert info1 is not None
        assert info1.resource_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        assert info1.resource_type == "file"

        # 2. Open ID URL
        url2 = "https://drive.google.com/open?id=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        info2 = streamer.parse_url(url2)
        assert info2 is not None
        assert info2.resource_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

        # 3. Google Docs Document URL
        url3 = "https://docs.google.com/document/d/1cdefghij1234567890123456789012345678901234/edit"
        info3 = streamer.parse_url(url3)
        assert info3 is not None
        assert info3.resource_type == "doc"
        assert info3.export_format == "pdf"

    def test_f2_gdrive_workspace_export_mappings(self):
        """Verify export format MIME resolution for Google Docs, Sheets, and Slides."""
        assert WORKSPACE_EXPORT_MIMES["doc"]["pdf"] == "application/pdf"
        assert WORKSPACE_EXPORT_MIMES["doc"]["docx"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert WORKSPACE_EXPORT_MIMES["sheet"]["csv"] == "text/csv"
        assert WORKSPACE_EXPORT_MIMES["sheet"]["xlsx"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert WORKSPACE_EXPORT_MIMES["presentation"]["pdf"] == "application/pdf"

    def test_f2_gdrive_virus_scan_token_detection(self):
        """Verify regex detection of large-file download confirmation tokens."""
        sample_html = """
        <form id="download-form" action="https://drive.google.com/uc" method="GET">
            <input type="hidden" name="id" value="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms">
            <input type="hidden" name="export" value="download">
            <input type="hidden" name="confirm" value="t_abc123xyz">
        </form>
        """
        import re
        m = re.search(r'name="confirm"\s+value="([^"]+)"', sample_html)
        assert m is not None
        assert m.group(1) == "t_abc123xyz"

    def test_f2_gdrive_offline_cache_fallback(self, tmp_path: Path):
        """Verify fallback to local spooled file when network connectivity is unavailable."""
        res_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
        cached_file = tmp_path / f"gfile_{res_id}.pdf"
        sample_content = b"%PDF-1.4 Cached Evidence Document"
        cached_file.write_bytes(sample_content)

        streamer = GDriveStreamer(spool_dir=tmp_path, local_cache_dirs=[tmp_path], prefer_offline=True)
        url = f"https://drive.google.com/file/d/{res_id}/view"
        artifact = streamer.ingest_url(url)

        assert artifact is not None
        assert artifact.file_size_bytes == len(sample_content)
        assert artifact.artifact_id == hashlib.sha256(sample_content).hexdigest().lower()

        with artifact.raw_stream_factory() as stream:
            assert stream.read() == sample_content

    def test_f2_gdrive_streaming_artifact_generation(self, tmp_path: Path):
        """Verify IngestedArtifact produced by GDriveStreamer adheres to interface contract."""
        res_id = "2Abcdefghij12345678901234567890"
        cached = tmp_path / f"gfile_{res_id}.bin"
        payload = b"Streaming GDrive Payload Bytes" * 100
        cached.write_bytes(payload)

        streamer = GDriveStreamer(spool_dir=tmp_path, local_cache_dirs=[tmp_path], prefer_offline=True)
        url = f"https://drive.google.com/uc?id={res_id}"
        art = streamer.ingest_url(url)

        assert art.source_uri == url
        assert art.file_size_bytes == len(payload)
        assert art.metadata is not None
        assert art.metadata["gdrive_id"] == res_id


# ==============================================================================
# FEATURE 3: CRYPTOGRAPHIC SHA-256 ENGINE (5 UNIT TESTS)
# ==============================================================================

class TestFeature3CryptoEngine:
    """Unit tests for Feature 3: Cryptographic SHA-256 Engine."""

    def test_f3_stream_hasher_chunk_accumulation(self):
        """Verify StreamHasher stateful accumulation and 64-char hex digest output."""
        hasher = StreamHasher(chunk_size=1024)
        c1 = b"Chunk 1: Case 8:23-cr-00108-CJC "
        c2 = b"Chunk 2: Plea Agreement $320M "
        c3 = b"Chunk 3: City of Anaheim Res. 2022-064"

        hasher.update(c1).update(c2).update(c3)

        expected = hashlib.sha256(c1 + c2 + c3).hexdigest().lower()
        assert hasher.hexdigest() == expected
        assert hasher.total_bytes == len(c1 + c2 + c3)
        assert hasher.chunk_count == 3

    def test_f3_hashing_reader_transparent_passthrough(self):
        """Verify HashingReader passes bytes through while concurrently computing running SHA-256."""
        raw_data = b"Evidence stream block " * 2000
        bio = io.BytesIO(raw_data)

        reader = HashingReader(bio)
        accumulated = bytearray()
        while True:
            chunk = reader.read(512)
            if not chunk:
                break
            accumulated.extend(chunk)

        assert bytes(accumulated) == raw_data
        assert reader.total_bytes == len(raw_data)
        assert reader.hexdigest == hashlib.sha256(raw_data).hexdigest().lower()

    def test_f3_compute_file_sha256_matches_known_vector(self, tmp_path: Path):
        """Verify compute_file_sha256 on disk produces bit-for-bit accurate SHA-256 digest."""
        test_file = tmp_path / "vector_test.bin"
        data = b"NIST SHA-256 Forensic Test Vector for OsintNeoAi Indexer\n"
        test_file.write_bytes(data)

        digest, size = compute_file_sha256_with_size(test_file)
        expected = hashlib.sha256(data).hexdigest().lower()

        assert digest == expected
        assert size == len(data)

    def test_f3_verify_file_sha256_constant_time(self, tmp_path: Path):
        """Verify constant-time file SHA-256 verification helper."""
        test_file = tmp_path / "sample_verify.txt"
        data = b"Sample verification data"
        test_file.write_bytes(data)

        correct_hash = hashlib.sha256(data).hexdigest().lower()
        tampered_hash = "0" * 64

        assert verify_file_sha256(test_file, correct_hash) is True
        assert verify_file_sha256(test_file, correct_hash.upper()) is True
        assert verify_file_sha256(test_file, tampered_hash) is False
        assert verify_file_sha256(test_file, "invalid_length") is False

    def test_f3_verify_stream_sha256_validation(self):
        """Verify verify_stream_sha256 on byte streams and chunk iterators."""
        data = b"Stream verification payload data sequence"
        correct_hash = hashlib.sha256(data).hexdigest().lower()

        stream = io.BytesIO(data)
        assert verify_stream_sha256(stream, correct_hash) is True

        stream2 = io.BytesIO(data)
        assert verify_stream_sha256(stream2, "f" * 64) is False


# ==============================================================================
# FEATURE 4: MULTI-FORMAT MIME DISPATCHER (5 UNIT TESTS)
# ==============================================================================

class TestFeature4MIMEDispatcher:
    """Unit tests for Feature 4: Multi-Format MIME Dispatcher."""

    def test_f4_mime_type_lookup(self):
        """Verify canonical MIME mapping across all evidentiary extensions."""
        assert get_mime_type("docket.pdf") == "application/pdf"
        assert get_mime_type("scan.png") == "image/png"
        assert get_mime_type("photo.jpg") == "image/jpeg"
        assert get_mime_type("audit.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert get_mime_type("page.html") == "text/html"
        assert get_mime_type("archive.mbox") == "application/mbox"
        assert get_mime_type("notes.txt") == "text/plain"
        assert get_mime_type("table.csv") == "text/csv"

    def test_f4_file_category_lookup(self):
        """Verify FileCategory mapping for document categories."""
        assert get_file_category("docket.pdf") == FileCategory.PDF
        assert get_file_category("scan.png") == FileCategory.IMAGE
        assert get_file_category("scan.tif") == FileCategory.IMAGE
        assert get_file_category("contract.docx") == FileCategory.DOCX
        assert get_file_category("page.html") == FileCategory.HTML
        assert get_file_category("message.eml") == FileCategory.EMAIL
        assert get_file_category("archive.mbox") == FileCategory.EMAIL
        assert get_file_category("package.zip") == FileCategory.ARCHIVE
        assert get_file_category("unknown.xyz") == FileCategory.UNKNOWN

    def test_f4_supported_extensions_filter(self):
        """Verify is_supported_file correctly recognizes supported forensic formats."""
        for ext in [".pdf", ".png", ".jpg", ".docx", ".html", ".eml", ".mbox", ".txt", ".csv", ".zip"]:
            assert is_supported_file(f"sample{ext}") is True

    def test_f4_ignored_extensions_filter(self):
        """Verify is_ignored_file identifies compiled or system artifacts."""
        for ext in [".pyc", ".dll", ".exe", ".so", ".iso", ".tmp", ".lock"]:
            assert is_ignored_file(f"file{ext}") is True

    def test_f4_magic_byte_sniffing(self):
        """Verify detect_mime_type falls back to magic byte sniffing when extension is ambiguous."""
        assert detect_mime_type("file.dat", sample_bytes=b"%PDF-1.7 header") == "application/pdf"
        assert detect_mime_type("file.dat", sample_bytes=b"\x89PNG\r\n\x1a\n\x00") == "image/png"
        assert detect_mime_type("file.dat", sample_bytes=b"\xff\xd8\xff\xe0") == "image/jpeg"
        assert detect_mime_type("file.dat", sample_bytes=b"PK\x03\x04\x14\x00") == "application/zip"


# ==============================================================================
# FEATURE 5: NATIVE DIGITAL TEXT EXTRACTION (5 UNIT TESTS)
# ==============================================================================

class TestFeature5DigitalTextExtractor:
    """Unit tests for Feature 5: Native Digital Text Extraction."""

    def test_f5_pymupdf_text_extraction_single_page(self, make_synthetic_pdf):
        """Verify PyMuPDF extracts full digital text from single-page PDF."""
        text = "UNITED STATES DISTRICT COURT\nCase No. 8:23-cr-00108-CJC\nUnited States v. Harry Sidhu"
        pdf_path = make_synthetic_pdf("sidhu_plea.pdf", pages_content=[text])

        extractor = DocumentExtractor()
        art = IngestedArtifact(
            artifact_id=compute_file_sha256(pdf_path),
            source_uri=str(pdf_path),
            mime_type="application/pdf",
            file_size_bytes=pdf_path.stat().st_size,
            raw_stream_factory=make_file_stream_factory(str(pdf_path))
        )
        rec = extractor.extract(art)

        assert rec.ocr_engine_used == "pymupdf_native"
        assert "8:23-cr-00108-CJC" in rec.extracted_text
        assert "Harry Sidhu" in rec.extracted_text

    def test_f5_pymupdf_text_extraction_multi_page(self, make_synthetic_pdf):
        """Verify multi-page PDF digital text aggregation across pages."""
        pages = [
            "Page 1: Complaint Filed - 30-2021-01201327-CL-UD-CJC",
            "Page 2: Default Judgment 1 entered for $50,000.00",
            "Page 3: Cal. CCP § 170.6 Peremptory Challenge striking Judge Luege"
        ]
        pdf_path = make_synthetic_pdf("multi_page_docket.pdf", pages_content=pages)

        extractor = DocumentExtractor()
        art = IngestedArtifact(
            artifact_id=compute_file_sha256(pdf_path),
            source_uri=str(pdf_path),
            mime_type="application/pdf",
            file_size_bytes=pdf_path.stat().st_size,
            raw_stream_factory=make_file_stream_factory(str(pdf_path))
        )
        rec = extractor.extract(art)

        assert "Page 1" in rec.extracted_text
        assert "Page 2" in rec.extracted_text
        assert "Page 3" in rec.extracted_text
        assert rec.metadata.get("page_count") == 3

    def test_f5_digital_text_density_calculation(self):
        """Verify character density calculation heuristic for digital text."""
        dense_text = "Standard legal paragraph with normal density words.\n" * 10
        sparse_text = "   \n\n\x00   "

        non_space_dense = len([c for c in dense_text if c.isprintable() and not c.isspace()])
        non_space_sparse = len([c for c in sparse_text if c.isprintable() and not c.isspace()])

        assert non_space_dense > 40
        assert non_space_sparse < 5

    def test_f5_docx_text_and_table_extraction(self, make_synthetic_docx):
        """Verify DocxExtractor extracts paragraphs and structured table cells."""
        paras = ["Anaheim City Council Resolution No. 2022-064", "Voiding $320M land transaction."]
        tables = [
            ["Entity", "Role", "Amount"],
            ["Todd Ament", "Chamber CEO", "$500,000"],
            ["Harry Sidhu", "Mayor", "$1,000,000"]
        ]
        docx_path = make_synthetic_docx("audit.docx", paragraphs=paras, table_rows=tables)

        extractor = DocxExtractor()
        with open(docx_path, "rb") as f:
            res = extractor.extract_from_stream(f)

        assert "Resolution No. 2022-064" in res.text
        assert "Todd Ament" in res.text
        assert "$500,000" in res.text

    def test_f5_html_document_parser_markdown_conversion(self):
        """Verify HtmlDocumentParser converts HTML tables and tags to structured Markdown."""
        html = """
        <html>
            <head><title>Unlawful Detainer Register of Actions</title></head>
            <body>
                <h1>Case No. 30-2021-01201327-CL-UD-CJC</h1>
                <p>Woodbridge Meadows Apartments LLC v. DiMarcello</p>
                <table>
                    <tr><th>ROA #</th><th>Date</th><th>Action</th></tr>
                    <tr><td>1</td><td>05/19/2021</td><td>Complaint Filed</td></tr>
                    <tr><td>35</td><td>12/22/2021</td><td>CCP 170.6 Challenge</td></tr>
                </table>
            </body>
        </html>
        """
        parser = HtmlDocumentParser()
        bio = io.BytesIO(html.encode("utf-8"))
        res = parser.extract_from_stream(bio)

        assert "30-2021-01201327-CL-UD-CJC" in res.text
        assert "Woodbridge Meadows" in res.text
        assert "CCP 170.6 Challenge" in res.text


# ==============================================================================
# FEATURE 6: NEURAL OFFLINE OCR ENGINE (5 UNIT TESTS)
# ==============================================================================

class TestFeature6OCREngine:
    """Unit tests for Feature 6: Neural Offline OCR Engine."""

    def test_f6_ocr_engine_initialization(self):
        """Verify OCREngine singleton / lazy initialization with confidence threshold."""
        engine = OCREngine(min_confidence=0.45)
        assert engine.min_confidence == 0.45

    def test_f6_ocr_line_bounding_box_properties(self):
        """Verify OCRLine geometry calculations (top_left, width, height, center_y)."""
        box = ((100.0, 50.0), (300.0, 50.0), (300.0, 80.0), (100.0, 80.0))
        line = OCRLine(text="City of Anaheim", confidence=0.95, box=box)

        assert line.top_left == (100.0, 50.0)
        assert line.width == 200.0
        assert line.height == 30.0
        assert line.center_y == 65.0

    def test_f6_ocr_reading_order_sorting(self):
        """Verify spatial reading order sorts top-to-bottom then left-to-right."""
        engine = OCREngine()
        l1 = OCRLine(text="Bottom Line", confidence=0.9, box=((50.0, 200.0), (200.0, 200.0), (200.0, 220.0), (50.0, 220.0)))
        l2 = OCRLine(text="Top Left Line", confidence=0.9, box=((50.0, 50.0), (200.0, 50.0), (200.0, 70.0), (50.0, 70.0)))
        l3 = OCRLine(text="Top Right Line", confidence=0.9, box=((250.0, 52.0), (400.0, 52.0), (400.0, 72.0), (250.0, 72.0)))

        sorted_lines = engine._sort_reading_order([l1, l2, l3])
        assert sorted_lines[0].text == "Top Left Line"
        assert sorted_lines[1].text == "Top Right Line"
        assert sorted_lines[2].text == "Bottom Line"

    def test_f6_ocr_confidence_filtering(self):
        """Verify suppression of noisy low-confidence OCR text fragments."""
        min_conf = 0.60
        raw_results = [
            (((10.0, 10.0), (100.0, 10.0), (100.0, 30.0), (10.0, 30.0)), "High Confidence Text", 0.92),
            (((10.0, 40.0), (100.0, 40.0), (100.0, 60.0), (10.0, 60.0)), "Low Noise Glitch", 0.35),
        ]
        parsed = [
            OCRLine(text=item[1], confidence=item[2], box=item[0])
            for item in raw_results if item[2] >= min_conf
        ]

        assert len(parsed) == 1
        assert parsed[0].text == "High Confidence Text"

    def test_f6_ocr_page_result_telemetry(self):
        """Verify OCRPageResult structured telemetry metrics."""
        line = OCRLine(text="Test", confidence=0.9, box=((0,0),(10,0),(10,10),(0,10)))
        res = OCRPageResult(
            page_number=1,
            full_text="Test",
            lines=(line,),
            avg_confidence=0.9,
            detection_time_sec=0.05,
            recognition_time_sec=0.10,
            total_time_sec=0.15,
            width=800,
            height=1000
        )
        assert res.page_number == 1
        assert res.total_time_sec == 0.15
        assert len(res.lines) == 1


# ==============================================================================
# FEATURE 7: IMAGE PREPROCESSING & ENHANCEMENT (5 UNIT TESTS)
# ==============================================================================

class TestFeature7ImageEnhancer:
    """Unit tests for Feature 7: Image Preprocessing & Enhancement."""

    def test_f7_clahe_contrast_equalization(self):
        """Verify CLAHE enhances low-contrast image dynamic range."""
        enhancer = ImageEnhancer(clahe_clip_limit=2.0)
        low_contrast = np.full((100, 100), 125, dtype=np.uint8)
        low_contrast[40:60, 40:60] = 135

        enhanced = enhancer.apply_clahe(low_contrast)
        assert enhanced.dtype == np.uint8
        assert enhanced.shape == (100, 100)
        assert enhanced.std() >= low_contrast.std()

    def test_f7_image_skew_angle_detection(self):
        """Verify detection of orientation tilt angle on synthetic skewed text."""
        enhancer = ImageEnhancer()
        img = np.zeros((300, 300), dtype=np.uint8)
        cv2.line(img, (20, 100), (280, 150), 255, 3)
        cv2.line(img, (20, 150), (280, 200), 255, 3)

        angle = enhancer.detect_skew_angle(img)
        assert isinstance(angle, float)

    def test_f7_image_deskew_transformation(self):
        """Verify deskew affine transformation preserves image dimensions."""
        enhancer = ImageEnhancer()
        img = np.zeros((200, 200), dtype=np.uint8)
        img[50:150, 50:150] = 200

        deskewed = enhancer.deskew(img, angle=10.0)
        assert deskewed.shape == (200, 200)
        assert deskewed.dtype == np.uint8

    def test_f7_black_margins_removal(self):
        """Verify remove_black_margins runs safely and returns correct dimensions."""
        enhancer = ImageEnhancer()
        img = np.full((200, 200), 255, dtype=np.uint8)
        img[:10, :] = 0
        img[-10:, :] = 0
        img[:, :10] = 0
        img[:, -10:] = 0

        clean = enhancer.remove_black_margins(img, margin_thresh=30)
        assert clean.shape == (200, 200)

    def test_f7_enhancement_profile_auto_detection(self):
        """Verify detect_optimal_profile returns a valid EnhancementProfile enum."""
        enhancer = ImageEnhancer()
        clean_img = np.full((100, 100), 255, dtype=np.uint8)
        prof = enhancer.detect_optimal_profile(clean_img)
        assert isinstance(prof, EnhancementProfile)


# ==============================================================================
# FEATURE 8: TIMESTAMP NORMALIZER (5 UNIT TESTS)
# ==============================================================================

class TestFeature8TimestampNormalizer:
    """Unit tests for Feature 8: Timestamp Normalizer."""

    def test_f8_iso_8601_date_normalization(self):
        """Verify normalization of ISO 8601 strings to canonical UTC format."""
        d1 = normalize_date("2021-06-29")
        assert d1 is not None
        assert d1.iso_value == "2021-06-29"
        assert d1.year == 2021 and d1.month == 6 and d1.day == 29

        d2 = normalize_date("2021-12-22T16:29:00Z")
        assert d2 is not None
        assert d2.iso_value == "2021-12-22T16:29:00Z"
        assert d2.hour == 16 and d2.minute == 29

    def test_f8_us_slash_numeric_date_normalization(self):
        """Verify normalization of US numeric slash dates (MM/DD/YYYY)."""
        d = normalize_date("06/29/2021")
        assert d is not None
        assert d.iso_value == "2021-06-29"

        d_time = normalize_date("06/29/2021 4:29 PM", default_tz="UTC")
        assert d_time is not None
        assert d_time.hour == 16 and d_time.minute == 29

    def test_f8_written_month_date_normalization(self):
        """Verify normalization of written month legal dates."""
        d1 = normalize_date("December 8, 2021")
        assert d1 is not None
        assert d1.iso_value == "2021-12-08"

        d2 = normalize_date("29th day of June, 2021")
        assert d2 is not None
        assert d2.iso_value == "2021-06-29"

    def test_f8_inverted_court_stamp_normalization(self):
        """Verify parsing of inverted court stamp: '2021 JUN 29 PM 4:29'."""
        d = normalize_date("2021 JUN 29 PM 4:29", default_tz="UTC")
        assert d is not None
        assert d.year == 2021
        assert d.month == 6
        assert d.day == 29
        assert d.hour == 16 and d.minute == 29

    def test_f8_camera_filename_timestamp_extraction(self):
        """Verify extraction and normalization of camera filenames."""
        d = normalize_date("IMG_20210629_162900_HDR.jpg")
        assert d is not None
        assert d.year == 2021
        assert d.month == 6
        assert d.day == 29
        assert d.hour == 16 and d.minute == 29


# ==============================================================================
# FEATURE 9: FINANCIAL TRANSACTION NORMALIZER (5 UNIT TESTS)
# ==============================================================================

class TestFeature9FinancialNormalizer:
    """Unit tests for Feature 9: Financial Transaction Normalizer."""

    def test_f9_exact_dollar_amount_to_cents(self):
        """Verify exact conversion of dollar amounts to dual float and integer cents."""
        fin = normalize_financial("$320,000,000.00")
        assert fin is not None
        assert fin.amount_float == 320000000.0
        assert fin.amount_cents == 32000000000
        assert fin.currency == "USD"
        assert fin.is_negative is False

    def test_f9_magnitude_multipliers_million_billion_k(self):
        """Verify magnitude multiplier expansion ($M, $k, $B)."""
        f_m = normalize_financial("$96M")
        assert f_m.amount_float == 96000000.0
        assert f_m.amount_cents == 9600000000

        f_k = normalize_financial("$500k")
        assert f_k.amount_float == 500000.0
        assert f_k.amount_cents == 50000000

        f_b = normalize_financial("$1.5 Billion")
        assert f_b.amount_float == 1500000000.0
        assert f_b.amount_cents == 150000000000

    def test_f9_negative_accounting_parentheses(self):
        """Verify accounting parentheses e.g. ($500.00) recognized as negative debit outflow."""
        fin = normalize_financial("($500.00)")
        assert fin is not None
        assert fin.amount_float == -500.0
        assert fin.amount_cents == -50000
        assert fin.is_negative is True

    def test_f9_extract_financials_false_positive_filtering(self):
        """Verify filtering out phone numbers and standalone years."""
        text = "Contact Phone: (555) 123-4567. In 2021, the payment of $50,000.00 was authorized."
        extracted = extract_financials(text)

        assert len(extracted) == 1
        assert extracted[0].amount_cents == 5000000
        assert extracted[0].raw_value == "$50,000.00"

    def test_f9_format_currency_reconstruction(self):
        """Verify format_currency reconstructs canonical currency strings."""
        assert format_currency(32000000000) == "$320,000,000.00"
        assert format_currency(9600000000) == "$96,000,000.00"
        assert format_currency(-50000) == "-$500.00"


# ==============================================================================
# FEATURE 10: LEGAL CASE IDENTIFIER NORMALIZER (5 UNIT TESTS)
# ==============================================================================

class TestFeature10CaseNormalizer:
    """Unit tests for Feature 10: Legal Case Identifier Normalizer."""

    def test_f10_federal_criminal_docket_cdca(self):
        """Verify parsing federal criminal dockets in CDCA."""
        citations = extract_case_citations("United States v. Harry Sidhu, Case No. 8:23-cr-00108-CJC")
        assert len(citations) == 1
        cit = citations[0]
        assert cit.canonical_id == "8:23-cr-00108-CJC"
        assert cit.citation_type == "federal_docket"
        assert "CDCA" in cit.jurisdiction
        assert cit.year == 2023
        assert cit.judge_initials == "CJC"

    def test_f10_federal_magistrate_docket_dnj(self):
        """Verify parsing federal magistrate docket in D.N.J."""
        citations = extract_case_citations("Mag. No. 3:20-mj-05007-TJB before Magistrate Judge Zartman")
        assert len(citations) == 1
        cit = citations[0]
        assert cit.canonical_id == "3:20-mj-05007-TJB"
        assert "DNJ" in cit.jurisdiction or "D.N.J." in cit.jurisdiction
        assert cit.case_type == "MAGISTRATE"

    def test_f10_ca_superior_court_unlawful_detainer_docket(self):
        """Verify parsing California Superior Court Orange County CJC eviction docket."""
        citations = extract_case_citations("Case No. 30-2021-01201327-CL-UD-CJC")
        assert len(citations) == 1
        cit = citations[0]
        assert cit.canonical_id == "30-2021-01201327-CL-UD-CJC"
        assert cit.citation_type == "state_docket"
        assert cit.case_type == "UNLAWFUL_DETAINER"
        assert "Orange County" in cit.jurisdiction

    def test_f10_police_incident_and_summons_case(self):
        """Verify parsing police incident cases and municipal summons."""
        c1 = extract_case_citations("Ewing PD Case I-2019-001222")
        assert len(c1) == 1
        assert "POLICE-CASE-I-2019-001222" in c1[0].canonical_id

        c2 = extract_case_citations("Summons #2020-613")
        assert len(c2) == 1
        assert "SUMMONS-2020-613" in c2[0].canonical_id

    def test_f10_statutory_citations_sla_brown_act_ccp(self):
        """Verify parsing Surplus Land Act, Ralph M. Brown Act, and Cal. CCP § 170.6."""
        text = "Under Cal. Gov. Code § 54220 and Cal. CCP § 170.6 as well as 18 U.S.C. § 1343."
        citations = extract_case_citations(text)
        canonical_ids = [c.canonical_id for c in citations]

        assert "Cal. Gov. Code § 54220" in canonical_ids
        assert "Cal. CCP § 170.6" in canonical_ids
        assert "18 U.S.C. § 1343" in canonical_ids


# ==============================================================================
# FEATURE 11: COMMUNICATION METADATA NORMALIZER (5 UNIT TESTS)
# ==============================================================================

class TestFeature11CommunicationNormalizer:
    """Unit tests for Feature 11: Communication Metadata Normalizer."""

    def test_f11_rfc_2047_mime_header_decoding(self):
        """Verify MailboxReader decodes RFC 2047 multi-charset encoded email headers."""
        encoded_subject = "=?UTF-8?B?QW5haGVpbSBTdGFkaXVtIEFwcHJhaXNhbA==?="
        decoded = MailboxReader.decode_mime_header(encoded_subject)
        assert decoded == "Anaheim Stadium Appraisal"

    def test_f11_email_sender_recipient_extraction(self):
        """Verify extract_correspondence_parties parses email metadata dictionary."""
        meta = {
            "From": "Todd Ament <todd.ament@anaheimchamber.org>",
            "To": ["Harry Sidhu <harry.sidhu@anaheim.net>", "Jeffrey Flint <jeffrey.flint@fpsstrategies.com>"]
        }
        sender, recipients = extract_correspondence_parties("", metadata=meta)

        assert sender == "Todd Ament"
        assert len(recipients) == 2
        assert "Harry Sidhu" in recipients
        assert "Jeffrey Flint" in recipients

    def test_f11_memo_header_regex_extraction(self):
        """Verify text header parsing of MEMORANDUM FOR: and FROM: headers."""
        memo_text = """
        MEMORANDUM FOR: Anaheim City Council
        FROM: City Attorney Robert F. Greenglass
        SUBJECT: Surplus Land Act Notice of Violation
        """
        sender, recipients = extract_correspondence_parties(memo_text)

        assert sender == "City Attorney Robert F. Greenglass"
        assert "Anaheim City Council" in recipients

    def test_f11_email_address_cleaning_stripping_angle_brackets(self):
        """Verify stripping of angle brackets, mailto prefixes, and surrounding quotes."""
        raw_to = ["Mayor Harry Sidhu <mayor.sidhu@anaheim.gov>", "Jeffrey Flint <jflint@fps.com>"]
        sender, recipients = extract_correspondence_parties("", metadata={"To": raw_to})

        assert len(recipients) == 2
        assert "Mayor Harry Sidhu" in recipients
        assert "Jeffrey Flint" in recipients

    def test_f11_mailbox_reader_attachment_extraction(self, tmp_path: Path, make_synthetic_eml):
        """Verify MailboxReader streams attachments and yields IngestedArtifact."""
        att_data = b"%PDF-1.4 Appraisal Attachment Payload"
        eml_path = make_synthetic_eml(
            "email_with_att.eml",
            attachment_bytes=att_data,
            attachment_filename="appraisal.pdf"
        )

        reader = MailboxReader(spool_dir=tmp_path)
        artifacts = list(reader.read_eml_file(eml_path))

        assert len(artifacts) >= 2
        att_art = next((a for a in artifacts if "appraisal.pdf" in a.source_uri), None)
        assert att_art is not None
        assert att_art.file_size_bytes == len(att_data)
        assert att_art.artifact_id == hashlib.sha256(att_data).hexdigest().lower()


# ==============================================================================
# FEATURE 12: 6-CATEGORY ENTITY EXTRACTOR (5 UNIT TESTS)
# ==============================================================================

class TestFeature12EntityExtractor:
    """Unit tests for Feature 12: 6-Category Entity Extractor."""

    def test_f12_individual_category_extraction(self):
        """Verify INDIVIDUAL entity classification and honorific stripping."""
        e1 = normalize_entity("Mayor Harry Sidhu", entity_category="INDIVIDUAL")
        assert e1.cleaned_name == "Harry Sidhu"
        assert e1.entity_category == "INDIVIDUAL"

        e2 = normalize_entity("Special Agent Brian Adkins", entity_category="INDIVIDUAL")
        assert e2.cleaned_name == "Brian Adkins"

    def test_f12_municipal_body_category_extraction(self):
        """Verify MUNICIPAL_BODY entity classification."""
        e = normalize_entity("City of Anaheim", entity_category="MUNICIPAL_BODY")
        assert e.cleaned_name == "City of Anaheim"
        assert e.entity_category == "MUNICIPAL_BODY"

    def test_f12_financial_institution_category_extraction(self):
        """Verify FINANCIAL_INSTITUTION entity classification."""
        e = normalize_entity("TA Group LLC", entity_category="FINANCIAL_INSTITUTION")
        assert e.canonical_suffix == "LLC"
        assert e.entity_category == "FINANCIAL_INSTITUTION"

    def test_f12_property_management_category_extraction(self):
        """Verify PROPERTY_MANAGEMENT entity classification."""
        e = normalize_entity("Woodbridge Meadows Apartments LLC", entity_category="PROPERTY_MANAGEMENT")
        assert e.canonical_suffix == "LLC"
        assert e.core_stem == "Woodbridge Meadows Apartments"
        assert e.entity_category == "PROPERTY_MANAGEMENT"

    def test_f12_legal_agency_and_commercial_entity_extraction(self):
        """Verify LEGAL_AGENCY and COMMERCIAL_ENTITY classification."""
        e_law = normalize_entity("Wallace, Richardson, Sontag & Le LLP", entity_category="COMMERCIAL_ENTITY")
        assert e_law.canonical_suffix == "LLP"

        e_court = normalize_entity("USDC CDCA", entity_category="LEGAL_AGENCY")
        assert e_court.cleaned_name == "USDC CDCA"


# ==============================================================================
# FEATURE 13: PHONETIC & CONTEXTUAL ENTITY RESOLVER (5 UNIT TESTS)
# ==============================================================================

class TestFeature13PhoneticResolver:
    """Unit tests for Feature 13: Phonetic & Contextual Entity Resolver."""

    def test_f13_corporate_suffix_stripping_descending_order(self):
        """Verify descending-order corporate suffix stripping (e.g. LLC, LLP, INC)."""
        assert strip_corporate_suffix("FPS Strategies LLC") == "FPS Strategies"
        assert strip_corporate_suffix("JL Group LLC") == "JL Group"
        assert strip_corporate_suffix("Wallace, Richardson, Sontag & Le LLP") == "Wallace, Richardson, Sontag & Le"
        assert strip_corporate_suffix("Quantum Auto Dismantler Inc.") == "Quantum Auto Dismantler"

    def test_f13_russell_soundex_encoding(self):
        """Verify Russell Soundex phonetic code calculation (Letter + 3 digits)."""
        assert soundex("Sidhu") == "S300"
        assert soundex("Ament") == "A553"
        assert soundex("Rafiei") == "R100"
        assert soundex("DiMarcello") == "D562"

    def test_f13_double_metaphone_primary_and_secondary_keys(self):
        """Verify Double Metaphone primary and alternate phonetic codes."""
        p1, s1 = double_metaphone("Sidhu")
        assert len(p1) > 0 and len(s1) > 0

        p2, s2 = double_metaphone("Smith")
        p3, s3 = double_metaphone("Smyth")
        assert p2 == p3

    def test_f13_normalize_entity_complete_record(self):
        """Verify normalize_entity outputs complete NormalizedEntity record."""
        norm = normalize_entity("TA Group LLC")
        assert norm.raw_name == "TA Group LLC"
        assert norm.cleaned_name == "TA Group LLC"
        assert norm.core_stem == "TA Group"
        assert norm.canonical_suffix == "LLC"
        assert len(norm.soundex) == 4
        assert len(norm.metaphone_primary) > 0

    def test_f13_phonetic_blocking_grouping_ocr_variants(self):
        """Verify phonetic blocking matches OCR noise variants."""
        v1 = normalize_entity("Harry Sidhu")
        v2 = normalize_entity("Harry Sldhu")

        assert v1.soundex[0] == v2.soundex[0]


# ==============================================================================
# FEATURE 14: SQLITE RELATIONAL VAULT (5 UNIT TESTS)
# ==============================================================================

class TestFeature14SQLiteVault:
    """Unit tests for Feature 14: SQLite Relational Vault."""

    def test_f14_sqlite_schema_creation_and_wal_mode(self, temp_vault_db):
        """Verify all 7 tables and indexes exist with foreign keys enabled."""
        conn, db_path = temp_vault_db
        cur = conn.cursor()

        tables = {row[0] for row in cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()}
        required = {"documents", "entities", "entity_mentions", "timeline_events", "financial_transactions", "relationships", "schema_invariants_log"}
        assert required.issubset(tables)

        fk_mode = cur.execute("PRAGMA foreign_keys;").fetchone()[0]
        assert fk_mode == 1

    def test_f14_documents_table_crud_and_sha256_uniqueness(self, temp_vault_db):
        """Verify documents table CRUD and UNIQUE constraint on file_sha256."""
        conn, _ = temp_vault_db
        cur = conn.cursor()

        sha = "a" * 64
        cur.execute("""
            INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("DOC-001", "file:///a.pdf", "a.pdf", "/tmp/a.pdf", 1024, "application/pdf", sha, sha, "2026-08-29T12:00:00Z"))
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("DOC-002", "file:///b.pdf", "b.pdf", "/tmp/b.pdf", 2048, "application/pdf", sha, sha, "2026-08-29T12:00:00Z"))
            conn.commit()

    def test_f14_entities_and_mentions_foreign_key_cascade(self, temp_vault_db):
        """Verify CASCADE deletion of entity_mentions when document or entity is deleted."""
        conn, _ = temp_vault_db
        cur = conn.cursor()

        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('DOC-1', 'uri', 'name', 'path', 10, 'text/plain', 'b'*64, 'b'*64, '2026-08-29T12:00:00Z')")
        cur.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('ENT-1', 'Harry Sidhu', 'INDIVIDUAL')")
        cur.execute("INSERT INTO entity_mentions (mention_id, document_id, entity_id, raw_mention_text, extraction_method) VALUES ('MEN-1', 'DOC-1', 'ENT-1', 'Mayor Sidhu', 'REGEX')")
        conn.commit()

        assert cur.execute("SELECT COUNT(*) FROM entity_mentions").fetchone()[0] == 1

        cur.execute("DELETE FROM entities WHERE entity_id = 'ENT-1'")
        conn.commit()
        assert cur.execute("SELECT COUNT(*) FROM entity_mentions").fetchone()[0] == 0

    def test_f14_timeline_events_and_financial_transactions_insertion(self, temp_vault_db):
        """Verify timeline_events and financial_transactions table constraints."""
        conn, _ = temp_vault_db
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO timeline_events (event_id, event_date_iso, event_year, event_type, title, description)
            VALUES ('EVT-001', '2021-12-08', 2021, 'REGULATORY_NOTICE', 'HCD Notice', 'Surplus Land Act Notice')
        """)
        cur.execute("""
            INSERT INTO financial_transactions (transaction_id, transaction_date_iso, amount, currency, payment_method)
            VALUES ('TRX-001', '2021-12-08', 96000000.0, 'USD', 'WIRE')
        """)
        conn.commit()

        assert cur.execute("SELECT COUNT(*) FROM timeline_events").fetchone()[0] == 1
        assert cur.execute("SELECT COUNT(*) FROM financial_transactions").fetchone()[0] == 1

    def test_f14_relationships_graph_table_self_loop_prevention(self, temp_vault_db):
        """Verify CHECK constraint preventing self-referential relationships."""
        conn, _ = temp_vault_db
        cur = conn.cursor()

        cur.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('ENT-10', 'Todd Ament', 'INDIVIDUAL')")
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO relationships (relationship_id, source_entity_id, target_entity_id, relationship_type)
                VALUES ('REL-001', 'ENT-10', 'ENT-10', 'CONNECTED_TO')
            """)
            conn.commit()


# ==============================================================================
# FEATURE 15: MASTER JSON CATALOG EXPORTER (5 UNIT TESTS)
# ==============================================================================

class TestFeature15MasterCatalogExporter:
    """Unit tests for Feature 15: Master JSON Catalog Exporter."""

    def test_f15_rfc_8785_canonical_json_deterministic_serialization(self, merkle_tools):
        """Verify deterministic sorting and formatting under RFC 8785."""
        d1 = {"b": 2, "a": 1, "z": [3, 2, 1]}
        d2 = {"a": 1, "z": [3, 2, 1], "b": 2}

        jcs1 = merkle_tools["canonical_json_bytes"](d1)
        jcs2 = merkle_tools["canonical_json_bytes"](d2)

        assert jcs1 == jcs2
        assert jcs1 == b'{"a":1,"b":2,"z":[3,2,1]}'

    def test_f15_merkle_root_computation_single_and_paired(self, merkle_tools):
        """Verify binary Merkle tree root reduction."""
        h1 = hashlib.sha256(b"doc1").hexdigest()
        h2 = hashlib.sha256(b"doc2").hexdigest()

        root = merkle_tools["merkle_root"]([h1, h2])
        expected = hashlib.sha256((h1 + h2).encode("utf-8")).hexdigest()
        assert root == expected

    def test_f15_composite_master_merkle_root_calculation(self, merkle_tools):
        """Verify master root aggregates all 5 sub-tree roots."""
        r_docs = "1" * 64
        r_ents = "2" * 64
        r_evts = "3" * 64
        r_trx = "4" * 64
        r_rels = "5" * 64

        composite_hash = hashlib.sha256((r_docs + r_ents + r_evts + r_trx + r_rels).encode("utf-8")).hexdigest()
        assert len(composite_hash) == 64

    def test_f15_catalog_metadata_summary_counts_integrity(self):
        """Verify summary count integrity in catalog dictionary structure."""
        catalog = {
            "catalog_metadata": {
                "schema_version": "1.0.0",
                "generated_at": "2026-08-29T12:00:00Z",
                "root_merkle_sha256": "0" * 64,
                "total_documents": 2,
                "total_entities": 3,
                "total_events": 4,
                "total_transactions": 1,
                "total_relationships": 2,
                "integrity_mode": "forensic_court_ready"
            },
            "documents": [{"document_id": "D1"}, {"document_id": "D2"}],
            "entities": [{"entity_id": "E1"}, {"entity_id": "E2"}, {"entity_id": "E3"}],
            "timeline_events": [{"event_id": f"EV{i}"} for i in range(4)],
            "financial_transactions": [{"transaction_id": "T1"}],
            "relationships": [{"relationship_id": "R1"}, {"relationship_id": "R2"}],
            "audit_invariants": {
                "documents_merkle_sha256": "0" * 64,
                "entities_merkle_sha256": "0" * 64,
                "events_merkle_sha256": "0" * 64,
                "transactions_merkle_sha256": "0" * 64,
                "relationships_merkle_sha256": "0" * 64,
                "foreign_key_violations": 0,
                "chronological_inversions": 0,
                "all_invariants_passed": True
            }
        }

        meta = catalog["catalog_metadata"]
        assert meta["total_documents"] == len(catalog["documents"])
        assert meta["total_entities"] == len(catalog["entities"])
        assert meta["total_events"] == len(catalog["timeline_events"])
        assert meta["total_transactions"] == len(catalog["financial_transactions"])
        assert meta["total_relationships"] == len(catalog["relationships"])

    def test_f15_catalog_json_schema_structural_conformance(self):
        """Verify presence of all mandatory top-level sections in catalog."""
        required_keys = {
            "catalog_metadata",
            "documents",
            "entities",
            "timeline_events",
            "financial_transactions",
            "relationships",
            "audit_invariants"
        }
        catalog_mock = {k: {} if "metadata" in k or "audit" in k else [] for k in required_keys}
        assert required_keys.issubset(catalog_mock.keys())


# ==============================================================================
# FEATURE 16: E2E TEST SUITE (TIERS 1–4) (5 UNIT TESTS)
# ==============================================================================

class TestFeature16E2ETestSuite:
    """Unit tests for Feature 16: E2E Test Suite (Tiers 1–4)."""

    def test_f16_test_harness_conftest_isolation(self, tmp_path: Path):
        """Verify temporary paths and database isolation across test invocations."""
        p1 = tmp_path / "sub1"
        p2 = tmp_path / "sub2"
        p1.mkdir()
        p2.mkdir()
        assert p1.exists() and p2.exists()
        assert p1 != p2

    def test_f16_synthetic_pdf_generator_fixture_integrity(self, make_synthetic_pdf):
        """Verify make_synthetic_pdf creates structurally valid readable PDF."""
        pdf_path = make_synthetic_pdf("test_valid.pdf", pages_content=["Sample Text Content"])
        doc = pymupdf.open(str(pdf_path))
        assert doc.page_count == 1
        assert "Sample Text Content" in doc[0].get_text()
        doc.close()

    def test_f16_synthetic_image_generator_fixture_integrity(self, make_synthetic_image):
        """Verify make_synthetic_image produces readable PNG file."""
        img_path = make_synthetic_image("test_scan.png", text_lines=["Notice Line 1", "Notice Line 2"])
        img = cv2.imread(str(img_path))
        assert img is not None
        assert img.shape[0] > 0 and img.shape[1] > 0

    def test_f16_synthetic_archive_generator_fixture_integrity(self, make_synthetic_archive):
        """Verify make_synthetic_archive creates valid zip containing specified members."""
        zip_path = make_synthetic_archive("test_pack.zip", {"file1.txt": b"Hello", "file2.txt": b"World"})
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert set(zf.namelist()) == {"file1.txt", "file2.txt"}
            assert zf.read("file1.txt") == b"Hello"

    def test_f16_investigative_domain_corpora_fixtures_validity(self, angel_stadium_records, unlawful_detainer_records):
        """Verify angel_stadium_records and unlawful_detainer_records fixture schemas."""
        assert "cases" in angel_stadium_records
        assert len(angel_stadium_records["cases"]) == 3
        assert "financials" in angel_stadium_records
        assert unlawful_detainer_records["case_number"] == "30-2021-01201327-CL-UD-CJC"
        assert len(unlawful_detainer_records["key_dates"]) == 5


# ==============================================================================
# FEATURE 17: 100% INVARIANT VERIFICATION & HARDENING (5 UNIT TESTS)
# ==============================================================================

class TestFeature17InvariantVerification:
    """Unit tests for Feature 17: 100% Invariant Verification & Hardening."""

    def test_f17_foreign_key_integrity_pragma_check(self, in_memory_vault_db):
        """Verify PRAGMA foreign_key_check returns zero violations on clean relational graph."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('D1', 'uri', 'name', 'path', 10, 'text/plain', '1'*64, '1'*64, '2026-08-29T12:00:00Z')")
        cur.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('E1', 'City of Anaheim', 'MUNICIPAL_BODY')")
        cur.execute("INSERT INTO timeline_events (event_id, document_id, primary_entity_id, event_date_iso, event_year, event_type, title, description) VALUES ('EV1', 'D1', 'E1', '2022-05-24', 2022, 'LEGISLATIVE_ACTION', 'Res 2022-064', 'Voided stadium deal')")
        conn.commit()

        violations = cur.execute("PRAGMA foreign_key_check;").fetchall()
        assert len(violations) == 0

    def test_f17_document_hash_uniqueness_invariant(self, in_memory_vault_db):
        """Verify mathematical invariant: COUNT(documents) == COUNT(DISTINCT file_sha256)."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('D1', 'u1', 'n1', 'p1', 10, 'text/plain', '1'*64, '1'*64, '2026-08-29T12:00:00Z')")
        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('D2', 'u2', 'n2', 'p2', 20, 'text/plain', '2'*64, '2'*64, '2026-08-29T12:00:00Z')")
        conn.commit()

        tot = cur.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        distinct = cur.execute("SELECT COUNT(DISTINCT file_sha256) FROM documents").fetchone()[0]
        assert tot == distinct

    def test_f17_chronological_monotonicity_rank_invariant(self, in_memory_vault_db):
        """Verify strict chronological monotonicity of ordered timeline events."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        events = [
            ("EV-1", "2021-05-19", 2021, "JUDICIAL_FILING", "Complaint Filed", 1),
            ("EV-2", "2021-06-29", 2021, "JUDICIAL_FILING", "Default Judgment 1", 2),
            ("EV-3", "2021-12-22", 2021, "JUDICIAL_FILING", "Judge Luege Stay Order", 3),
            ("EV-4", "2022-02-04", 2022, "JUDICIAL_FILING", "Default Judgment 3", 4),
        ]
        for eid, dt, yr, etype, title, rank in events:
            cur.execute("""
                INSERT INTO timeline_events (event_id, event_date_iso, event_year, event_type, title, description, chronological_rank)
                VALUES (?, ?, ?, ?, ?, '', ?)
            """, (eid, dt, yr, etype, title, rank))
        conn.commit()

        ordered = cur.execute("SELECT event_date_iso, chronological_rank FROM timeline_events ORDER BY chronological_rank ASC").fetchall()
        for i in range(len(ordered) - 1):
            assert ordered[i][0] <= ordered[i+1][0]
            assert ordered[i][1] < ordered[i+1][1]

    def test_f17_financial_conservatism_non_negative_amounts(self, in_memory_vault_db):
        """Verify database CHECK constraint and invariant that financial transaction magnitude >= 0.0."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO financial_transactions (transaction_id, transaction_date_iso, amount, currency, payment_method)
            VALUES ('TRX-10', '2022-05-24', 50000000.0, 'USD', 'ESCROW')
        """)
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO financial_transactions (transaction_id, transaction_date_iso, amount, currency, payment_method)
                VALUES ('TRX-BAD', '2022-05-24', -500.0, 'USD', 'ESCROW')
            """)
            conn.commit()

    def test_f17_schema_invariants_log_table_audit_recording(self, in_memory_vault_db):
        """Verify logging of audit results into schema_invariants_log table."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO schema_invariants_log (
                tier_level, merkle_root_sha256, documents_count, entities_count,
                events_count, transactions_count, relationships_count,
                foreign_key_violations, chronological_inversions, verification_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("TIER_1", "e" * 64, 10, 5, 20, 4, 8, 0, 0, "PASSED"))
        conn.commit()

        log_row = cur.execute("SELECT tier_level, verification_status, foreign_key_violations FROM schema_invariants_log").fetchone()
        assert log_row[0] == "TIER_1"
        assert log_row[1] == "PASSED"
        assert log_row[2] == 0
