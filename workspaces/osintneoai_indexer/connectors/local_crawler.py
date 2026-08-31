"""
OsintNeoAi Indexer — Local Archive & Directory Crawler
Module: workspaces.osintneoai_indexer.connectors.local_crawler
Milestone: M1 (Ingestion & Streaming Engine)

Lazy generator traversing local target directories, handling standard evidentiary
files and compressed archive streams (ZIP, TAR, GZ) with O(1) memory invariance.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import logging
import mimetypes
import os
import sys
import tarfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    BinaryIO,
    Callable,
    Dict,
    Generator,
    Iterable,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
    Any,
)

logger = logging.getLogger("osintneoai.connectors.crawler")

# ==============================================================================
# 1. Interface Contracts & Data Models (PROJECT.md M1 ↔ M2)
# ==============================================================================

@dataclass(frozen=True)
class IngestedArtifact:
    """
    Canonical immutable container for ingested evidence artifacts.
    """
    artifact_id: str             # Canonical lowercase SHA-256 hex string (64 chars)
    source_uri: str              # File path or archive URI (e.g. zip://path#member)
    mime_type: str               # Normalized MIME type (e.g. application/pdf)
    file_size_bytes: int         # Exact uncompressed size in bytes
    raw_stream_factory: Callable[[], BinaryIO] # Factory returning fresh BinaryIO stream
    metadata: Optional[Dict[str, Any]] = None  # Optional contextual metadata


@dataclass
class CrawlStats:
    """
    Telemetry and accounting for crawler execution.
    """
    total_files_scanned: int = 0
    evidentiary_artifacts_yielded: int = 0
    archive_members_extracted: int = 0
    archives_processed: int = 0
    skipped_binaries: int = 0
    skipped_directories: int = 0
    errors_encountered: int = 0
    total_bytes_streamed: int = 0


# ==============================================================================
# 2. Forensic Extension & MIME Mapping Tables
# ==============================================================================

FORENSIC_MIME_MAP: Dict[str, str] = {
    # Documents & Legal Records
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
    
    # Scanned Images & Visual Intelligence
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".jpe": "image/jpeg",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    
    # Text, Markdown, Notes & Logs
    ".txt": "text/plain",
    ".text": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".log": "text/plain",
    ".nfo": "text/plain",
    ".ini": "text/plain",
    ".conf": "text/plain",
    ".cfg": "text/plain",
    
    # Web & Structured Data
    ".html": "text/html",
    ".htm": "text/html",
    ".xhtml": "application/xhtml+xml",
    ".xml": "application/xml",
    ".json": "application/json",
    ".jsonl": "application/x-ndjson",
    ".ndjson": "application/x-ndjson",
    ".csv": "text/csv",
    ".tsv": "text/tab-separated-values",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    
    # Spreadsheets
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".xls": "application/vnd.ms-excel",
    ".ods": "application/vnd.oasis.opendocument.spreadsheet",
    
    # Email & Communications
    ".eml": "message/rfc822",
    ".msg": "application/vnd.ms-outlook",
    ".mbox": "application/mbox",
    
    # Compressed Archives
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".tgz": "application/gzip",
    ".tar.gz": "application/gzip",
    ".tar.bz2": "application/x-bzip-compressed-tar",
    ".tbz2": "application/x-bzip-compressed-tar",
    ".tar.xz": "application/x-xz-compressed-tar",
    ".txz": "application/x-xz-compressed-tar",
    ".7z": "application/x-7z-compressed",
    ".rar": "application/vnd.rar",
}

EVIDENTIARY_EXTENSIONS: Set[str] = set(FORENSIC_MIME_MAP.keys())

ARCHIVE_EXTENSIONS: Set[str] = {
    ".zip", ".tar", ".gz", ".tgz", ".tar.gz",
    ".tar.bz2", ".tbz2", ".tar.xz", ".txz"
}

DEFAULT_EXCLUDED_EXTENSIONS: Set[str] = {
    # Executables & Binaries
    ".exe", ".dll", ".so", ".dylib", ".sys", ".drv", ".ocx",
    ".msi", ".msp", ".iso", ".img", ".dmg", ".pkg", ".deb", ".rpm",
    # Bytecode & Object Files
    ".pyc", ".pyo", ".pyd", ".class", ".jar", ".war", ".ear",
    ".rpyc", ".rpymc", ".o", ".obj", ".lib", ".a", ".pdb", ".idb",
    ".whl", ".egg", ".node", ".bin", ".rom", ".vmdk", ".qcow2",
    # Web / Style / Font Assets
    ".ttf", ".otf", ".woff", ".woff2", ".eot", ".cur", ".ico",
    ".css", ".scss", ".sass", ".less", ".map",
    # Temporary / Cache / Incomplete
    ".tmp", ".temp", ".bak", ".swp", ".swo", ".ds_store",
    "thumbs.db", "desktop.ini", ".crdownload", ".download", ".part",
}

DEFAULT_EXCLUDED_DIRS: Set[str] = {
    ".git", ".svn", ".hg", ".venv", "venv", "env", ".env",
    "node_modules", "__pycache__", ".pytest_cache", ".agents",
    "appdata", "windows", "$recycle.bin", "system volume information",
    ".idea", ".vscode", ".mypy_cache", ".ruff_cache", "build", "dist",
    "temp", "tmp"
}

DEFAULT_TARGET_PATHS: List[str] = [
    r"C:\Users\Amd949609\Downloads",
    r"C:\OsintNeoAi\evidence",
]


# ==============================================================================
# 3. Stream Wrappers & Resource Managers
# ==============================================================================

class ManagedZipStream(io.RawIOBase):
    """
    A binary stream wrapper around a zip member (ZipExtFile) that guarantees
    both the member stream and parent ZipFile are closed on exit.
    """
    def __init__(self, zip_path: str, member_name: str):
        super().__init__()
        self.zip_path = zip_path
        self.member_name = member_name
        self._zf: Optional[zipfile.ZipFile] = zipfile.ZipFile(zip_path, "r")
        try:
            self._stream = self._zf.open(member_name, "r")
        except Exception:
            self._zf.close()
            self._zf = None
            raise
        self._closed = False

    def readable(self) -> bool:
        return not self._closed

    def seekable(self) -> bool:
        return not self._closed and hasattr(self._stream, "seekable") and self._stream.seekable()

    def read(self, size: int = -1) -> bytes:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.read(size)

    def readinto(self, b) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        data = self._stream.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.seek(offset, whence)

    def tell(self) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.tell()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                if self._stream is not None:
                    self._stream.close()
            finally:
                if self._zf is not None:
                    self._zf.close()
                    self._zf = None
                    self._stream = None
        super().close()

    def __enter__(self) -> ManagedZipStream:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False


class ManagedTarStream(io.RawIOBase):
    """
    A binary stream wrapper around a tar member that guarantees both the member
    stream and parent TarFile are closed on exit.
    """
    def __init__(self, tar_path: str, member_name: str):
        super().__init__()
        self.tar_path = tar_path
        self.member_name = member_name
        self._tf: Optional[tarfile.TarFile] = tarfile.open(tar_path, "r:*")
        try:
            member = self._tf.getmember(member_name)
            extracted = self._tf.extractfile(member)
            if extracted is None:
                raise ValueError(f"Tar member '{member_name}' is not a regular file")
            self._stream = extracted
        except Exception:
            self._tf.close()
            self._tf = None
            raise
        self._closed = False

    def readable(self) -> bool:
        return not self._closed

    def seekable(self) -> bool:
        return not self._closed and hasattr(self._stream, "seekable") and self._stream.seekable()

    def read(self, size: int = -1) -> bytes:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.read(size)

    def readinto(self, b) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        data = self._stream.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.seek(offset, whence)

    def tell(self) -> int:
        if self._closed or self._stream is None:
            raise ValueError("I/O operation on closed stream")
        return self._stream.tell()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                if self._stream is not None:
                    self._stream.close()
            finally:
                if self._tf is not None:
                    self._tf.close()
                    self._tf = None
                    self._stream = None
        super().close()

    def __enter__(self) -> ManagedTarStream:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False


# ==============================================================================
# 4. Stream Factory Builders & Hash Utilities
# ==============================================================================

def make_file_stream_factory(file_path: str) -> Callable[[], BinaryIO]:
    """Returns a factory that opens a fresh binary file stream."""
    return lambda: open(file_path, "rb")


def make_zip_stream_factory(zip_path: str, member_name: str) -> Callable[[], BinaryIO]:
    """Returns a factory that creates a ManagedZipStream for a zip entry."""
    return lambda: ManagedZipStream(zip_path, member_name)


def make_tar_stream_factory(tar_path: str, member_name: str) -> Callable[[], BinaryIO]:
    """Returns a factory that creates a ManagedTarStream for a tar entry."""
    return lambda: ManagedTarStream(tar_path, member_name)


def make_gzip_stream_factory(gz_path: str) -> Callable[[], BinaryIO]:
    """Returns a factory that creates an open gzip reader stream."""
    return lambda: gzip.open(gz_path, "rb")


def compute_stream_sha256(stream: BinaryIO, chunk_size: int = 65536) -> Tuple[str, int]:
    """
    Computes canonical lowercase SHA-256 hex digest and byte count from a stream
    in constant O(1) memory.
    """
    hasher = hashlib.sha256()
    total_bytes = 0
    while True:
        chunk = stream.read(chunk_size)
        if not chunk:
            break
        hasher.update(chunk)
        total_bytes += len(chunk)
    return hasher.hexdigest().lower(), total_bytes


def detect_mime_type(
    file_path: Union[str, Path],
    sample_bytes: Optional[bytes] = None,
) -> str:
    """
    Multi-stage MIME type detector:
    1. Direct extension lookup in FORENSIC_MIME_MAP
    2. Standard library mimetypes.guess_type
    3. Magic byte signature sniffer
    4. Fallback to application/octet-stream or text/plain
    """
    name = str(file_path).lower()
    
    # Handle composite archive extensions
    if name.endswith(".tar.gz") or name.endswith(".tgz"):
        return "application/gzip"
    if name.endswith(".tar.bz2") or name.endswith(".tbz2"):
        return "application/x-bzip-compressed-tar"
    if name.endswith(".tar.xz") or name.endswith(".txz"):
        return "application/x-xz-compressed-tar"
    if name.endswith(".jsonl") or name.endswith(".ndjson"):
        return "application/x-ndjson"

    ext = os.path.splitext(name)[1]
    if ext in FORENSIC_MIME_MAP:
        return FORENSIC_MIME_MAP[ext]

    # Magic byte inspection
    if sample_bytes:
        if sample_bytes.startswith(b"%PDF-"):
            return "application/pdf"
        if sample_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        if sample_bytes.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if sample_bytes.startswith(b"II*\x00") or sample_bytes.startswith(b"MM\x00*"):
            return "image/tiff"
        if sample_bytes.startswith(b"PK\x03\x04"):
            return "application/zip"
        if sample_bytes.startswith(b"\x1f\x8b"):
            return "application/gzip"
        if sample_bytes.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            return "application/msword"

    guessed, _ = mimetypes.guess_type(str(file_path))
    if guessed:
        return guessed

    if sample_bytes:
        try:
            sample_bytes.decode("utf-8")
            return "text/plain"
        except UnicodeDecodeError:
            pass

    return "application/octet-stream"


# ==============================================================================
# 5. Local Crawler Engine Class
# ==============================================================================

class LocalCrawler:
    """
    High-throughput, memory-bounded local file and archive crawler.
    """
    def __init__(
        self,
        target_paths: Optional[Sequence[Union[str, Path]]] = None,
        excluded_dirs: Optional[Set[str]] = None,
        excluded_extensions: Optional[Set[str]] = None,
        evidentiary_extensions: Optional[Set[str]] = None,
        chunk_size: int = 65536,
        max_archive_depth: int = 2,
        skip_empty: bool = False,
        deduplicate: bool = False,
    ):
        self.target_paths = [Path(p) for p in (target_paths or DEFAULT_TARGET_PATHS)]
        self.excluded_dirs = {d.lower() for d in (excluded_dirs or DEFAULT_EXCLUDED_DIRS)}
        self.excluded_extensions = {e.lower() for e in (excluded_extensions or DEFAULT_EXCLUDED_EXTENSIONS)}
        self.evidentiary_extensions = {e.lower() for e in (evidentiary_extensions or EVIDENTIARY_EXTENSIONS)}
        self.chunk_size = chunk_size
        self.max_archive_depth = max_archive_depth
        self.skip_empty = skip_empty
        self.deduplicate = deduplicate
        self.seen_hashes: Set[str] = set()
        self.stats = CrawlStats()

    def _is_excluded_dir(self, dirname: str) -> bool:
        norm = dirname.lower().strip()
        return norm in self.excluded_dirs or norm.startswith(".")

    def _is_excluded_file(self, filename: str) -> bool:
        norm = filename.lower()
        if norm.startswith("~$") or norm.startswith("._"):
            return True
        ext = os.path.splitext(norm)[1]
        return ext in self.excluded_extensions

    def crawl(self) -> Generator[IngestedArtifact, None, None]:
        """
        Main generator entry point iterating through all configured target paths.
        """
        for root_path in self.target_paths:
            if not root_path.exists():
                logger.warning(f"Target path does not exist, skipping: {root_path}")
                continue
            if root_path.is_file():
                yield from self.crawl_file_or_archive(root_path)
            elif root_path.is_dir():
                yield from self.crawl_directory(root_path)

    def crawl_directory(self, dir_path: Path) -> Generator[IngestedArtifact, None, None]:
        """
        Recursively crawls directory tree with top-down branch pruning.
        """
        logger.info(f"Beginning local crawl on directory: {dir_path}")
        for root, dirs, files in os.walk(dir_path, topdown=True, followlinks=False):
            # In-place directory pruning
            original_count = len(dirs)
            dirs[:] = [d for d in dirs if not self._is_excluded_dir(d)]
            self.stats.skipped_directories += (original_count - len(dirs))

            for fname in files:
                self.stats.total_files_scanned += 1
                if self._is_excluded_file(fname):
                    self.stats.skipped_binaries += 1
                    continue

                full_path = Path(root) / fname
                try:
                    yield from self.crawl_file_or_archive(full_path)
                except Exception as e:
                    self.stats.errors_encountered += 1
                    logger.warning(f"Error processing file '{full_path}': {e}", exc_info=False)

    def crawl_file_or_archive(self, file_path: Path) -> Generator[IngestedArtifact, None, None]:
        """
        Inspects file extension; routes archives to stream unpacker or yields direct file.
        """
        fname_lower = file_path.name.lower()
        ext = os.path.splitext(fname_lower)[1]
        
        # Check archive extensions
        is_archive = ext in ARCHIVE_EXTENSIONS or fname_lower.endswith(".tar.gz")
        if is_archive:
            yield from self.crawl_archive(file_path, depth=0)
            return

        # Direct file processing
        try:
            size = file_path.stat().st_size
            if self.skip_empty and size == 0:
                return

            with open(file_path, "rb") as f:
                sample = f.read(64)
                f.seek(0)
                sha256_hex, total_bytes = compute_stream_sha256(f, chunk_size=self.chunk_size)

            if self.deduplicate and sha256_hex in self.seen_hashes:
                return
            self.seen_hashes.add(sha256_hex)

            mime = detect_mime_type(file_path, sample_bytes=sample)
            canonical_path = str(file_path.resolve())

            artifact = IngestedArtifact(
                artifact_id=sha256_hex,
                source_uri=canonical_path,
                mime_type=mime,
                file_size_bytes=total_bytes,
                raw_stream_factory=make_file_stream_factory(canonical_path),
            )

            self.stats.evidentiary_artifacts_yielded += 1
            self.stats.total_bytes_streamed += total_bytes
            yield artifact

        except (PermissionError, OSError) as e:
            self.stats.errors_encountered += 1
            logger.warning(f"File access error for '{file_path}': {e}")

    def crawl_archive(self, archive_path: Path, depth: int = 0) -> Generator[IngestedArtifact, None, None]:
        """
        Streams members out of ZIP, TAR, or GZ archives without disk extraction.
        """
        if depth > self.max_archive_depth:
            logger.warning(f"Maximum archive depth ({self.max_archive_depth}) reached for: {archive_path}")
            return

        self.stats.archives_processed += 1
        name_lower = archive_path.name.lower()

        # Handle ZIP Archives
        if name_lower.endswith(".zip"):
            yield from self._crawl_zip(archive_path, depth)
        # Handle TAR Archives
        elif any(name_lower.endswith(s) for s in [".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz"]):
            yield from self._crawl_tar(archive_path, depth)
        # Handle standalone GZIP Files
        elif name_lower.endswith(".gz"):
            yield from self._crawl_gzip(archive_path)

    def _crawl_zip(self, zip_path: Path, depth: int) -> Generator[IngestedArtifact, None, None]:
        canonical_zip = str(zip_path.resolve())
        try:
            with zipfile.ZipFile(canonical_zip, "r") as zf:
                for entry in zf.infolist():
                    self.stats.total_files_scanned += 1
                    if entry.is_dir():
                        continue
                    
                    mname = entry.filename
                    # Security: skip path traversal entries
                    if ".." in mname or mname.startswith("/") or mname.startswith("\\"):
                        continue
                    # Skip Mac OS metadata & hidden items
                    if "__MACOSX" in mname or os.path.basename(mname).startswith("._"):
                        continue

                    if self._is_excluded_file(mname):
                        self.stats.skipped_binaries += 1
                        continue

                    mname_lower = mname.lower()
                    mext = os.path.splitext(mname_lower)[1]

                    # Stream member for SHA-256
                    try:
                        with zf.open(entry.filename, "r") as s:
                            sample = s.read(64)
                        with zf.open(entry.filename, "r") as s:
                            sha256_hex, total_bytes = compute_stream_sha256(s, chunk_size=self.chunk_size)

                        if self.skip_empty and total_bytes == 0:
                            continue
                        if self.deduplicate and sha256_hex in self.seen_hashes:
                            continue
                        self.seen_hashes.add(sha256_hex)

                        mime = detect_mime_type(mname, sample_bytes=sample)
                        uri = f"zip://{canonical_zip}#{entry.filename}"

                        artifact = IngestedArtifact(
                            artifact_id=sha256_hex,
                            source_uri=uri,
                            mime_type=mime,
                            file_size_bytes=total_bytes,
                            raw_stream_factory=make_zip_stream_factory(canonical_zip, entry.filename),
                            metadata={"archive_path": canonical_zip, "member_name": entry.filename}
                        )

                        self.stats.evidentiary_artifacts_yielded += 1
                        self.stats.archive_members_extracted += 1
                        self.stats.total_bytes_streamed += total_bytes
                        yield artifact

                    except Exception as e:
                        self.stats.errors_encountered += 1
                        logger.warning(f"Error reading zip member '{entry.filename}' in '{zip_path}': {e}")

        except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, OSError) as e:
            self.stats.errors_encountered += 1
            logger.warning(f"Failed to process zip archive '{zip_path}': {e}")

    def _crawl_tar(self, tar_path: Path, depth: int) -> Generator[IngestedArtifact, None, None]:
        canonical_tar = str(tar_path.resolve())
        try:
            with tarfile.open(canonical_tar, "r:*") as tf:
                for member in tf.getmembers():
                    self.stats.total_files_scanned += 1
                    if not member.isfile():
                        continue

                    mname = member.name
                    if ".." in mname or mname.startswith("/") or mname.startswith("\\"):
                        continue
                    if "__MACOSX" in mname or os.path.basename(mname).startswith("._"):
                        continue
                    if self._is_excluded_file(mname):
                        self.stats.skipped_binaries += 1
                        continue

                    try:
                        extracted = tf.extractfile(member)
                        if extracted is None:
                            continue
                        with extracted as s:
                            sample = s.read(64)
                        
                        extracted2 = tf.extractfile(member)
                        if extracted2 is None:
                            continue
                        with extracted2 as s:
                            sha256_hex, total_bytes = compute_stream_sha256(s, chunk_size=self.chunk_size)

                        if self.skip_empty and total_bytes == 0:
                            continue
                        if self.deduplicate and sha256_hex in self.seen_hashes:
                            continue
                        self.seen_hashes.add(sha256_hex)

                        mime = detect_mime_type(mname, sample_bytes=sample)
                        uri = f"tar://{canonical_tar}#{member.name}"

                        artifact = IngestedArtifact(
                            artifact_id=sha256_hex,
                            source_uri=uri,
                            mime_type=mime,
                            file_size_bytes=total_bytes,
                            raw_stream_factory=make_tar_stream_factory(canonical_tar, member.name),
                            metadata={"archive_path": canonical_tar, "member_name": member.name}
                        )

                        self.stats.evidentiary_artifacts_yielded += 1
                        self.stats.archive_members_extracted += 1
                        self.stats.total_bytes_streamed += total_bytes
                        yield artifact

                    except Exception as e:
                        self.stats.errors_encountered += 1
                        logger.warning(f"Error reading tar member '{member.name}' in '{tar_path}': {e}")

        except (tarfile.TarError, OSError) as e:
            self.stats.errors_encountered += 1
            logger.warning(f"Failed to process tar archive '{tar_path}': {e}")

    def _crawl_gzip(self, gz_path: Path) -> Generator[IngestedArtifact, None, None]:
        canonical_gz = str(gz_path.resolve())
        try:
            with gzip.open(canonical_gz, "rb") as s:
                sample = s.read(64)
            with gzip.open(canonical_gz, "rb") as s:
                sha256_hex, total_bytes = compute_stream_sha256(s, chunk_size=self.chunk_size)

            if self.skip_empty and total_bytes == 0:
                return
            if self.deduplicate and sha256_hex in self.seen_hashes:
                return
            self.seen_hashes.add(sha256_hex)

            # Strip .gz extension to guess inner MIME type
            inner_name = gz_path.stem
            mime = detect_mime_type(inner_name, sample_bytes=sample)
            uri = f"gzip://{canonical_gz}"

            artifact = IngestedArtifact(
                artifact_id=sha256_hex,
                source_uri=uri,
                mime_type=mime,
                file_size_bytes=total_bytes,
                raw_stream_factory=make_gzip_stream_factory(canonical_gz),
                metadata={"archive_path": canonical_gz}
            )

            self.stats.evidentiary_artifacts_yielded += 1
            self.stats.archive_members_extracted += 1
            self.stats.total_bytes_streamed += total_bytes
            yield artifact

        except (gzip.BadGzipFile, EOFError, OSError) as e:
            self.stats.errors_encountered += 1
            logger.warning(f"Failed to process gzip file '{gz_path}': {e}")


# ==============================================================================
# 6. Convenience Generator Function
# ==============================================================================

def crawl_local_files(
    target_paths: Optional[Sequence[Union[str, Path]]] = None,
    excluded_dirs: Optional[Set[str]] = None,
    excluded_extensions: Optional[Set[str]] = None,
    evidentiary_extensions: Optional[Set[str]] = None,
    chunk_size: int = 65536,
    max_archive_depth: int = 2,
    skip_empty: bool = False,
    deduplicate: bool = False,
) -> Generator[IngestedArtifact, None, None]:
    """
    Convenience functional generator wrapping LocalCrawler.
    """
    crawler = LocalCrawler(
        target_paths=target_paths,
        excluded_dirs=excluded_dirs,
        excluded_extensions=excluded_extensions,
        evidentiary_extensions=evidentiary_extensions,
        chunk_size=chunk_size,
        max_archive_depth=max_archive_depth,
        skip_empty=skip_empty,
        deduplicate=deduplicate,
    )
    yield from crawler.crawl()
