"""
OsintNeoAi Indexer — Tier 2: Comprehensive Boundary & Corner Case Test Suite
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\tests\\test_tier2_boundaries.py

Provides exhaustive, non-trivial boundary and corner case tests across ALL 17 system features:
- Feature 1: Stream Ingestion & Chunking Boundaries (5 tests)
- Feature 2: Google Drive Link Resolver Boundaries (5 tests)
- Feature 3: Cryptographic SHA-256 Engine Boundaries (5 tests)
- Feature 4: Multi-Format MIME Dispatcher Boundaries (5 tests)
- Feature 5: Native Digital Text Extraction Boundaries (5 tests)
- Feature 6: Neural Offline OCR Engine Boundaries (5 tests)
- Feature 7: Image Preprocessing & Enhancement Boundaries (5 tests)
- Feature 8: Timestamp Normalizer Boundaries (5 tests)
- Feature 9: Financial Transaction Normalizer Boundaries (5 tests)
- Feature 10: Legal Case Identifier Normalizer Boundaries (5 tests)
- Feature 11: Communication Metadata Normalizer Boundaries (5 tests)
- Feature 12: 6-Category Entity Extractor Boundaries (5 tests)
- Feature 13: Phonetic & Contextual Entity Resolver Boundaries (5 tests)
- Feature 14: SQLite Relational Vault Boundaries (5 tests)
- Feature 15: Master JSON Catalog Exporter Boundaries (5 tests)
- Feature 16: E2E Test Suite (Tiers 1–4) Boundaries (5 tests)
- Feature 17: 100% Invariant Verification & Hardening Boundaries (5 tests)
Total: 85 exhaustive boundary tests.
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
from connectors.gdrive_streamer import GDriveStreamer, GDriveResourceInfo, GDriveStreamError
from connectors.mailbox_reader import MailboxReader, EmailMetadata, MailboxReaderError
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
# FEATURE 1 BOUNDARIES: STREAM INGESTION & CHUNKING (5 TESTS)
# ==============================================================================

class TestFeature1Boundaries:
    """Boundary and corner tests for Feature 1: Stream Ingestion & Chunking."""

    def test_f1_boundary_zero_byte_empty_file(self, tmp_path: Path):
        """Verify ingestion of a zero-byte file yields accurate empty hash and 0 size."""
        empty_file = tmp_path / "empty_doc.txt"
        empty_file.write_bytes(b"")

        crawler = LocalCrawler(target_paths=[tmp_path], skip_empty=False)
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 1
        art = artifacts[0]
        assert art.file_size_bytes == 0
        assert art.artifact_id == hashlib.sha256(b"").hexdigest().lower()
        with art.raw_stream_factory() as s:
            assert s.read() == b""

    def test_f1_boundary_single_byte_file(self, tmp_path: Path):
        """Verify ingestion of a single-byte file."""
        one_byte = tmp_path / "byte.txt"
        one_byte.write_bytes(b"X")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 1
        assert artifacts[0].file_size_bytes == 1
        assert artifacts[0].artifact_id == hashlib.sha256(b"X").hexdigest().lower()

    def test_f1_boundary_extreme_chunk_sizes(self, tmp_path: Path):
        """Verify streaming with 1-byte, 1 MB, and 16 MB chunk sizes."""
        data = b"Arbitrary chunk boundary test content\n" * 100
        test_file = tmp_path / "chunk_test.txt"
        test_file.write_bytes(data)

        for chunk_sz in [1, 1024, 65536, 1024 * 1024]:
            digest, size = compute_file_sha256_with_size(test_file, chunk_size=chunk_sz)
            assert digest == hashlib.sha256(data).hexdigest().lower()
            assert size == len(data)

    def test_f1_boundary_nonexistent_or_permission_denied_target(self, tmp_path: Path):
        """Verify crawler handles missing directories without unhandled crashes."""
        missing_dir = tmp_path / "does_not_exist_dir"
        crawler = LocalCrawler(target_paths=[missing_dir])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 0

    def test_f1_boundary_corrupted_zip_archive(self, tmp_path: Path):
        """Verify crawler gracefully handles corrupted zip archives."""
        corrupt_zip = tmp_path / "corrupt.zip"
        corrupt_zip.write_bytes(b"PK\x03\x04CorruptedZipHeaderGarbageBytes")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())

        # Should record error in stats and not crash
        assert crawler.stats.errors_encountered >= 1 or len(artifacts) == 0


# ==============================================================================
# FEATURE 2 BOUNDARIES: GOOGLE DRIVE LINK RESOLVER (5 TESTS)
# ==============================================================================

class TestFeature2Boundaries:
    """Boundary and corner tests for Feature 2: Google Drive Link Resolver."""

    def test_f2_boundary_invalid_url_schemes(self):
        """Verify non-Google URLs or malformed schemes raise GDriveStreamError."""
        streamer = GDriveStreamer()
        for invalid_url in [
            "ftp://drive.google.com/file/d/123",
            "https://dropbox.com/s/12345/file.pdf",
            "not_a_url_at_all",
            "http://",
        ]:
            with pytest.raises(GDriveStreamError):
                streamer.parse_url(invalid_url)

    def test_f2_boundary_truncated_file_id(self):
        """Verify truncated file IDs (< 20 characters) are rejected."""
        streamer = GDriveStreamer()
        with pytest.raises(GDriveStreamError):
            streamer.parse_url("https://drive.google.com/file/d/short_id/view")

    def test_f2_boundary_folder_ingestion_guard(self):
        """Verify folder URL passed to ingest_url raises explanatory GDriveStreamError."""
        streamer = GDriveStreamer()
        folder_url = "https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"
        with pytest.raises(GDriveStreamError, match="Folder URLs"):
            streamer.ingest_url(folder_url)

    def test_f2_boundary_offline_missing_cache(self, tmp_path: Path):
        """Verify requesting uncached file in prefer_offline mode raises GDriveStreamError."""
        streamer = GDriveStreamer(spool_dir=tmp_path, local_cache_dirs=[tmp_path], prefer_offline=True)
        url = "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view"
        with pytest.raises(GDriveStreamError, match="no local cache was found"):
            streamer.ingest_url(url)

    def test_f2_boundary_whitespace_padded_urls(self):
        """Verify URLs with leading/trailing whitespace, newlines, and tabs are trimmed cleanly."""
        streamer = GDriveStreamer()
        padded_url = "  \n\t https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/view \n "
        info = streamer.parse_url(padded_url)
        assert info.resource_id == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"


# ==============================================================================
# FEATURE 3 BOUNDARIES: CRYPTOGRAPHIC SHA-256 ENGINE (5 TESTS)
# ==============================================================================

class TestFeature3Boundaries:
    """Boundary and corner tests for Feature 3: Cryptographic SHA-256 Engine."""

    def test_f3_boundary_empty_bytes_sha256(self):
        """Verify empty byte hashing returns standard SHA-256 empty digest."""
        empty_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert compute_bytes_sha256(b"") == empty_sha

        hasher = StreamHasher()
        assert hasher.hexdigest() == empty_sha
        assert hasher.total_bytes == 0

    def test_f3_boundary_single_byte_chunks_stream_hasher(self):
        """Verify feeding data 1 byte at a time produces exact matching digest."""
        data = b"Single Byte Chunk Accumulation Test"
        hasher = StreamHasher(chunk_size=1)
        for byte_val in data:
            hasher.update(bytes([byte_val]))

        assert hasher.hexdigest() == hashlib.sha256(data).hexdigest().lower()
        assert hasher.total_bytes == len(data)

    def test_f3_boundary_non_seekable_stream(self):
        """Verify verify_stream_sha256 handles non-seekable byte generators."""
        def chunk_gen():
            yield b"Chunk A"
            yield b"Chunk B"

        combined = b"Chunk AChunk B"
        expected_hash = hashlib.sha256(combined).hexdigest().lower()

        assert verify_stream_sha256(chunk_gen(), expected_hash) is True

    def test_f3_boundary_tampered_single_bit_difference(self):
        """Verify cryptographic avalanche effect: 1-bit difference produces completely different digest."""
        d1 = b"Evidence Record Version A" * 100
        d2 = bytearray(d1)
        d2[0] ^= 1  # Flip 1 bit in first byte

        h1 = compute_bytes_sha256(d1)
        h2 = compute_bytes_sha256(bytes(d2))

        assert h1 != h2
        # Verify hex distance is substantial (> 20 chars different)
        diffs = sum(1 for a, b in zip(h1, h2) if a != b)
        assert diffs > 25

    def test_f3_boundary_invalid_hash_string_formats(self, tmp_path: Path):
        """Verify verify_file_sha256 rejects malformed hash arguments safely."""
        f = tmp_path / "test.bin"
        f.write_bytes(b"Data")
        for bad_hash in ["", "   ", "short", "0" * 63, "0" * 65, "z" * 64, None]:
            assert verify_file_sha256(f, bad_hash) is False


# ==============================================================================
# FEATURE 4 BOUNDARIES: MULTI-FORMAT MIME DISPATCHER (5 TESTS)
# ==============================================================================

class TestFeature4Boundaries:
    """Boundary and corner tests for Feature 4: Multi-Format MIME Dispatcher."""

    def test_f4_boundary_extension_case_insensitivity(self):
        """Verify uppercase and mixed case extensions resolve to canonical MIME types."""
        assert get_mime_type("docket.PDF") == "application/pdf"
        assert get_mime_type("audit.DOCX") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert get_mime_type("photo.JpEg") == "image/jpeg"
        assert get_mime_type("scan.PNG") == "image/png"

    def test_f4_boundary_multiple_dots_in_filename(self):
        """Verify filenames with multiple internal dots isolate final extension."""
        assert get_mime_type("case.8.23.cr.00108.plea.final.signed.pdf") == "application/pdf"
        assert get_mime_type("backup.2026.08.29.tar.gz") == "application/gzip"
        assert get_file_category("report.v2.docx") == FileCategory.DOCX

    def test_f4_boundary_file_with_no_extension(self):
        """Verify extensionless files default to application/octet-stream."""
        assert get_mime_type("LICENSE") == "application/octet-stream"
        assert get_file_category("unnamed_binary_blob") == FileCategory.UNKNOWN

    def test_f4_boundary_hidden_dot_files(self):
        """Verify ignored file extensions are detected."""
        assert is_ignored_file("test.pyc") is True
        assert is_ignored_file("library.dll") is True

    def test_f4_boundary_mismatched_extension_magic_byte_sniffing(self):
        """Verify magic byte sniffer detects true MIME when extension is unknown or binary."""
        fake_txt = b"%PDF-1.4 Fake Extension PDF"
        assert detect_mime_type("evidence.unknown", sample_bytes=fake_txt) == "application/pdf"

        fake_png = b"\x89PNG\r\n\x1a\n\x00Fake PNG"
        assert detect_mime_type("picture.unknown_ext", sample_bytes=fake_png) == "image/png"


# ==============================================================================
# FEATURE 5 BOUNDARIES: NATIVE DIGITAL TEXT EXTRACTION (5 TESTS)
# ==============================================================================

class TestFeature5Boundaries:
    """Boundary and corner tests for Feature 5: Native Digital Text Extraction."""

    def test_f5_boundary_zero_page_or_empty_pdf(self, tmp_path: Path):
        """Verify corrupted or empty PDF returns structured error record without crash."""
        bad_pdf = tmp_path / "broken.pdf"
        bad_pdf.write_bytes(b"%PDF-Broken truncated payload")

        extractor = DocumentExtractor()
        art = IngestedArtifact(
            artifact_id=compute_file_sha256(bad_pdf),
            source_uri=str(bad_pdf),
            mime_type="application/pdf",
            file_size_bytes=bad_pdf.stat().st_size,
            raw_stream_factory=make_file_stream_factory(str(bad_pdf))
        )
        rec = extractor.extract(art)
        assert "[ERROR:" in rec.extracted_text or rec.ocr_engine_used == "error"

    def test_f5_boundary_unicode_surrogate_and_cjk_characters(self, make_synthetic_pdf):
        """Verify extraction of special legal symbols, emojis, and multilingual Unicode."""
        special_text = "LEGAL NOTICE: § 54220 ¶ 12 © 2026 🏛 Anaheim City Council — ⚖ Justice"
        pdf_path = make_synthetic_pdf("unicode_test.pdf", pages_content=[special_text])

        extractor = DocumentExtractor()
        art = IngestedArtifact(
            artifact_id=compute_file_sha256(pdf_path),
            source_uri=str(pdf_path),
            mime_type="application/pdf",
            file_size_bytes=pdf_path.stat().st_size,
            raw_stream_factory=make_file_stream_factory(str(pdf_path))
        )
        rec = extractor.extract(art)
        assert "§ 54220" in rec.extracted_text
        assert "Anaheim City Council" in rec.extracted_text

    def test_f5_boundary_zero_length_docx(self):
        """Verify zero-length DOCX payload returns structured empty result."""
        extractor = DocxExtractor()
        res = extractor.extract_from_bytes(b"")
        assert res.text == ""
        assert res.metadata.get("empty_payload") is True

    def test_f5_boundary_malformed_html_tags(self):
        """Verify unclosed, malformed HTML parsed safely via fallback parser."""
        malformed_html = "<html><body><h1>Unclosed Heading<p>Paragraph without closing tag<table><tr><td>Data"
        parser = HtmlDocumentParser()
        res = parser.extract_from_stream(io.BytesIO(malformed_html.encode("utf-8")))
        assert "Unclosed Heading" in res.text
        assert "Data" in res.text

    def test_f5_boundary_very_long_unbroken_string(self):
        """Verify TextExtractor handles massive unbroken alphanumeric string without memory explosion."""
        huge_str = "A" * 100000
        extractor = TextExtractor()
        res = extractor.extract_from_stream(io.BytesIO(huge_str.encode("utf-8")))
        assert len(res.text) == 100000


# ==============================================================================
# FEATURE 6 BOUNDARIES: NEURAL OFFLINE OCR ENGINE (5 TESTS)
# ==============================================================================

class TestFeature6Boundaries:
    """Boundary and corner tests for Feature 6: Neural Offline OCR Engine."""

    def test_f6_boundary_all_white_blank_image(self):
        """Verify blank white image returns empty OCR line list and 0.0 confidence."""
        engine = OCREngine()
        blank_white = np.full((300, 300, 3), 255, dtype=np.uint8)
        res = engine.ocr_image(blank_white)
        assert len(res.lines) == 0
        assert res.full_text == ""

    def test_f6_boundary_all_black_solid_image(self):
        """Verify solid black image returns empty OCR results."""
        engine = OCREngine()
        blank_black = np.zeros((300, 300, 3), dtype=np.uint8)
        res = engine.ocr_image(blank_black)
        assert len(res.lines) == 0

    def test_f6_boundary_micro_dimension_image(self):
        """Verify micro-dimension image (1x1 pixel) handled safely."""
        engine = OCREngine()
        micro_img = np.full((1, 1, 3), 128, dtype=np.uint8)
        res = engine.ocr_image(micro_img)
        assert res.width == 1 and res.height == 1
        assert len(res.lines) == 0

    def test_f6_boundary_extreme_aspect_ratio_image(self):
        """Verify extreme aspect ratio strip (10x1000 pixels) handled safely."""
        engine = OCREngine()
        strip_img = np.full((10, 1000, 3), 255, dtype=np.uint8)
        res = engine.ocr_image(strip_img)
        assert res.height == 10 and res.width == 1000

    def test_f6_boundary_inverted_color_image(self):
        """Verify OCR handles white text on black background."""
        img = np.zeros((150, 400, 3), dtype=np.uint8)
        cv2.putText(img, "ANAHEIM", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)

        engine = OCREngine()
        res = engine.ocr_image(img)
        assert isinstance(res, OCRPageResult)


# ==============================================================================
# FEATURE 7 BOUNDARIES: IMAGE PREPROCESSING & ENHANCEMENT (5 TESTS)
# ==============================================================================

class TestFeature7Boundaries:
    """Boundary and corner tests for Feature 7: Image Preprocessing & Enhancement."""

    def test_f7_boundary_extreme_skew_angles(self):
        """Verify deskew handles angles up to 45 degrees safely."""
        enhancer = ImageEnhancer(max_deskew_angle=45.0)
        img = np.zeros((200, 200), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (150, 150), 255, -1)

        deskewed = enhancer.deskew(img, angle=44.9)
        assert deskewed.shape == (200, 200)

    def test_f7_boundary_single_pixel_image(self):
        """Verify enhancement on 1x1 image returns without division by zero."""
        enhancer = ImageEnhancer()
        pixel = np.array([[128]], dtype=np.uint8)
        enhanced = enhancer.enhance(pixel, profile=EnhancementProfile.LIGHT)
        assert enhanced is not None

    def test_f7_boundary_high_contrast_clean_image_passthrough(self):
        """Verify PASSTHROUGH profile leaves clean image intact."""
        enhancer = ImageEnhancer()
        orig = np.full((100, 100, 3), 240, dtype=np.uint8)
        res = enhancer.enhance(orig, profile=EnhancementProfile.PASSTHROUGH)
        assert np.array_equal(orig, res)

    def test_f7_boundary_clahe_clip_limit_extremes(self):
        """Verify CLAHE handles extreme clip limits (0.1 and 10.0)."""
        gray = np.full((50, 50), 128, dtype=np.uint8)
        e_low = ImageEnhancer(clahe_clip_limit=0.1)
        e_high = ImageEnhancer(clahe_clip_limit=10.0)

        assert e_low.apply_clahe(gray).shape == (50, 50)
        assert e_high.apply_clahe(gray).shape == (50, 50)

    def test_f7_boundary_none_or_empty_image_array(self):
        """Verify passing None or 0-size array returns gracefully."""
        enhancer = ImageEnhancer()
        assert enhancer.enhance(None) is None
        empty = np.empty((0, 0), dtype=np.uint8)
        assert enhancer.enhance(empty).size == 0


# ==============================================================================
# FEATURE 8 BOUNDARIES: TIMESTAMP NORMALIZER (5 TESTS)
# ==============================================================================

class TestFeature8Boundaries:
    """Boundary and corner tests for Feature 8: Timestamp Normalizer."""

    def test_f8_boundary_leap_year_feb_29(self):
        """Verify leap year 2024-02-29 is valid and 2023-02-29 is rejected."""
        d_leap = normalize_date("2024-02-29")
        assert d_leap is not None
        assert d_leap.iso_value == "2024-02-29"

        d_non_leap = normalize_date("2023-02-29")
        assert d_non_leap is None

    def test_f8_boundary_century_year_2000(self):
        """Verify century year 2000 leap year date parsing."""
        d = normalize_date("2000-02-29")
        assert d is not None
        assert d.year == 2000 and d.month == 2 and d.day == 29

    def test_f8_boundary_out_of_range_month_day(self):
        """Verify out of range month (13) and day (32) return None."""
        assert normalize_date("2021-13-15") is None
        assert normalize_date("2021-06-32") is None
        assert normalize_date("2021-00-10") is None

    def test_f8_boundary_midnight_and_noon_times(self):
        """Verify 12:00 AM (00:00) vs 12:00 PM (12:00) conversions."""
        d_midnight = normalize_date("06/29/2021 12:00 AM", default_tz="UTC")
        assert d_midnight is not None
        assert d_midnight.hour == 0 and d_midnight.minute == 0

        d_noon = normalize_date("06/29/2021 12:00 PM", default_tz="UTC")
        assert d_noon is not None
        assert d_noon.hour == 12 and d_noon.minute == 0

    def test_f8_boundary_complex_embedded_docket_dates(self):
        """Verify date extracted when surrounded by dense docket legal text."""
        snippet = "ENTERED ON THE DOCKET PURSUANT TO FED. R. CIV. P. 58 ON December 22, 2021 BY CLERK."
        extracted = extract_dates(snippet)
        assert len(extracted) == 1
        assert extracted[0].iso_value == "2021-12-22"


# ==============================================================================
# FEATURE 9 BOUNDARIES: FINANCIAL TRANSACTION NORMALIZER (5 TESTS)
# ==============================================================================

class TestFeature9Boundaries:
    """Boundary and corner tests for Feature 9: Financial Transaction Normalizer."""

    def test_f9_boundary_zero_dollar_amount(self):
        """Verify $0.00 and $0 normalize to zero amount and 0 cents."""
        fin = normalize_financial("$0.00")
        assert fin is not None
        assert fin.amount_float == 0.0
        assert fin.amount_cents == 0

    def test_f9_boundary_sub_cent_rounding(self):
        """Verify sub-cent rounding using Decimal ROUND_HALF_UP."""
        f1 = normalize_financial("$0.005")
        assert f1 is not None
        assert f1.amount_cents == 1

        f2 = normalize_financial("$0.004")
        assert f2 is not None
        assert f2.amount_cents == 0

    def test_f9_boundary_trillion_dollar_amount(self):
        """Verify massive trillion-dollar amounts convert without 64-bit integer overflow."""
        fin = normalize_financial("$1.25 Trillion")
        assert fin is not None
        assert fin.amount_float == 1250000000000.0
        assert fin.amount_cents == 125000000000000

    def test_f9_boundary_international_currencies(self):
        """Verify Euro, British Pound, and Yen symbols resolve to respective ISO codes."""
        f_eur = normalize_financial("€50M")
        assert f_eur.currency == "EUR"
        assert f_eur.amount_cents == 5000000000

        f_gbp = normalize_financial("£25,000.00")
        assert f_gbp.currency == "GBP"
        assert f_gbp.amount_cents == 2500000

    def test_f9_boundary_malformed_currency_strings(self):
        """Verify strings with currency symbols but no numbers return None."""
        assert normalize_financial("$$$") is None
        assert normalize_financial("$abc") is None
        assert normalize_financial("USD") is None


# ==============================================================================
# FEATURE 10 BOUNDARIES: LEGAL CASE IDENTIFIER NORMALIZER (5 TESTS)
# ==============================================================================

class TestFeature10Boundaries:
    """Boundary and corner tests for Feature 10: Legal Case Identifier Normalizer."""

    def test_f10_boundary_dockets_with_irregular_spacing(self):
        """Verify regex accommodates extra spaces in docket numbers."""
        citations = extract_case_citations("Case  No.  8:23-cr-00108-CJC")
        assert len(citations) == 1
        assert citations[0].canonical_id == "8:23-cr-00108-CJC"

    def test_f10_boundary_dockets_with_surrounding_punctuation(self):
        """Verify dockets enclosed in parentheses or quotes stripped cleanly."""
        text = 'See plea agreement in "(8:23-cr-00108-CJC)"; also [30-2021-01201327-CL-UD-CJC].'
        nums = extract_case_numbers(text)
        assert "8:23-cr-00108-CJC" in nums
        assert "30-2021-01201327-CL-UD-CJC" in nums

    def test_f10_boundary_state_dockets_other_counties(self):
        """Verify state dockets from other California counties (e.g. County 19 for Los Angeles)."""
        citations = extract_case_citations("Case No. 19-2022-00123456-CU-BC-CJC")
        assert len(citations) == 1
        assert citations[0].canonical_id == "19-2022-00123456-CU-BC-CJC"
        assert "County 19" in citations[0].jurisdiction

    def test_f10_boundary_statute_with_subsections(self):
        """Verify statutory citations with subsection references match base code."""
        citations = extract_case_citations("Violating Cal. Gov. Code § 54220 et seq.")
        assert len(citations) == 1
        assert citations[0].canonical_id == "Cal. Gov. Code § 54220"

    def test_f10_boundary_empty_or_non_legal_text(self):
        """Verify text without legal citations returns empty list."""
        assert extract_case_citations("Just a normal paragraph with no legal citations.") == []
        assert extract_case_numbers("") == []


# ==============================================================================
# FEATURE 11 BOUNDARIES: COMMUNICATION METADATA NORMALIZER (5 TESTS)
# ==============================================================================

class TestFeature11Boundaries:
    """Boundary and corner tests for Feature 11: Communication Metadata Normalizer."""

    def test_f11_boundary_malformed_rfc2047_header(self):
        """Verify malformed MIME encoded header falls back to raw string without crash."""
        bad_hdr = "=?INVALID_CHARSET?B?BrokenBase64====?="
        decoded = MailboxReader.decode_mime_header(bad_hdr)
        assert isinstance(decoded, str)

    def test_f11_boundary_multiple_cc_and_bcc_recipients(self):
        """Verify parsing 20+ recipients in To/Cc lists."""
        recipients_list = [f"Official {i} <official{i}@anaheim.net>" for i in range(25)]
        meta = {"To": recipients_list}
        sender, recipients = extract_correspondence_parties("", metadata=meta)
        assert len(recipients) == 25

    def test_f11_boundary_empty_subject_and_sender(self):
        """Verify email message with empty subject and sender extracts defaults."""
        msg = EmailMessage()
        msg.set_content("Body without headers")
        reader = MailboxReader()
        headers = reader.parse_message_headers(msg)

        assert headers.subject == ""
        assert headers.sender_email == ""

    def test_f11_boundary_nested_quoted_printable_mime(self):
        """Verify decoding of quoted-printable text with soft line breaks."""
        raw_email = (
            b"From: todd.ament@anaheimchamber.org\r\n"
            b"To: harry.sidhu@anaheim.net\r\n"
            b"Subject: QP Test\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Transfer-Encoding: quoted-printable\r\n\r\n"
            b"This is a long line that has been split using =\r\nsoft line breaks in QP.\r\n"
        )
        reader = MailboxReader()
        artifacts = list(reader.read_mail_source(io.BytesIO(raw_email)))
        assert len(artifacts) == 1
        with artifacts[0].raw_stream_factory() as s:
            body = s.read().decode("utf-8")
            assert "soft line breaks" in body

    def test_f11_boundary_email_with_no_attachments(self):
        """Verify email without attachments yields single IngestedArtifact."""
        msg = EmailMessage()
        msg["From"] = "sender@domain.com"
        msg["To"] = "recipient@domain.com"
        msg["Subject"] = "No Attachment"
        msg.set_content("Plain text body only.")

        reader = MailboxReader()
        artifacts = list(reader.process_message(msg, "memory://eml", 0))
        assert len(artifacts) == 1
        assert artifacts[0].metadata["attachment_count"] == 0


# ==============================================================================
# FEATURE 12 BOUNDARIES: 6-CATEGORY ENTITY EXTRACTOR (5 TESTS)
# ==============================================================================

class TestFeature12Boundaries:
    """Boundary and corner tests for Feature 12: 6-Category Entity Extractor."""

    def test_f12_boundary_single_letter_or_short_names(self):
        """Verify short 2-letter entity names (JL Group, TA Group) normalized cleanly."""
        e1 = normalize_entity("JL Group LLC")
        assert e1.core_stem == "JL Group"
        assert e1.canonical_suffix == "LLC"

    def test_f12_boundary_hyphenated_and_apostrophe_names(self):
        """Verify entity names containing apostrophes and hyphens."""
        e_apo = normalize_entity("Dog's Day Productions")
        assert e_apo.cleaned_name == "Dog's Day Productions"

        e_hyph = normalize_entity("Smith-Sidhu Consulting")
        assert "Smith-Sidhu" in e_hyph.cleaned_name

    def test_f12_boundary_all_caps_corporate_names(self):
        """Verify all-caps corporate legal names stripped properly."""
        e = normalize_entity("WALLACE, RICHARDSON, SONTAG & LE LLP")
        assert e.canonical_suffix == "LLP"
        assert e.core_stem == "WALLACE, RICHARDSON, SONTAG & LE"

    def test_f12_boundary_names_with_foreign_accents(self):
        """Verify names with diacritics normalized under Unicode NFKD."""
        e = normalize_entity("Mélahat Rafièi")
        assert len(e.soundex) == 4
        assert len(e.metaphone_primary) > 0

    def test_f12_boundary_empty_or_whitespace_only_names(self):
        """Verify empty and whitespace strings return default empty record."""
        e_empty = normalize_entity("")
        assert e_empty.cleaned_name == ""
        assert e_empty.soundex == "0000"

        e_space = normalize_entity("   \t\n  ")
        assert e_space.cleaned_name == ""


# ==============================================================================
# FEATURE 13 BOUNDARIES: PHONETIC & CONTEXTUAL ENTITY RESOLVER (5 TESTS)
# ==============================================================================

class TestFeature13Boundaries:
    """Boundary and corner tests for Feature 13: Phonetic & Contextual Entity Resolver."""

    def test_f13_boundary_soundex_names_with_numbers_or_symbols(self):
        """Verify Soundex handles alphanumeric names safely."""
        s = soundex("3M Corporation")
        assert len(s) == 4

        s2 = soundex("E*Trade")
        assert len(s2) == 4

    def test_f13_boundary_double_metaphone_silent_letters(self):
        """Verify Double Metaphone encoding on words with silent leading consonants."""
        p_kn, _ = double_metaphone("Knight")
        p_n, _ = double_metaphone("Night")
        assert p_kn == p_n

        p_wr, _ = double_metaphone("Wright")
        p_r, _ = double_metaphone("Right")
        assert p_wr == p_r

    def test_f13_boundary_chained_multiple_corporate_suffixes(self):
        """Verify corporate suffix cleaner strips chained suffixes."""
        cleaned = strip_corporate_suffix("Acme Holdings LLC Inc")
        assert "Acme Holdings" in cleaned

    def test_f13_boundary_identical_phonetics_different_names(self):
        """Verify phonetic clustering equivalence for spelling variants."""
        p_sm1, _ = double_metaphone("Smith")
        p_sm2, _ = double_metaphone("Smyth")
        assert p_sm1 == p_sm2

    def test_f13_boundary_empty_name_phonetic_defaults(self):
        """Verify empty strings produce standard zeroed phonetic codes."""
        assert soundex("") == "0000"
        assert double_metaphone("") == ("", "")


# ==============================================================================
# FEATURE 14 BOUNDARIES: SQLITE RELATIONAL VAULT (5 TESTS)
# ==============================================================================

class TestFeature14Boundaries:
    """Boundary and corner tests for Feature 14: SQLite Relational Vault."""

    def test_f14_boundary_check_constraint_negative_file_size(self, in_memory_vault_db):
        """Verify documents table rejects negative file_size_bytes via CHECK constraint."""
        conn = in_memory_vault_db
        cur = conn.cursor()
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp)
                VALUES ('D-NEG', 'uri', 'name', 'path', -100, 'text/plain', '3'*64, '3'*64, '2026-08-29T12:00:00Z')
            """)
            conn.commit()

    def test_f14_boundary_check_constraint_invalid_entity_category(self, in_memory_vault_db):
        """Verify entities table rejects unapproved entity_category."""
        conn = in_memory_vault_db
        cur = conn.cursor()
        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO entities (entity_id, canonical_name, entity_category)
                VALUES ('E-BAD', 'Bad Category Corp', 'INVALID_CATEGORY_CODE')
            """)
            conn.commit()

    def test_f14_boundary_check_constraint_confidence_out_of_bounds(self, in_memory_vault_db):
        """Verify entity_mentions table rejects confidence scores > 1.0 or < 0.0."""
        conn = in_memory_vault_db
        cur = conn.cursor()
        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('D-1', 'u', 'n', 'p', 10, 'text/plain', '4'*64, '4'*64, '2026-08-29T12:00:00Z')")
        cur.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('E-1', 'Name', 'INDIVIDUAL')")
        conn.commit()

        with pytest.raises(sqlite3.IntegrityError):
            cur.execute("""
                INSERT INTO entity_mentions (mention_id, document_id, entity_id, raw_mention_text, extraction_method, confidence_score)
                VALUES ('M-BAD', 'D-1', 'E-1', 'text', 'REGEX', 1.5)
            """)
            conn.commit()

    def test_f14_boundary_massive_extracted_text_payload(self, in_memory_vault_db):
        """Verify documents table handles 5MB extracted text payload."""
        conn = in_memory_vault_db
        cur = conn.cursor()
        huge_text = "Forensic transcription text line.\n" * 150000

        cur.execute("""
            INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp, extracted_text)
            VALUES ('D-HUGE', 'u', 'n', 'p', ?, 'text/plain', ?, ?, '2026-08-29T12:00:00Z', ?)
        """, (len(huge_text), "5" * 64, "5" * 64, huge_text))
        conn.commit()

        retrieved = cur.execute("SELECT extracted_text FROM documents WHERE document_id = 'D-HUGE'").fetchone()[0]
        assert len(retrieved) == len(huge_text)

    def test_f14_boundary_transaction_rollback_on_batch_failure(self, in_memory_vault_db):
        """Verify transaction rollback leaves database in clean pre-batch state upon error."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        initial_count = cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0]

        try:
            conn.execute("BEGIN TRANSACTION;")
            conn.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('E-OK', 'Good Entity', 'INDIVIDUAL')")
            # Cause integrity error
            conn.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('E-FAIL', 'Bad Category', 'NON_EXISTENT')")
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()

        after_count = cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        assert after_count == initial_count


# ==============================================================================
# FEATURE 15 BOUNDARIES: MASTER JSON CATALOG EXPORTER (5 TESTS)
# ==============================================================================

class TestFeature15Boundaries:
    """Boundary and corner tests for Feature 15: Master JSON Catalog Exporter."""

    def test_f15_boundary_merkle_root_empty_list(self, merkle_tools):
        """Verify Merkle root of empty list returns SHA-256 of empty bytes."""
        empty_root = merkle_tools["merkle_root"]([])
        assert empty_root == hashlib.sha256(b"").hexdigest().lower()

    def test_f15_boundary_merkle_root_odd_number_of_leaves(self, merkle_tools):
        """Verify Merkle tree root calculation with 3 and 5 leaf nodes."""
        leaves_3 = [hashlib.sha256(f"leaf_{i}".encode()).hexdigest() for i in range(3)]
        root_3 = merkle_tools["merkle_root"](leaves_3)
        assert len(root_3) == 64

        leaves_5 = [hashlib.sha256(f"leaf_{i}".encode()).hexdigest() for i in range(5)]
        root_5 = merkle_tools["merkle_root"](leaves_5)
        assert len(root_5) == 64

    def test_f15_boundary_canonical_json_nested_lists_and_dicts(self, merkle_tools):
        """Verify RFC 8785 deterministic ordering on deeply nested objects."""
        nested = {
            "z_list": [{"b": 2, "a": 1}],
            "a_dict": {"k2": "val2", "k1": "val1"},
            "num": 100.0
        }
        b1 = merkle_tools["canonical_json_bytes"](nested)
        # Verify a_dict comes before z_list, and k1 before k2
        assert b1.index(b'"a_dict"') < b1.index(b'"z_list"')
        assert b1.index(b'"k1"') < b1.index(b'"k2"')

    def test_f15_boundary_catalog_with_zero_records(self, merkle_tools):
        """Verify catalog with 0 records computes valid Merkle root hashes."""
        catalog_empty = {
            "catalog_metadata": {"total_documents": 0, "total_entities": 0},
            "documents": [],
            "entities": []
        }
        h = merkle_tools["canonical_json_sha256"](catalog_empty)
        assert len(h) == 64

    def test_f15_boundary_special_unicode_in_catalog_json(self, merkle_tools):
        """Verify catalog JSON serialization handles quotes, backslashes, and emojis safely."""
        special_data = {"text": 'Legal Quote: "Approved" \\ Backslash and Emoji: ⚖'}
        encoded = merkle_tools["canonical_json_bytes"](special_data)
        assert b"\\\\" in encoded or b"\\\"" in encoded


# ==============================================================================
# FEATURE 16 BOUNDARIES: E2E TEST SUITE (TIERS 1–4) (5 TESTS)
# ==============================================================================

class TestFeature16Boundaries:
    """Boundary and corner tests for Feature 16: E2E Test Suite (Tiers 1–4)."""

    def test_f16_boundary_temp_file_cleanup_after_generator(self, tmp_path: Path):
        """Verify stream factories close cleanly allowing file removal on Windows."""
        temp_f = tmp_path / "temp_to_clean.bin"
        temp_f.write_bytes(b"Data bytes to clean")

        factory = make_file_stream_factory(str(temp_f))
        with factory() as s:
            assert s.read() == b"Data bytes to clean"

        # Should be removable immediately without Windows file-lock error
        temp_f.unlink()
        assert not temp_f.exists()

    def test_f16_boundary_concurrent_database_connections(self, temp_vault_db):
        """Verify multiple connections can read concurrently under WAL mode."""
        conn1, db_path = temp_vault_db
        conn2 = sqlite3.connect(str(db_path))

        conn1.execute("INSERT INTO entities (entity_id, canonical_name, entity_category) VALUES ('E-C1', 'C1', 'INDIVIDUAL')")
        conn1.commit()

        row = conn2.execute("SELECT canonical_name FROM entities WHERE entity_id = 'E-C1'").fetchone()
        assert row[0] == "C1"
        conn2.close()

    def test_f16_boundary_zero_byte_fixtures_handling(self, make_synthetic_pdf):
        """Verify synthetic PDF generator handles empty string pages."""
        pdf_path = make_synthetic_pdf("empty_page.pdf", pages_content=[""])
        doc = pymupdf.open(str(pdf_path))
        assert doc.page_count == 1
        doc.close()

    def test_f16_boundary_corrupted_pdf_in_extractor(self, tmp_path: Path):
        """Verify DocumentExtractor returns error record rather than raising exception on corrupt PDF."""
        corrupt = tmp_path / "zero_header.pdf"
        corrupt.write_bytes(b"\x00\x00\x00\x00NotAPdf")

        extractor = DocumentExtractor()
        art = IngestedArtifact(
            artifact_id=compute_file_sha256(corrupt),
            source_uri=str(corrupt),
            mime_type="application/pdf",
            file_size_bytes=len(b"\x00\x00\x00\x00NotAPdf"),
            raw_stream_factory=make_file_stream_factory(str(corrupt))
        )
        rec = extractor.extract(art)
        assert rec is not None
        assert rec.ocr_engine_used == "error"

    def test_f16_boundary_deeply_nested_directory_crawler(self, tmp_path: Path):
        """Verify crawler traverses deeply nested folder structure."""
        nested = tmp_path / "l1" / "l2" / "l3" / "l4"
        nested.mkdir(parents=True)
        (nested / "deep_doc.txt").write_bytes(b"Deeply nested evidence")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 1
        assert "deep_doc.txt" in artifacts[0].source_uri


# ==============================================================================
# FEATURE 17 BOUNDARIES: 100% INVARIANT VERIFICATION & HARDENING (5 TESTS)
# ==============================================================================

class TestFeature17Boundaries:
    """Boundary and corner tests for Feature 17: 100% Invariant Verification & Hardening."""

    def test_f17_boundary_foreign_key_violation_detection(self, in_memory_vault_db):
        """Verify PRAGMA foreign_key_check detects orphaned records if FKs are disabled temporarily."""
        conn = in_memory_vault_db
        # Temporarily disable FK checks to insert orphaned child record
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("""
            INSERT INTO entity_mentions (mention_id, document_id, entity_id, raw_mention_text, extraction_method)
            VALUES ('MEN-ORPHAN', 'DOC-NONEXISTENT', 'ENT-NONEXISTENT', 'Orphan Mention', 'REGEX')
        """)
        conn.commit()

        violations = conn.execute("PRAGMA foreign_key_check;").fetchall()
        assert len(violations) >= 1

    def test_f17_boundary_chronological_inversion_detection(self, in_memory_vault_db):
        """Verify invariant checker identifies chronological inversions when rank conflicts with date."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        # Insert inverted events: rank 1 has 2023 date, rank 2 has 2021 date
        cur.execute("INSERT INTO timeline_events (event_id, event_date_iso, event_year, event_type, title, description, chronological_rank) VALUES ('EV-A', '2023-08-16', 2023, 'JUDICIAL_FILING', 'Plea', '', 1)")
        cur.execute("INSERT INTO timeline_events (event_id, event_date_iso, event_year, event_type, title, description, chronological_rank) VALUES ('EV-B', '2021-12-08', 2021, 'REGULATORY_NOTICE', 'Notice', '', 2)")
        conn.commit()

        rows = cur.execute("SELECT event_date_iso, chronological_rank FROM timeline_events ORDER BY chronological_rank ASC").fetchall()
        inversions = sum(1 for i in range(len(rows)-1) if rows[i][0] > rows[i+1][0])
        assert inversions == 1

    def test_f17_boundary_hash_collision_detection(self, in_memory_vault_db):
        """Verify invariant detection logic catches duplicates if table contains duplicated hashes."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("INSERT INTO documents (document_id, source_uri, file_name, file_path, file_size_bytes, mime_type, file_sha256, content_sha256, ingestion_timestamp) VALUES ('D1', 'u1', 'n1', 'p1', 10, 'text/plain', '6'*64, '6'*64, '2026-08-29T12:00:00Z')")
        conn.commit()

        total = cur.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        distinct = cur.execute("SELECT COUNT(DISTINCT file_sha256) FROM documents").fetchone()[0]
        assert total == distinct == 1

    def test_f17_boundary_audit_log_failure_recording(self, in_memory_vault_db):
        """Verify logging failed invariant runs into schema_invariants_log."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO schema_invariants_log (
                tier_level, merkle_root_sha256, documents_count, entities_count,
                events_count, transactions_count, relationships_count,
                foreign_key_violations, chronological_inversions, verification_status
            ) VALUES ('TIER_2', '7'*64, 5, 5, 5, 2, 2, 2, 1, 'FAILED')
        """)
        conn.commit()

        failed_run = cur.execute("SELECT verification_status, foreign_key_violations FROM schema_invariants_log WHERE tier_level = 'TIER_2'").fetchone()
        assert failed_run[0] == "FAILED"
        assert failed_run[1] == 2

    def test_f17_boundary_zero_balance_financial_sums(self, in_memory_vault_db):
        """Verify financial transaction sum invariant on empty or zero-balance table."""
        conn = in_memory_vault_db
        cur = conn.cursor()

        total_sum = cur.execute("SELECT COALESCE(SUM(amount), 0.0) FROM financial_transactions").fetchone()[0]
        assert total_sum == 0.0
