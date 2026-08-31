"""
Adversarial Stress Test Suite for Milestone 1 Ingestion & Streaming Engine (Refined)
Path: C:\\OsintNeoAi\\.agents\\reviewer_m1_2\\test_adversarial_m1.py
"""

import email
import gc
import gzip
import hashlib
import io
import os
import tarfile
import tempfile
import tracemalloc
import zipfile
from email.message import EmailMessage
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from workspaces.osintneoai_indexer.config import (
    CHUNK_SIZE,
    EXTENSION_MAPPINGS,
    FileCategory,
    IndexerConfig,
    get_file_category,
    get_mime_type,
    is_ignored_file,
    is_supported_file,
)
from workspaces.osintneoai_indexer.storage.hasher import (
    HashingReader,
    StreamHasher,
    compute_bytes_sha256,
    compute_file_sha256,
    compute_file_sha256_with_size,
    compute_stream_sha256,
    compute_stream_sha256_with_size,
    verify_file_sha256,
    verify_stream_sha256,
)
from workspaces.osintneoai_indexer.connectors.local_crawler import (
    LocalCrawler,
    ManagedTarStream,
    ManagedZipStream,
    crawl_local_files,
    detect_mime_type,
)
from workspaces.osintneoai_indexer.connectors.gdrive_streamer import (
    GDriveResourceInfo,
    GDriveStreamError,
    GDriveStreamer,
)
from workspaces.osintneoai_indexer.connectors.mailbox_reader import (
    MailboxReader,
    MailboxReaderError,
)


class TestAdversarialWindowsLocks:
    """Stress tests Windows file locking on archives during edge cases."""

    def test_concurrent_managed_zip_readers_and_unlinking(self, tmp_path):
        zip_path = tmp_path / "concurrent.zip"
        content1 = b"Member 1 data" * 100
        content2 = b"Member 2 data" * 200
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("m1.txt", content1)
            zf.writestr("m2.txt", content2)

        crawler = LocalCrawler(target_paths=[zip_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 2

        # Open both streams concurrently
        s1 = artifacts[0].raw_stream_factory()
        s2 = artifacts[1].raw_stream_factory()

        assert len(s1.read(50)) == 50
        assert len(s2.read(50)) == 50

        s1.close()
        s2.close()

        # Unlink should succeed on Windows when all streams are closed
        zip_path.unlink()
        assert not zip_path.exists()

    def test_managed_tar_symlink_and_directory_skip(self, tmp_path):
        tar_path = tmp_path / "special_members.tar"
        with tarfile.open(tar_path, "w") as tf:
            # Add directory
            dir_info = tarfile.TarInfo("subdir/")
            dir_info.type = tarfile.DIRTYPE
            tf.addfile(dir_info)

            # Add regular file
            file_info = tarfile.TarInfo("subdir/file.txt")
            file_data = b"Regular file payload"
            file_info.size = len(file_data)
            tf.addfile(file_info, io.BytesIO(file_data))

        crawler = LocalCrawler(target_paths=[tar_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 1
        assert "subdir/file.txt" in artifacts[0].source_uri
        with artifacts[0].raw_stream_factory() as s:
            assert s.read() == b"Regular file payload"

        tar_path.unlink()
        assert not tar_path.exists()

    def test_zip_stream_context_manager_exception_cleanup(self, tmp_path):
        zip_path = tmp_path / "exc_test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("data.txt", b"Some text payload for investigation")

        crawler = LocalCrawler(target_paths=[zip_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 1

        try:
            with artifacts[0].raw_stream_factory() as stream:
                stream.read(5)
                raise RuntimeError("Simulated mid-stream failure")
        except RuntimeError:
            pass

        # Verify file is unlocked and can be unlinked
        zip_path.unlink()
        assert not zip_path.exists()


class TestAdversarialMemoryBounds:
    """Stress tests memory bounds with 25 MB+ stream payloads."""

    def test_large_stream_memory_invariance_under_hasher_and_hashing_reader(self, tmp_path):
        tracemalloc.start()

        large_file = tmp_path / "large_25mb.bin"
        chunk_64k = b"Z" * 65536
        total_chunks = 400  # 400 * 64 KB = 25.6 MB

        with open(large_file, "wb") as f:
            for _ in range(total_chunks):
                f.write(chunk_64k)

        # 1. Test StreamHasher
        with open(large_file, "rb") as f:
            h, sz = compute_stream_sha256_with_size(f, chunk_size=65536)
        assert sz == 25600 * 1024

        # 2. Test HashingReader with buffer iteration
        with open(large_file, "rb") as raw:
            with HashingReader(raw) as reader:
                buf = bytearray(65536)
                read_total = 0
                while True:
                    n = reader.readinto(buf)
                    if n == 0:
                        break
                    read_total += n
                assert read_total == sz
                assert reader.hexdigest == h

        current_ram, peak_ram = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_ram / (1024 * 1024)
        assert peak_mb < 20.0, f"Memory footprint exceeded: {peak_mb:.2f} MB"


class TestAdversarialMIMEDetection:
    """Stress tests MIME sniffing and category mapping edge cases."""

    def test_magic_byte_sniffing_for_extensionless_and_misnamed_files(self):
        # PDF magic bytes
        assert detect_mime_type("unknown_blob", sample_bytes=b"%PDF-1.7 header") == "application/pdf"
        # PNG magic bytes
        assert detect_mime_type("image_no_ext", sample_bytes=b"\x89PNG\r\n\x1a\n\x00\x00") == "image/png"
        # JPEG magic bytes
        assert detect_mime_type("photo", sample_bytes=b"\xff\xd8\xff\xe0\x00\x10JFIF") == "image/jpeg"
        # TIFF little endian
        assert detect_mime_type("scan_doc", sample_bytes=b"II*\x00\x08\x00") == "image/tiff"
        # ZIP magic bytes
        assert detect_mime_type("archive_blob", sample_bytes=b"PK\x03\x04\x14\x00") == "application/zip"
        # GZIP magic bytes
        assert detect_mime_type("compressed_data", sample_bytes=b"\x1f\x8b\x08\x00") == "application/gzip"
        # Plain text fallback
        assert detect_mime_type("notes", sample_bytes=b"Plain UTF-8 text contents") == "text/plain"

    def test_composite_extensions(self):
        assert detect_mime_type("data.tar.gz") == "application/gzip"
        assert detect_mime_type("data.tar.bz2") == "application/x-bzip-compressed-tar"
        assert detect_mime_type("data.tar.xz") == "application/x-xz-compressed-tar"
        assert detect_mime_type("records.jsonl") == "application/x-ndjson"
        assert detect_mime_type("records.ndjson") == "application/x-ndjson"


class TestAdversarialGDriveConnector:
    """Stress tests GDrive streamer URL patterns, queries, and offline fallbacks."""

    def test_complex_url_patterns_with_query_params(self):
        streamer = GDriveStreamer()

        # Doc with multiple params and export format
        u1 = "https://docs.google.com/document/d/1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7/edit?usp=sharing&format=txt&foo=bar"
        info1 = streamer.parse_url(u1)
        assert info1.resource_id == "1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7"
        assert info1.resource_type == "doc"
        assert info1.export_format == "txt"
        assert info1.inferred_mime_type == "text/plain"

        # Sheet with export format xlsx
        u2 = "https://docs.google.com/spreadsheets/d/1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7/edit?format=xlsx"
        info2 = streamer.parse_url(u2)
        assert info2.resource_type == "sheet"
        assert info2.export_format == "xlsx"
        assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in info2.inferred_mime_type

        # File URL with trailing slashes and view?usp=drivesdk
        u3 = "https://drive.google.com/file/d/1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7/view/?usp=drivesdk"
        info3 = streamer.parse_url(u3)
        assert info3.resource_id == "1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7"
        assert info3.resource_type == "file"

    def test_offline_failure_when_no_cache_exists(self, tmp_path):
        empty_dir = tmp_path / "empty_cache"
        empty_dir.mkdir()
        streamer = GDriveStreamer(local_cache_dirs=[empty_dir], prefer_offline=True)

        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.get.side_effect = ConnectionError("Network unreachable in offline mode")
            mock_session_cls.return_value = mock_session

            with pytest.raises(GDriveStreamError, match="Failed to stream Google Drive resource"):
                streamer.ingest_url("1AcgqV5AOt2nl6njJLFn3HAcE-Z_5kPb7")


class TestAdversarialMailboxConnector:
    """Stress tests mailbox parsing with malformed headers, nested structures, and charsets."""

    def test_deeply_nested_multipart_message(self, tmp_path):
        # Create multipart/mixed containing multipart/alternative containing text/plain + text/html, and an attachment
        msg = EmailMessage()
        msg["From"] = "investigator@doj.gov"
        msg["To"] = "agent@fbi.gov"
        msg["Subject"] = "Nested Multipart Case Analysis"
        msg["Date"] = "Mon, 15 Aug 2022 12:00:00 +0000"
        msg["Message-ID"] = "<nested-001@doj.gov>"

        msg.set_content("Plain text body version")
        msg.add_alternative("<p>HTML body version</p>", subtype="html")
        msg.add_attachment(b"%PDF-1.4 Evidence Document", maintype="application", subtype="pdf", filename="evidence.pdf")

        eml_file = tmp_path / "nested.eml"
        with open(eml_file, "wb") as f:
            f.write(msg.as_bytes())

        reader = MailboxReader()
        artifacts = list(reader.read_eml_file(eml_file))

        assert len(artifacts) == 2  # 1 email body + 1 attachment
        body_art = artifacts[0]
        att_art = artifacts[1]

        assert body_art.mime_type == "message/rfc822"
        assert body_art.metadata["has_html"] is True
        assert att_art.mime_type == "application/pdf"
        assert att_art.metadata["filename"] == "evidence.pdf"

    def test_broken_charset_and_missing_headers(self, tmp_path):
        raw_eml = (
            b"From: =?unknown-charset?Q?Broken_Name?= <test@example.com>\n"
            b"Subject: =?invalid-enc?B?%%%broken???==\n"
            b"Date: Invalid Date String\n"
            b"\n"
            b"Raw message body without headers.\n"
        )
        eml_file = tmp_path / "broken.eml"
        eml_file.write_bytes(raw_eml)

        reader = MailboxReader()
        artifacts = list(reader.read_eml_file(eml_file))

        assert len(artifacts) == 1
        art = artifacts[0]
        assert art.mime_type == "message/rfc822"
        assert art.metadata["normalized_date"] is None
        with art.raw_stream_factory() as s:
            assert b"Raw message body" in s.read()
