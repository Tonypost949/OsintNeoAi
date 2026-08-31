"""
Adversarial Stress and Boundary Test Suite for OsintNeoAi Indexer (M1)
Evaluates storage/hasher.py and connectors/local_crawler.py under hostile edge cases.
"""

from __future__ import annotations

import gc
import gzip
import hashlib
import io
import os
import shutil
import sys
import tarfile
import tempfile
import tracemalloc
import zipfile
from pathlib import Path
from typing import BinaryIO, Generator, List, Tuple

import pytest

from workspaces.osintneoai_indexer.config import CHUNK_SIZE, MAX_RAM_MB
from workspaces.osintneoai_indexer.storage.hasher import (
    DEFAULT_CHUNK_SIZE,
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
    CrawlStats,
    IngestedArtifact,
    LocalCrawler,
    ManagedTarStream,
    ManagedZipStream,
    crawl_local_files,
    detect_mime_type,
)


# ============================================================================
# 1. EMPIRICAL HASHER FIDELITY TESTS
# ============================================================================

class TestHasherAdversarialFidelity:
    """Stress-tests SHA-256 calculation against ground-truth hashlib across boundaries."""

    @pytest.mark.parametrize("size", [
        0, 1, 2, 63, 64, 65, 1023, 1024, 1025,
        65535, 65536, 65537,  # Exact 64 KB boundaries
        131071, 131072, 131073,  # 128 KB boundaries
        1000000, 5242880  # 1 MB, 5 MB
    ])
    def test_sha256_byte_fidelity_stream_and_bytes(self, size: int):
        """Verifies byte-for-byte fidelity against hashlib.sha256 for exact boundary sizes."""
        # Generate pseudo-random deterministic bytes
        data = bytes((i * 37 + 13) % 256 for i in range(size))
        expected_hash = hashlib.sha256(data).hexdigest().lower()

        # 1. compute_bytes_sha256
        assert compute_bytes_sha256(data) == expected_hash

        # 2. compute_stream_sha256_with_size
        stream = io.BytesIO(data)
        actual_hash, total_bytes = compute_stream_sha256_with_size(stream, chunk_size=65536)
        assert actual_hash == expected_hash
        assert total_bytes == size

        # 3. StreamHasher incremental
        hasher = StreamHasher(chunk_size=65536)
        hasher.update(data)
        assert hasher.hexdigest() == expected_hash
        assert hasher.total_bytes == size

    @pytest.mark.parametrize("custom_chunk", [1, 7, 13, 1024, 65535, 65536, 65537, 1000000])
    def test_sha256_arbitrary_chunk_sizes(self, custom_chunk: int):
        """Verifies SHA-256 is invariant to arbitrary chunk sizes."""
        data = b"ADVERSARIAL_PAYLOAD_" * 10000  # ~200 KB
        expected_hash = hashlib.sha256(data).hexdigest().lower()

        actual_hash, total_bytes = compute_stream_sha256_with_size(
            io.BytesIO(data), chunk_size=custom_chunk
        )
        assert actual_hash == expected_hash
        assert total_bytes == len(data)

    def test_sha256_generator_variable_chunks(self):
        """Verifies hasher accepts generators yielding arbitrary and empty chunks."""
        chunks = [
            b"Hello",
            b"",
            b" ",
            b"World",
            b"",
            b"!" * 50000,
            b"",
            b"FinalChunk",
        ]
        full_data = b"".join(chunks)
        expected_hash = hashlib.sha256(full_data).hexdigest().lower()

        def chunk_gen():
            for c in chunks:
                yield c

        actual_hash, total_bytes = compute_stream_sha256_with_size(chunk_gen())
        assert actual_hash == expected_hash
        assert total_bytes == len(full_data)

    def test_non_seekable_stream(self):
        """Verifies hasher works on non-seekable streams without raising errors."""
        class NonSeekableStream:
            def __init__(self, data: bytes):
                self._stream = io.BytesIO(data)

            def read(self, size: int = -1) -> bytes:
                return self._stream.read(size)

            def seekable(self) -> bool:
                return False

        data = b"Non-seekable stream verification payload 123456789"
        expected_hash = hashlib.sha256(data).hexdigest().lower()

        stream = NonSeekableStream(data)
        actual_hash, total_bytes = compute_stream_sha256_with_size(
            stream, rewind_if_seekable=True
        )
        assert actual_hash == expected_hash
        assert total_bytes == len(data)

    def test_hashing_reader_readinto_and_small_reads(self):
        """Verifies HashingReader when reading byte-by-byte and via readinto buffer."""
        data = b"HashingReader byte-by-byte adversarial validation" * 500
        expected_hash = hashlib.sha256(data).hexdigest().lower()

        # Test byte-by-byte read()
        reader = HashingReader(io.BytesIO(data))
        collected = []
        while True:
            b = reader.read(1)
            if not b:
                break
            collected.append(b)
        assert b"".join(collected) == data
        assert reader.hexdigest == expected_hash
        assert reader.total_bytes == len(data)

        # Test readinto() with custom buffer
        reader2 = HashingReader(io.BytesIO(data))
        buf = bytearray(17)
        collected2 = bytearray()
        while True:
            n = reader2.readinto(buf)
            if not n or n == 0:
                break
            collected2.extend(buf[:n])
        assert bytes(collected2) == data
        assert reader2.hexdigest == expected_hash
        assert reader2.total_bytes == len(data)

    def test_hasher_reset_and_reuse(self):
        """Verifies StreamHasher can be reset and reused cleanly."""
        hasher = StreamHasher()
        hasher.update(b"Initial data payload")
        first_hash = hasher.hexdigest()
        assert first_hash == hashlib.sha256(b"Initial data payload").hexdigest()

        hasher.reset()
        assert hasher.total_bytes == 0
        assert hasher.chunk_count == 0
        assert hasher.hexdigest() == hashlib.sha256(b"").hexdigest()

        hasher.update(b"Second data payload")
        second_hash = hasher.hexdigest()
        assert second_hash == hashlib.sha256(b"Second data payload").hexdigest()

    def test_verify_hash_edge_cases(self, tmp_path: Path):
        """Verifies constant-time verification with uppercase, whitespace, invalid formats."""
        test_file = tmp_path / "verify_test.txt"
        test_file.write_bytes(b"Verifiable content 12345")
        correct_hash = hashlib.sha256(b"Verifiable content 12345").hexdigest()

        # Exact match
        assert verify_file_sha256(test_file, correct_hash) is True
        # Uppercase match
        assert verify_file_sha256(test_file, correct_hash.upper()) is True
        # Match with surrounding whitespace
        assert verify_file_sha256(test_file, f"  {correct_hash}  ") is True
        # Corrupted hash (1 character off)
        corrupted = "0" + correct_hash[1:]
        assert verify_file_sha256(test_file, corrupted) is False
        # Invalid length
        assert verify_file_sha256(test_file, "abcd") is False
        assert verify_file_sha256(test_file, "") is False
        # Nonexistent file
        assert verify_file_sha256(tmp_path / "nonexistent.file", correct_hash) is False


# ============================================================================
# 2. CORRUPTED & MALFORMED ARCHIVES ADVERSARIAL TESTS
# ============================================================================

class TestCorruptedArchiveHandling:
    """Stress-tests crawler resilience against malformed, truncated, and corrupt archives."""

    def test_truncated_zip(self, tmp_path: Path):
        """Verifies crawler gracefully handles truncated zip files without crashing."""
        good_zip = tmp_path / "temp.zip"
        with zipfile.ZipFile(good_zip, "w") as zf:
            zf.writestr("valid_doc.pdf", b"%PDF-1.4 header and sample data")
            zf.writestr("valid_doc2.txt", b"Plain text evidence")

        # Read zip bytes and truncate by 50%
        zip_bytes = good_zip.read_bytes()
        truncated_zip = tmp_path / "corrupted_truncated.zip"
        truncated_zip.write_bytes(zip_bytes[: len(zip_bytes) // 2])

        # Crawl
        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        # The crawler should not crash and record the error
        assert crawler.stats.errors_encountered >= 1

    def test_corrupted_zip_magic_bytes_with_garbage(self, tmp_path: Path):
        """Verifies crawler handles zip file starting with PK header followed by garbage."""
        bad_zip = tmp_path / "garbage_pk.zip"
        bad_zip.write_bytes(b"PK\x03\x04" + b"\xff\xfe\x00\x01" * 200)

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert crawler.stats.errors_encountered >= 1

    def test_corrupted_tar_archive(self, tmp_path: Path):
        """Verifies crawler handles malformed and truncated tar archives."""
        bad_tar = tmp_path / "corrupted.tar"
        bad_tar.write_bytes(b"USTAR\x00\x00" + b"\xde\xad\xbe\xef" * 100)

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert crawler.stats.errors_encountered >= 1

    def test_corrupted_gzip_stream(self, tmp_path: Path):
        """Verifies crawler handles malformed gzip files."""
        bad_gz = tmp_path / "broken_evidence.txt.gz"
        bad_gz.write_bytes(b"\x1f\x8b\x08\x00" + b"CorruptedDeflateGarbageBytes" * 20)

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert crawler.stats.errors_encountered >= 1

    def test_zero_byte_archive(self, tmp_path: Path):
        """Verifies crawler handles 0-byte zip/tar/gz files."""
        (tmp_path / "empty.zip").write_bytes(b"")
        (tmp_path / "empty.tar").write_bytes(b"")
        (tmp_path / "empty.gz").write_bytes(b"")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        # Should record errors or skip without uncaught exception
        assert crawler.stats.errors_encountered >= 1 or len(artifacts) == 0

    def test_zip_with_path_traversal_and_macosx_metadata(self, tmp_path: Path):
        """Verifies crawler skips path traversal (../) and Mac OS metadata entries."""
        zip_path = tmp_path / "security_test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("legit_evidence.pdf", b"%PDF-1.4 legit data")
            zf.writestr("../traversal_attempt.txt", b"evil traversal payload")
            zf.writestr("/root_traversal.txt", b"evil root payload")
            zf.writestr("__MACOSX/._legit_evidence.pdf", b"mac os resource fork")
            zf.writestr("subdir/._hidden.txt", b"hidden mac metadata")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        names = [a.source_uri for a in artifacts]

        # Only legit_evidence.pdf should be yielded
        assert any("legit_evidence.pdf" in n for n in names)
        assert not any("traversal_attempt" in n for n in names)
        assert not any("root_traversal" in n for n in names)
        assert not any("__MACOSX" in n for n in names)
        assert not any("._hidden" in n for n in names)


# ============================================================================
# 3. SPECIAL CHARACTERS & DEEP NESTING TESTS
# ============================================================================

class TestSpecialFilenamesAndNesting:
    """Stress-tests unicode, emojis, punctuation, and recursive archive structures."""

    def test_unicode_and_special_character_filenames(self, tmp_path: Path):
        """Verifies crawler correctly processes international characters and emojis."""
        special_names = [
            "документ_отчет_2026.pdf",
            "财务报告_Evidence_公开.docx",
            "証拠_データ_重要.txt",
            "München_Überweisung_Rechnung.eml",
            "report (confidential) [v2.0] + final & approved #1.txt",
            "📁_financial_leak_🔥_2026.json",
        ]
        created_files = []
        for name in special_names:
            p = tmp_path / name
            content = f"Content for {name}".encode("utf-8")
            p.write_bytes(content)
            created_files.append((p, content))

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == len(special_names)

        # Verify hash and content for each
        for artifact in artifacts:
            matched = False
            for p, content in created_files:
                if str(p.resolve()) == artifact.source_uri:
                    expected_hash = hashlib.sha256(content).hexdigest().lower()
                    assert artifact.artifact_id == expected_hash
                    # Verify stream factory returns identical bytes
                    with artifact.raw_stream_factory() as s:
                        assert s.read() == content
                    matched = True
                    break
            assert matched is True

    def test_zip_with_special_character_members(self, tmp_path: Path):
        """Verifies zip archives containing members with spaces, unicode, hashes."""
        zip_path = tmp_path / "unicode_archive.zip"
        members = {
            "отчет_ноябрь.pdf": b"%PDF-1.4 Russian text",
            "folder with spaces/financial report #42 [final].txt": b"Evidence data with hash",
            "🌟_star_data_🌟.json": b'{"key": "value"}',
        }
        with zipfile.ZipFile(zip_path, "w") as zf:
            for mname, mdata in members.items():
                zf.writestr(mname, mdata)

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == len(members)

        for artifact in artifacts:
            # Check stream factory reading
            with artifact.raw_stream_factory() as s:
                streamed = s.read()
                expected_hash = hashlib.sha256(streamed).hexdigest().lower()
                assert artifact.artifact_id == expected_hash


# ============================================================================
# 4. LARGE STREAM & MEMORY INVARIANCE STRESS HARNESS (< 250 MB)
# ============================================================================

class TestLargeStreamMemoryStress:
    """Empirical verification that memory consumption stays strictly < 250 MB under heavy load."""

    def test_large_multimegabyte_stream_hasher_memory(self):
        """Stream 50 MB synthetic data through StreamHasher and verify O(1) RAM."""
        tracemalloc.start()
        tracemalloc.reset_peak()

        gc.collect()
        initial_mem = tracemalloc.get_traced_memory()[0]

        # Generator producing 50 MB in 64 KB chunks without holding whole buffer in memory
        chunk_size = 64 * 1024
        total_chunks = 800  # 800 * 64KB = 50 MB (52,428,800 bytes)
        sample_chunk = b"X" * chunk_size

        hasher_ground_truth = hashlib.sha256()

        def stream_gen():
            for _ in range(total_chunks):
                hasher_ground_truth.update(sample_chunk)
                yield sample_chunk

        actual_hash, total_bytes = compute_stream_sha256_with_size(stream_gen(), chunk_size=chunk_size)
        expected_hash = hasher_ground_truth.hexdigest().lower()

        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_mem / (1024 * 1024)
        print(f"\n[STRESS TEST] 50 MB Stream Ingestion Peak Memory: {peak_mb:.2f} MB")

        assert actual_hash == expected_hash
        assert total_bytes == total_chunks * chunk_size
        # Memory should be well under 5 MB for streaming, definitely < 250 MB
        assert peak_mb < 25.0

    def test_large_file_crawler_memory_and_fidelity(self, tmp_path: Path):
        """Crawl directory with multiple large files (totalling 60 MB) and verify memory < 250 MB."""
        tracemalloc.start()
        tracemalloc.reset_peak()

        # Create 3 x 20 MB files
        chunk_20mb = b"OsintNeoAi_Forensic_Evidence_Block_Data_2026\n" * 450000  # ~20 MB
        expected_hashes = {}
        for i in range(3):
            fpath = tmp_path / f"large_evidence_{i}.txt"
            fpath.write_bytes(chunk_20mb)
            expected_hashes[str(fpath.resolve())] = hashlib.sha256(chunk_20mb).hexdigest().lower()

        crawler = LocalCrawler(target_paths=[tmp_path], chunk_size=65536)
        artifacts = list(crawler.crawl())

        assert len(artifacts) == 3
        for artifact in artifacts:
            assert artifact.artifact_id == expected_hashes[artifact.source_uri]
            assert artifact.file_size_bytes == len(chunk_20mb)

        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        peak_mb = peak_mem / (1024 * 1024)
        print(f"\n[STRESS TEST] 60 MB Multi-File Crawler Peak Memory: {peak_mb:.2f} MB")
        assert peak_mb < 50.0  # Far below the 250 MB ceiling requirement!


# ============================================================================
# 5. WINDOWS LOCK RELEASE VERIFICATION
# ============================================================================

class TestWindowsLockRelease:
    """Verifies that all files and archives are cleanly closed and unlinked on Windows."""

    def test_zip_stream_factory_closes_and_allows_unlink(self, tmp_path: Path):
        """Ensure opening and reading via raw_stream_factory does not lock zip file."""
        zip_path = tmp_path / "deletable.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", b"Some data")
            zf.writestr("file2.pdf", b"%PDF-1.4")

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 2

        # Read streams
        for artifact in artifacts:
            with artifact.raw_stream_factory() as stream:
                data = stream.read()
                assert len(data) > 0

        # Now attempt to remove the zip file immediately — should not raise PermissionError
        zip_path.unlink()
        assert not zip_path.exists()

    def test_tar_stream_factory_closes_and_allows_unlink(self, tmp_path: Path):
        """Ensure opening and reading via raw_stream_factory does not lock tar file."""
        tar_path = tmp_path / "deletable.tar"
        with tarfile.open(tar_path, "w") as tf:
            data = b"Sample tar member data"
            ti = tarfile.TarInfo("sample.txt")
            ti.size = len(data)
            tf.addfile(ti, io.BytesIO(data))

        crawler = LocalCrawler(target_paths=[tmp_path])
        artifacts = list(crawler.crawl())
        assert len(artifacts) == 1

        with artifacts[0].raw_stream_factory() as stream:
            read_data = stream.read()
            assert read_data == b"Sample tar member data"

        # Attempt to unlink
        tar_path.unlink()
        assert not tar_path.exists()
