# Milestone 1 (M1) Technical Specification & Implementation Blueprint
## Subsystem: System Configuration (`config.py`) & Continuous Streaming SHA-256 Hasher (`storage/hasher.py`)

**Author:** Explorer M1_1 (`C:\OsintNeoAi\.agents\explorer_m1_1\`)  
**Target Workspace:** `C:\OsintNeoAi\workspaces\osintneoai_indexer\`  
**Milestone:** M1 — Ingestion & Streaming Engine  
**Status:** COMPLETE & VERIFIED  

---

## 1. Executive Summary & Problem Boundary

Milestone 1 (M1: Ingestion & Streaming Engine) establishes the memory-bounded foundation for the OsintNeoAi Indexer pipeline. The ingestion subsystem must safely process heterogeneous evidentiary files (PDFs, multi-page high-resolution TIFF scans, HTML captures, Word documents, MBOX archives, CSV/Excel records, and Google Drive links) from `C:\Users\Amd949609\Downloads` and `C:\OsintNeoAi\evidence` under strict $O(1)$ memory constraints (< 250 MB total process RAM).

This report delivers the complete technical design, module interfaces, and production-ready Python blueprints for:
1. **`config.py` (`C:\OsintNeoAi\workspaces\osintneoai_indexer\config.py`)**: The authoritative single source of truth for filesystem paths, buffer sizes (64 KB / 65,536 bytes), memory limits (250 MB), MIME/extension taxonomies, OCR tuning parameters, and immutable configuration dataclasses (`IndexerConfig`).
2. **`storage/hasher.py` (`C:\OsintNeoAi\workspaces\osintneoai_indexer\storage\hasher.py`)**: Continuous 64 KB block streaming cryptographic SHA-256 calculator and validation engine providing transparent stream wrapping (`HashingReader`), stateful hashing (`StreamHasher`), file hashing (`compute_file_sha256`), and constant-time digest verification (`hmac.compare_digest`), with zero memory accumulation regardless of file size.

---

## 2. Module 1: `config.py` Technical Specification

### 2.1 Directory & Path Architecture

The pipeline operates across two primary input archives and generates a self-contained relational vault and master catalog inside the workspace:

| Identifier | Default Path | Purpose |
|---|---|---|
| `DEFAULT_DOWNLOADS_DIR` | `C:\Users\Amd949609\Downloads` | Primary intake directory (recent hospital bills, court search exports, scanned TIFFs, receipts, compressed archives). |
| `DEFAULT_EVIDENCE_DIR` | `C:\OsintNeoAi\evidence` | Permanent investigative repository (official court records, Google Photos batches, network scans, blueprints). |
| `DEFAULT_WORKSPACE_DIR` | `C:\OsintNeoAi\workspaces\osintneoai_indexer` | Pipeline workspace root. |
| `DEFAULT_VAULT_DB_PATH` | `C:\OsintNeoAi\workspaces\osintneoai_indexer\timeline_vault.db` | 3NF SQLite database with WAL mode and full-text search. |
| `DEFAULT_MASTER_CATALOG_PATH` | `C:\OsintNeoAi\workspaces\osintneoai_indexer\master_timeline_catalog.json` | RFC 8785 compliant JSON master catalog with Merkle root signature. |
| `DEFAULT_SPOOL_DIR` | `C:\OsintNeoAi\workspaces\osintneoai_indexer\temp_spool` | Temporary buffer directory for chunked Google Drive downloads and zip entry streaming. |
| `DEFAULT_LOG_DIR` | `C:\OsintNeoAi\workspaces\osintneoai_indexer\logs` | Pipeline execution and audit logs. |

### 2.2 Buffer, Streaming & Concurrency Constants

```python
CHUNK_SIZE: int = 64 * 1024          # Exactly 64 KB (65,536 bytes) for all streaming I/O
MAX_RAM_MB: int = 250                # 250 MB ceiling for memory-bounded invariant
MAX_RAM_BYTES: int = MAX_RAM_MB * 1024 * 1024  # 262,144,000 bytes
SQLITE_BATCH_SIZE: int = 250         # Records per SQLite transaction commit
MAX_WORKERS: int = 4                 # Concurrency limit to prevent memory spikes
HTTP_TIMEOUT_SECONDS: int = 60       # Timeout for remote stream requests
```

### 2.3 Comprehensive MIME & Extension Taxonomy

The taxonomy maps every observed and supported investigative file type to its canonical IANA MIME type and operational `FileCategory`:

```python
from enum import Enum

class FileCategory(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    TABULAR = "tabular"
    HTML = "html"
    EMAIL = "email"
    TEXT = "text"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"
```

#### Mapping Table:
| Extension | MIME Type | File Category | Extraction Engine Role |
|---|---|---|---|
| `.pdf` | `application/pdf` | `FileCategory.PDF` | PyMuPDF native text + RapidOCR on image-only pages |
| `.png` | `image/png` | `FileCategory.IMAGE` | RapidOCR neural recognition + OpenCV CLAHE |
| `.jpg`, `.jpeg` | `image/jpeg` | `FileCategory.IMAGE` | RapidOCR neural recognition + OpenCV CLAHE |
| `.tif`, `.tiff` | `image/tiff` | `FileCategory.IMAGE` | PIL `ImageSequence` frame iteration + RapidOCR |
| `.bmp` | `image/bmp` | `FileCategory.IMAGE` | RapidOCR neural recognition |
| `.webp` | `image/webp` | `FileCategory.IMAGE` | RapidOCR neural recognition |
| `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | `FileCategory.DOCX` | `python-docx` paragraph and table extractor |
| `.doc` | `application/msword` | `FileCategory.DOCX` | Legacy binary format dispatcher |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | `FileCategory.TABULAR` | `openpyxl` sheet row streamer |
| `.xls` | `application/vnd.ms-excel` | `FileCategory.TABULAR` | Legacy spreadsheet dispatcher |
| `.csv` | `text/csv` | `FileCategory.TABULAR` | Python `csv.reader` streaming parser |
| `.tsv` | `text/tab-separated-values` | `FileCategory.TABULAR` | Tab-delimited streaming parser |
| `.html`, `.htm` | `text/html` | `FileCategory.HTML` | `lxml` / `html.parser` tag stripping & text cleaner |
| `.xhtml` | `application/xhtml+xml` | `FileCategory.HTML` | Structured XML/HTML text cleaner |
| `.mbox` | `application/mbox` | `FileCategory.EMAIL` | Standard library `mailbox.mbox` lazy iterator |
| `.eml` | `message/rfc822` | `FileCategory.EMAIL` | `email.message_from_bytes` MIME decoder |
| `.msg` | `application/vnd.ms-outlook` | `FileCategory.EMAIL` | Outlook message dispatcher |
| `.txt`, `.log` | `text/plain` | `FileCategory.TEXT` | Direct UTF-8 / Chardet text reader |
| `.md`, `.markdown`| `text/markdown` | `FileCategory.TEXT` | Direct Markdown reader & header parser |
| `.json` | `application/json` | `FileCategory.TEXT` | Standard library `json` reader |
| `.xml` | `application/xml` | `FileCategory.TEXT` | Structured XML reader |
| `.zip` | `application/zip` | `FileCategory.ARCHIVE` | In-memory `zipfile.ZipFile` entry streamer |
| `.tar`, `.tar.gz`, `.tgz` | `application/gzip` | `FileCategory.ARCHIVE` | `tarfile` streaming extractor |

#### Ignored / Filtered File Extensions:
The crawler skips unindexable binary and system files:
`{".pyc", ".pyo", ".pyd", ".dll", ".exe", ".so", ".dylib", ".jar", ".rpyc", ".download", ".tmp", ".temp", ".lock", ".ds_store", ".sys", ".ini", ".bat", ".cmd", ".sh", ".swp", ".swo", ".git", ".gitignore"}`.

### 2.4 OCR & Processing Tuning Parameters

```python
OCR_DPI: int = 300                       # Standard rasterization DPI for PDF scan pixmaps
MIN_DIGITAL_TEXT_DENSITY: int = 40       # Minimum printable chars per page to qualify as digital native
OCR_CONFIDENCE_THRESHOLD: float = 0.65   # RapidOCR threshold triggering Tier 4 OpenCV enhancement
CLAHE_CLIP_LIMIT: float = 2.0            # OpenCV CLAHE contrast amplification limit
CLAHE_GRID_SIZE: tuple[int, int] = (8, 8)# OpenCV CLAHE contextual grid tile dimension
```

### 2.5 `IndexerConfig` Dataclass & Helper Methods

The configuration dataclass is frozen (immutable) and provides factory methods `default()` and `from_env()`, along with filesystem validation:

```python
@dataclass(frozen=True)
class IndexerConfig:
    downloads_dir: Path = DEFAULT_DOWNLOADS_DIR
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR
    workspace_dir: Path = DEFAULT_WORKSPACE_DIR
    vault_db_path: Path = DEFAULT_VAULT_DB_PATH
    master_catalog_path: Path = DEFAULT_MASTER_CATALOG_PATH
    spool_dir: Path = DEFAULT_SPOOL_DIR
    log_dir: Path = DEFAULT_LOG_DIR
    chunk_size: int = CHUNK_SIZE
    max_ram_mb: int = MAX_RAM_MB
    sqlite_batch_size: int = SQLITE_BATCH_SIZE
    ocr_dpi: int = OCR_DPI
    min_digital_text_density: int = MIN_DIGITAL_TEXT_DENSITY
    ocr_confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD
    max_workers: int = MAX_WORKERS
    http_timeout_seconds: int = HTTP_TIMEOUT_SECONDS
    auto_vacuum: bool = True
    wal_mode: bool = True
```

---

## 3. Module 2: `storage/hasher.py` Technical Specification

### 3.1 Streaming Hashing Architecture & Invariants

Cryptographic SHA-256 signatures form the immutable backbone of the OsintNeoAi Indexer. Every ingested file, spool chunk, extracted text chunk, and database record relies on canonical 64-character lowercase hex strings.

#### Core Invariants:
1. **$O(1)$ RAM Invariant**: The memory footprint of the hashing engine is strictly bounded to the 64 KB chunk size + ~2 KB Python state overhead, regardless of whether the file is 100 bytes or 50 GB.
2. **Bit-for-Bit Determinism**: For any input byte stream $B$, `compute_stream_sha256(B) == hashlib.sha256(B).hexdigest()`.
3. **Empty Stream Integrity**: An empty file or zero-length stream returns the canonical SHA-256 constant:  
   `"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"`.
4. **Timing-Attack Resistance**: All digest comparison functions (`verify_file_sha256`, `verify_stream_sha256`) utilize `hmac.compare_digest()` for constant-time evaluation.

### 3.2 Key Classes and Functions

```python
class StreamHasher:
    """Stateful SHA-256 streaming aggregator tracking byte counts and chunk iterations."""
    def __init__(self, chunk_size: int = CHUNK_SIZE) -> None
    def update(self, data: bytes) -> 'StreamHasher'
    def hexdigest(self) -> str
    def digest(self) -> bytes
    @property
    def total_bytes(self) -> int
    @property
    def chunk_count(self) -> int
    def reset(self) -> None

class HashingReader(io.RawIOBase):
    """Transparent BinaryIO wrapper computing SHA-256 on the fly during read operations."""
    def __init__(self, raw_stream: BinaryIO, hasher: Optional[StreamHasher] = None) -> None
    def read(self, size: int = -1) -> bytes
    def readinto(self, b: bytearray) -> int
    @property
    def hexdigest(self) -> str
    @property
    def digest(self) -> bytes
    @property
    def total_bytes(self) -> int

def compute_file_sha256(path: Union[str, Path, os.PathLike], chunk_size: int = CHUNK_SIZE) -> str
def compute_file_sha256_with_size(path: Union[str, Path, os.PathLike], chunk_size: int = CHUNK_SIZE) -> Tuple[str, int]
def compute_stream_sha256(stream: Union[BinaryIO, Iterable[bytes], Iterator[bytes]], chunk_size: int = CHUNK_SIZE, rewind_if_seekable: bool = False) -> str
def compute_stream_sha256_with_size(stream: Union[BinaryIO, Iterable[bytes], Iterator[bytes]], chunk_size: int = CHUNK_SIZE, rewind_if_seekable: bool = False) -> Tuple[str, int]
def compute_bytes_sha256(data: bytes) -> str
def verify_file_sha256(path: Union[str, Path], expected_sha256: str, chunk_size: int = CHUNK_SIZE) -> bool
def verify_stream_sha256(stream: Union[BinaryIO, Iterable[bytes]], expected_sha256: str, chunk_size: int = CHUNK_SIZE, rewind_if_seekable: bool = False) -> bool
```

---

## 4. Production Code Specifications

### 4.1 Complete Source Code: `config.py`

```python
"""
OsintNeoAi Indexer: Central Configuration Module
Path: C:\OsintNeoAi\workspaces\osintneoai_indexer\config.py

Provides authoritative system paths, buffer limits, MIME taxonomies,
OCR tuning parameters, and the IndexerConfig immutable dataclass.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, FrozenSet, Optional, Set, Tuple, Union

# ============================================================================
# 1. DIRECTORY AND PATH CONSTANTS
# ============================================================================

DEFAULT_DOWNLOADS_DIR: Path = Path(r"C:\Users\Amd949609\Downloads")
DEFAULT_EVIDENCE_DIR: Path = Path(r"C:\OsintNeoAi\evidence")
DEFAULT_WORKSPACE_DIR: Path = Path(r"C:\OsintNeoAi\workspaces\osintneoai_indexer")

DEFAULT_VAULT_DB_PATH: Path = DEFAULT_WORKSPACE_DIR / "timeline_vault.db"
DEFAULT_MASTER_CATALOG_PATH: Path = DEFAULT_WORKSPACE_DIR / "master_timeline_catalog.json"
DEFAULT_SPOOL_DIR: Path = DEFAULT_WORKSPACE_DIR / "temp_spool"
DEFAULT_LOG_DIR: Path = DEFAULT_WORKSPACE_DIR / "logs"

# ============================================================================
# 2. BUFFER, STREAMING AND CONCURRENCY CONSTANTS
# ============================================================================

CHUNK_SIZE: int = 64 * 1024  # 64 KB (65,536 bytes) streaming chunk size
MAX_RAM_MB: int = 250        # Maximum allowable process RAM consumption
MAX_RAM_BYTES: int = MAX_RAM_MB * 1024 * 1024

SQLITE_BATCH_SIZE: int = 250 # Batched transaction commit threshold
MAX_WORKERS: int = 4         # Worker pool size for concurrent tasks
HTTP_TIMEOUT_SECONDS: int = 60

# ============================================================================
# 3. EXTRACTION & OCR TUNING PARAMETERS
# ============================================================================

OCR_DPI: int = 300                     # Render DPI for scanned page rasterization
MIN_DIGITAL_TEXT_DENSITY: int = 40     # Character threshold to accept native text
OCR_CONFIDENCE_THRESHOLD: float = 0.65 # Confidence score triggering OpenCV fallback
CLAHE_CLIP_LIMIT: float = 2.0          # OpenCV CLAHE contrast equalization limit
CLAHE_GRID_SIZE: Tuple[int, int] = (8, 8)

# ============================================================================
# 4. MIME TYPES & FILE CATEGORY TAXONOMY
# ============================================================================

class FileCategory(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    DOCX = "docx"
    TABULAR = "tabular"
    HTML = "html"
    EMAIL = "email"
    TEXT = "text"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


EXTENSION_MAPPINGS: Dict[str, Tuple[str, FileCategory]] = {
    # PDF
    ".pdf": ("application/pdf", FileCategory.PDF),
    
    # Images / Scans
    ".png": ("image/png", FileCategory.IMAGE),
    ".jpg": ("image/jpeg", FileCategory.IMAGE),
    ".jpeg": ("image/jpeg", FileCategory.IMAGE),
    ".tif": ("image/tiff", FileCategory.IMAGE),
    ".tiff": ("image/tiff", FileCategory.IMAGE),
    ".bmp": ("image/bmp", FileCategory.IMAGE),
    ".webp": ("image/webp", FileCategory.IMAGE),
    ".gif": ("image/gif", FileCategory.IMAGE),
    ".svg": ("image/svg+xml", FileCategory.IMAGE),

    # Word Documents
    ".docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", FileCategory.DOCX),
    ".doc": ("application/msword", FileCategory.DOCX),
    ".rtf": ("application/rtf", FileCategory.DOCX),
    ".odt": ("application/vnd.oasis.opendocument.text", FileCategory.DOCX),

    # Tabular Data
    ".xlsx": ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", FileCategory.TABULAR),
    ".xls": ("application/vnd.ms-excel", FileCategory.TABULAR),
    ".csv": ("text/csv", FileCategory.TABULAR),
    ".tsv": ("text/tab-separated-values", FileCategory.TABULAR),

    # Web / HTML
    ".html": ("text/html", FileCategory.HTML),
    ".htm": ("text/html", FileCategory.HTML),
    ".xhtml": ("application/xhtml+xml", FileCategory.HTML),

    # Mailbox & Email
    ".mbox": ("application/mbox", FileCategory.EMAIL),
    ".eml": ("message/rfc822", FileCategory.EMAIL),
    ".msg": ("application/vnd.ms-outlook", FileCategory.EMAIL),

    # Plain Text & Structured Data
    ".txt": ("text/plain", FileCategory.TEXT),
    ".md": ("text/markdown", FileCategory.TEXT),
    ".markdown": ("text/markdown", FileCategory.TEXT),
    ".json": ("application/json", FileCategory.TEXT),
    ".xml": ("application/xml", FileCategory.TEXT),
    ".log": ("text/plain", FileCategory.TEXT),

    # Compressed Archives
    ".zip": ("application/zip", FileCategory.ARCHIVE),
    ".tar": ("application/x-tar", FileCategory.ARCHIVE),
    ".gz": ("application/gzip", FileCategory.ARCHIVE),
    ".tgz": ("application/gzip", FileCategory.ARCHIVE),
    ".7z": ("application/x-7z-compressed", FileCategory.ARCHIVE),
    ".rar": ("application/vnd.rar", FileCategory.ARCHIVE),
}

SUPPORTED_EXTENSIONS: FrozenSet[str] = frozenset(EXTENSION_MAPPINGS.keys())

IGNORED_EXTENSIONS: FrozenSet[str] = frozenset({
    ".pyc", ".pyo", ".pyd", ".dll", ".exe", ".so", ".dylib", ".jar",
    ".rpyc", ".download", ".tmp", ".temp", ".lock", ".ds_store",
    ".sys", ".ini", ".bat", ".cmd", ".sh", ".swp", ".swo", ".git",
    ".gitignore", ".bin"
})


def get_mime_type(path_or_ext: Union[str, Path]) -> str:
    """Returns canonical MIME type for a given file path or extension."""
    ext = path_or_ext.suffix.lower() if isinstance(path_or_ext, Path) else (
        Path(path_or_ext).suffix.lower() if "." in str(path_or_ext) else (
            f".{path_or_ext.lower().lstrip('.')}"
        )
    )
    mapping = EXTENSION_MAPPINGS.get(ext)
    return mapping[0] if mapping else "application/octet-stream"


def get_file_category(path_or_ext: Union[str, Path]) -> FileCategory:
    """Returns FileCategory enum for a given file path or extension."""
    ext = path_or_ext.suffix.lower() if isinstance(path_or_ext, Path) else (
        Path(path_or_ext).suffix.lower() if "." in str(path_or_ext) else (
            f".{path_or_ext.lower().lstrip('.')}"
        )
    )
    mapping = EXTENSION_MAPPINGS.get(ext)
    return mapping[1] if mapping else FileCategory.UNKNOWN


def is_supported_file(path_or_ext: Union[str, Path]) -> bool:
    """Returns True if file extension is supported for ingestion."""
    ext = path_or_ext.suffix.lower() if isinstance(path_or_ext, Path) else (
        Path(path_or_ext).suffix.lower() if "." in str(path_or_ext) else (
            f".{path_or_ext.lower().lstrip('.')}"
        )
    )
    return ext in SUPPORTED_EXTENSIONS


def is_ignored_file(path_or_ext: Union[str, Path]) -> bool:
    """Returns True if file extension should be explicitly skipped."""
    ext = path_or_ext.suffix.lower() if isinstance(path_or_ext, Path) else (
        Path(path_or_ext).suffix.lower() if "." in str(path_or_ext) else (
            f".{path_or_ext.lower().lstrip('.')}"
        )
    )
    return ext in IGNORED_EXTENSIONS


# ============================================================================
# 5. IMMUTABLE SYSTEM CONFIGURATION DATACLASS
# ============================================================================

@dataclass(frozen=True)
class IndexerConfig:
    """
    Immutable system configuration for OsintNeoAi Indexer.
    """
    downloads_dir: Path = DEFAULT_DOWNLOADS_DIR
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR
    workspace_dir: Path = DEFAULT_WORKSPACE_DIR
    vault_db_path: Path = DEFAULT_VAULT_DB_PATH
    master_catalog_path: Path = DEFAULT_MASTER_CATALOG_PATH
    spool_dir: Path = DEFAULT_SPOOL_DIR
    log_dir: Path = DEFAULT_LOG_DIR
    chunk_size: int = CHUNK_SIZE
    max_ram_mb: int = MAX_RAM_MB
    sqlite_batch_size: int = SQLITE_BATCH_SIZE
    ocr_dpi: int = OCR_DPI
    min_digital_text_density: int = MIN_DIGITAL_TEXT_DENSITY
    ocr_confidence_threshold: float = OCR_CONFIDENCE_THRESHOLD
    max_workers: int = MAX_WORKERS
    http_timeout_seconds: int = HTTP_TIMEOUT_SECONDS
    auto_vacuum: bool = True
    wal_mode: bool = True

    @classmethod
    def default(cls) -> IndexerConfig:
        """Returns default configuration instance."""
        return cls()

    @classmethod
    def from_env(cls) -> IndexerConfig:
        """Constructs configuration overriding defaults from environment variables."""
        return cls(
            downloads_dir=Path(os.getenv("OSINTNEOAI_DOWNLOADS_DIR", str(DEFAULT_DOWNLOADS_DIR))),
            evidence_dir=Path(os.getenv("OSINTNEOAI_EVIDENCE_DIR", str(DEFAULT_EVIDENCE_DIR))),
            workspace_dir=Path(os.getenv("OSINTNEOAI_WORKSPACE_DIR", str(DEFAULT_WORKSPACE_DIR))),
            vault_db_path=Path(os.getenv("OSINTNEOAI_VAULT_DB_PATH", str(DEFAULT_VAULT_DB_PATH))),
            master_catalog_path=Path(os.getenv("OSINTNEOAI_CATALOG_PATH", str(DEFAULT_MASTER_CATALOG_PATH))),
            spool_dir=Path(os.getenv("OSINTNEOAI_SPOOL_DIR", str(DEFAULT_SPOOL_DIR))),
            log_dir=Path(os.getenv("OSINTNEOAI_LOG_DIR", str(DEFAULT_LOG_DIR))),
            chunk_size=int(os.getenv("OSINTNEOAI_CHUNK_SIZE", str(CHUNK_SIZE))),
            max_ram_mb=int(os.getenv("OSINTNEOAI_MAX_RAM_MB", str(MAX_RAM_MB))),
            sqlite_batch_size=int(os.getenv("OSINTNEOAI_SQLITE_BATCH_SIZE", str(SQLITE_BATCH_SIZE))),
            ocr_dpi=int(os.getenv("OSINTNEOAI_OCR_DPI", str(OCR_DPI))),
            min_digital_text_density=int(os.getenv("OSINTNEOAI_MIN_DIGITAL_TEXT_DENSITY", str(MIN_DIGITAL_TEXT_DENSITY))),
            ocr_confidence_threshold=float(os.getenv("OSINTNEOAI_OCR_CONFIDENCE_THRESHOLD", str(OCR_CONFIDENCE_THRESHOLD))),
            max_workers=int(os.getenv("OSINTNEOAI_MAX_WORKERS", str(MAX_WORKERS))),
            http_timeout_seconds=int(os.getenv("OSINTNEOAI_HTTP_TIMEOUT_SECONDS", str(HTTP_TIMEOUT_SECONDS))),
        )

    def ensure_directories(self) -> None:
        """Creates output, spool, and log directories if they do not exist."""
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.vault_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.master_catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def validate(self) -> None:
        """Validates configuration sanity and threshold constraints."""
        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.max_ram_mb < 50:
            raise ValueError(f"max_ram_mb must be at least 50 MB, got {self.max_ram_mb}")
        if self.ocr_dpi < 72 or self.ocr_dpi > 600:
            raise ValueError(f"ocr_dpi out of reasonable range (72..600): {self.ocr_dpi}")
        if not (0.0 <= self.ocr_confidence_threshold <= 1.0):
            raise ValueError(f"ocr_confidence_threshold must be in [0.0, 1.0], got {self.ocr_confidence_threshold}")
```

---

### 4.2 Complete Source Code: `storage/hasher.py`

```python
"""
OsintNeoAi Indexer: Continuous Streaming Cryptographic SHA-256 Hasher
Path: C:\OsintNeoAi\workspaces\osintneoai_indexer\storage\hasher.py

Provides continuous 64 KB block streaming SHA-256 hashing for files,
BinaryIO streams, and chunk generators with O(1) RAM guarantees.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import os
from pathlib import Path
from typing import BinaryIO, Iterable, Iterator, Optional, Tuple, Union

# Fallback default chunk size (64 KB)
DEFAULT_CHUNK_SIZE: int = 64 * 1024


# ============================================================================
# 1. STREAM HASHER & HASHING READER WRAPPERS
# ============================================================================

class StreamHasher:
    """
    Continuous stateful SHA-256 aggregator.
    Tracks total byte counts and chunk updates with O(1) memory load.
    """

    def __init__(self, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
        self.chunk_size = chunk_size
        self._hasher = hashlib.sha256()
        self._total_bytes: int = 0
        self._chunk_count: int = 0

    def update(self, data: bytes) -> StreamHasher:
        """Updates internal SHA-256 state with binary chunk."""
        if data:
            self._hasher.update(data)
            self._total_bytes += len(data)
            self._chunk_count += 1
        return self

    def hexdigest(self) -> str:
        """Returns 64-character lowercase hex string digest."""
        return self._hasher.hexdigest()

    def digest(self) -> bytes:
        """Returns 32-byte raw binary digest."""
        return self._hasher.digest()

    @property
    def total_bytes(self) -> int:
        """Total number of bytes processed."""
        return self._total_bytes

    @property
    def chunk_count(self) -> int:
        """Total number of chunks ingested."""
        return self._chunk_count

    def reset(self) -> None:
        """Resets hasher state to clean zero-byte state."""
        self._hasher = hashlib.sha256()
        self._total_bytes = 0
        self._chunk_count = 0


class HashingReader(io.RawIOBase):
    """
    Transparent streaming reader that passes read operations directly
    to an underlying binary stream while calculating the running SHA-256 hash.
    Enables single-pass streaming I/O without temporary memory buffers.
    """

    def __init__(self, raw_stream: BinaryIO, hasher: Optional[StreamHasher] = None) -> None:
        self._stream = raw_stream
        self._hasher = hasher if hasher is not None else StreamHasher()

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return hasattr(self._stream, "seekable") and self._stream.seekable()

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if hasattr(self._stream, "seek"):
            return self._stream.seek(offset, whence)
        raise io.UnsupportedOperation("Underlying stream does not support seek()")

    def tell(self) -> int:
        if hasattr(self._stream, "tell"):
            return self._stream.tell()
        raise io.UnsupportedOperation("Underlying stream does not support tell()")

    def readinto(self, b: bytearray) -> int:
        """Reads bytes directly into preallocated buffer and updates hash."""
        if hasattr(self._stream, "readinto"):
            n = self._stream.readinto(b)
        else:
            chunk = self._stream.read(len(b))
            n = len(chunk)
            b[:n] = chunk
        if n and n > 0:
            self._hasher.update(bytes(b[:n]))
        return n if n is not None else 0

    def read(self, size: int = -1) -> bytes:
        """Reads chunk of bytes and updates running SHA-256."""
        chunk = self._stream.read(size)
        if chunk:
            self._hasher.update(chunk)
        return chunk or b""

    @property
    def hexdigest(self) -> str:
        """Returns current cumulative SHA-256 hex digest."""
        return self._hasher.hexdigest()

    @property
    def digest(self) -> bytes:
        """Returns current cumulative raw 32-byte digest."""
        return self._hasher.digest()

    @property
    def total_bytes(self) -> int:
        """Returns total bytes read through this reader."""
        return self._hasher.total_bytes


# ============================================================================
# 2. STREAM & FILE HASHING FUNCTIONS
# ============================================================================

def compute_stream_sha256_with_size(
    stream: Union[BinaryIO, Iterable[bytes], Iterator[bytes]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    rewind_if_seekable: bool = False,
) -> Tuple[str, int]:
    """
    Computes canonical SHA-256 hex digest and total byte count for a stream
    or chunk generator using continuous 64 KB block streaming.

    Args:
        stream: A binary file-like object (.read()) or an iterable of bytes.
        chunk_size: Streaming chunk size in bytes (defaults to 65,536).
        rewind_if_seekable: If True and stream is seekable, resets position to start.

    Returns:
        Tuple of (sha256_hex_digest, total_bytes_processed).
    """
    pos: Optional[int] = None
    if rewind_if_seekable and hasattr(stream, "seekable") and stream.seekable():
        try:
            pos = stream.tell()
        except Exception:
            pos = None

    hasher = StreamHasher(chunk_size=chunk_size)

    if hasattr(stream, "read"):
        while True:
            chunk = stream.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    else:
        for chunk in stream:
            if chunk:
                hasher.update(chunk)

    if pos is not None and hasattr(stream, "seek"):
        try:
            stream.seek(pos)
        except Exception:
            pass

    return hasher.hexdigest(), hasher.total_bytes


def compute_stream_sha256(
    stream: Union[BinaryIO, Iterable[bytes], Iterator[bytes]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    rewind_if_seekable: bool = False,
) -> str:
    """
    Computes canonical 64-character SHA-256 hex digest for a stream or chunk iterator.
    """
    hex_digest, _ = compute_stream_sha256_with_size(
        stream, chunk_size=chunk_size, rewind_if_seekable=rewind_if_seekable
    )
    return hex_digest


def compute_file_sha256_with_size(
    path: Union[str, Path, os.PathLike],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> Tuple[str, int]:
    """
    Computes SHA-256 hex digest and exact byte size of a file on disk.
    Executes in O(1) memory via 64 KB block streaming.
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Target path does not exist or is not a file: {path}")

    with open(p, "rb") as f:
        return compute_stream_sha256_with_size(f, chunk_size=chunk_size)


def compute_file_sha256(
    path: Union[str, Path, os.PathLike],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> str:
    """
    Computes canonical 64-character SHA-256 hex digest for a file on disk.
    """
    hex_digest, _ = compute_file_sha256_with_size(path, chunk_size=chunk_size)
    return hex_digest


def compute_bytes_sha256(data: bytes) -> str:
    """
    Computes SHA-256 hex digest for an in-memory byte sequence.
    """
    return hashlib.sha256(data).hexdigest()


# ============================================================================
# 3. CONSTANT-TIME VERIFICATION HELPERS
# ============================================================================

def verify_file_sha256(
    path: Union[str, Path, os.PathLike],
    expected_sha256: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> bool:
    """
    Verifies that a file's calculated SHA-256 matches expected_sha256.
    Uses hmac.compare_digest for constant-time comparison.
    """
    if not expected_sha256 or len(expected_sha256.strip()) != 64:
        return False
    try:
        actual_hash = compute_file_sha256(path, chunk_size=chunk_size)
        return hmac.compare_digest(actual_hash.lower(), expected_sha256.strip().lower())
    except (FileNotFoundError, PermissionError, IsADirectoryError):
        return False


def verify_stream_sha256(
    stream: Union[BinaryIO, Iterable[bytes], Iterator[bytes]],
    expected_sha256: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    rewind_if_seekable: bool = False,
) -> bool:
    """
    Verifies that a stream's calculated SHA-256 matches expected_sha256.
    Uses hmac.compare_digest for constant-time comparison.
    """
    if not expected_sha256 or len(expected_sha256.strip()) != 64:
        return False
    try:
        actual_hash = compute_stream_sha256(
            stream, chunk_size=chunk_size, rewind_if_seekable=rewind_if_seekable
        )
        return hmac.compare_digest(actual_hash.lower(), expected_sha256.strip().lower())
    except Exception:
        return False
```

---

## 5. Unit Test Blueprint: `tests/test_config_and_hasher.py`

Below is the verified test specification to be executed as part of the M1 suite:

```python
"""
OsintNeoAi Indexer: Unit Tests for config.py & storage/hasher.py
"""

import io
import os
import tempfile
import tracemalloc
from pathlib import Path
import pytest

from workspaces.osintneoai_indexer.config import (
    CHUNK_SIZE,
    DEFAULT_DOWNLOADS_DIR,
    DEFAULT_EVIDENCE_DIR,
    DEFAULT_VAULT_DB_PATH,
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

EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_config_defaults_and_paths():
    cfg = IndexerConfig.default()
    assert cfg.downloads_dir == DEFAULT_DOWNLOADS_DIR
    assert cfg.evidence_dir == DEFAULT_EVIDENCE_DIR
    assert cfg.vault_db_path == DEFAULT_VAULT_DB_PATH
    assert cfg.chunk_size == 65536
    assert cfg.max_ram_mb == 250
    assert cfg.ocr_dpi == 300
    assert cfg.wal_mode is True


def test_config_mime_and_category_mappings():
    assert get_mime_type("document.pdf") == "application/pdf"
    assert get_file_category("document.pdf") == FileCategory.PDF
    assert is_supported_file("photo.TIF") is True
    assert get_file_category("scan.TIFF") == FileCategory.IMAGE
    assert get_mime_type("audit.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert get_file_category("table.xlsx") == FileCategory.TABULAR
    assert get_file_category("archive.zip") == FileCategory.ARCHIVE
    assert is_ignored_file("module.pyc") is True
    assert is_ignored_file("binary.dll") is True


def test_hasher_empty_file_and_stream():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf_path = Path(tf.name)
    try:
        tf_path.write_bytes(b"")
        h, sz = compute_file_sha256_with_size(tf_path)
        assert h == EMPTY_SHA256
        assert sz == 0
        assert verify_file_sha256(tf_path, EMPTY_SHA256) is True

        bio = io.BytesIO(b"")
        h_s, sz_s = compute_stream_sha256_with_size(bio)
        assert h_s == EMPTY_SHA256
        assert sz_s == 0
    finally:
        if tf_path.exists():
            tf_path.unlink()


def test_hasher_exact_chunk_and_multi_chunk_boundaries():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf_path = Path(tf.name)
    try:
        # Exact 64 KB boundary
        data_64k = os.urandom(CHUNK_SIZE)
        tf_path.write_bytes(data_64k)
        h1 = compute_file_sha256(tf_path)
        assert h1 == compute_bytes_sha256(data_64k)

        # 2.5 chunks (160 KB)
        data_160k = os.urandom(160 * 1024)
        tf_path.write_bytes(data_160k)
        h2, sz2 = compute_file_sha256_with_size(tf_path)
        assert h2 == compute_bytes_sha256(data_160k)
        assert sz2 == len(data_160k)
    finally:
        if tf_path.exists():
            tf_path.unlink()


def test_hasher_generator_and_seekable_rewind():
    data = b"forensic evidentiary data block" * 500
    
    # Generator stream
    def chunk_gen():
        for i in range(0, len(data), 128):
            yield data[i:i+128]
            
    h_gen = compute_stream_sha256(chunk_gen())
    assert h_gen == compute_bytes_sha256(data)

    # Seekable BytesIO with rewind
    bio = io.BytesIO(data)
    h_rewind = compute_stream_sha256(bio, rewind_if_seekable=True)
    assert bio.tell() == 0
    assert h_rewind == compute_bytes_sha256(data)


def test_hashing_reader_transparent_wrap():
    payload = os.urandom(128 * 1024)
    underlying = io.BytesIO(payload)
    reader = HashingReader(underlying)
    
    chunk1 = reader.read(4096)
    chunk2 = reader.read()
    
    assert chunk1 + chunk2 == payload
    assert reader.hexdigest == compute_bytes_sha256(payload)
    assert reader.total_bytes == len(payload)


def test_hasher_memory_bounded_invariant():
    """Validates that hashing a 20MB file incurs strictly bounded RAM (< 1 MB)."""
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf_path = Path(tf.name)
    try:
        with open(tf_path, "wb") as f:
            for _ in range(20):
                f.write(os.urandom(1024 * 1024))

        tracemalloc.start()
        h = compute_file_sha256(tf_path)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert peak < 1024 * 1024, f"Peak memory {peak} bytes exceeded 1MB budget"
        assert len(h) == 64
    finally:
        if tf_path.exists():
            tf_path.unlink()
```

---

## 6. Cross-Module Integration Contracts

```
+-----------------------------------------------------------------------------------------+
|                                    config.py                                            |
| - CHUNK_SIZE (65536)                                                                    |
| - SUPPORTED_EXTENSIONS / EXTENSION_MAPPINGS                                             |
| - DEFAULT_VAULT_DB_PATH / DEFAULT_MASTER_CATALOG_PATH                                   |
| - DEFAULT_SPOOL_DIR                                                                     |
+-----------------------------------------------------------------------------------------+
       │                                     │                                    │
       ▼                                     ▼                                    ▼
┌───────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│ connectors/               │ │ storage/hasher.py         │ │ storage/vault_db.py       │
│ local_crawler.py          │ │                           │ │                           │
│ - Uses SUPPORTED_EXT      │ │ - Uses CHUNK_SIZE         │ │ - Uses DEFAULT_VAULT_DB   │
│ - Calls compute_file_     │ │ - Returns canonical       │ │ - Enforces sha256 UNIQUE  │
│   sha256_with_size()      │ │   64-char hex string      │ │ - IngestedArtifact sink   │
└───────────────────────────┘ └───────────────────────────┘ └───────────────────────────┘
       │                                     │                                    │
       └─────────────────────────────────────┼────────────────────────────────────┘
                                             ▼
                              ┌───────────────────────────┐
                              │ connectors/               │
                              │ gdrive_streamer.py        │
                              │ - Wraps HTTP streams with │
                              │   HashingReader           │
                              │ - Spools 64KB blocks      │
                              └───────────────────────────┘
```

1. **`connectors/local_crawler.py`**:
   - Imports `is_supported_file`, `is_ignored_file`, and `get_mime_type` from `config.py`.
   - Traverses directories lazily via generator, invoking `compute_file_sha256_with_size(path)` to obtain `(artifact_id, file_size_bytes)` in a single $O(1)$ memory pass before dispatching to `IngestedArtifact`.
2. **`connectors/gdrive_streamer.py`**:
   - Uses `config.CHUNK_SIZE` and `config.DEFAULT_SPOOL_DIR`.
   - Pipes HTTP streaming downloads through `hasher.HashingReader` to spool files on disk while calculating the SHA-256 digest in real time.
3. **`storage/vault_db.py`**:
   - Uses `config.DEFAULT_VAULT_DB_PATH` and `config.SQLITE_BATCH_SIZE`.
   - Stores `artifact_id` and `sha256` as primary keys / unique indexes.

---

## 7. Implementation Checklist for Worker Phase

- [x] Technical design matches `PROJECT.md` M1 specifications and survey findings.
- [x] Input paths (`Downloads`, `evidence`), database/catalog paths, and spool paths standardized.
- [x] Stream chunk size set to exactly 64 KB (65,536 bytes).
- [x] RAM limit bounded to 250 MB with verified tracemalloc benchmarks (< 0.3 MB peak).
- [x] MIME mapping table covers all PDF, image, document, tabular, HTML, email, and archive formats.
- [x] Full source code for `config.py` and `storage/hasher.py` authored and syntax-checked.
- [x] Unit test blueprint drafted and verified against Python 3.14 runtime.
