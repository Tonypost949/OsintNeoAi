"""
OsintNeoAi Indexer: Central Configuration Module
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\config.py

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
MAX_RAM_MB: int = 250        # Maximum allowable process RAM consumption (MB)
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
    ".jpe": ("image/jpeg", FileCategory.IMAGE),
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
    ".ods": ("application/vnd.oasis.opendocument.spreadsheet", FileCategory.TABULAR),

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
    ".text": ("text/plain", FileCategory.TEXT),
    ".md": ("text/markdown", FileCategory.TEXT),
    ".markdown": ("text/markdown", FileCategory.TEXT),
    ".json": ("application/json", FileCategory.TEXT),
    ".jsonl": ("application/x-ndjson", FileCategory.TEXT),
    ".ndjson": ("application/x-ndjson", FileCategory.TEXT),
    ".xml": ("application/xml", FileCategory.TEXT),
    ".yaml": ("application/x-yaml", FileCategory.TEXT),
    ".yml": ("application/x-yaml", FileCategory.TEXT),
    ".log": ("text/plain", FileCategory.TEXT),
    ".nfo": ("text/plain", FileCategory.TEXT),
    ".conf": ("text/plain", FileCategory.TEXT),
    ".cfg": ("text/plain", FileCategory.TEXT),
    ".ini": ("text/plain", FileCategory.TEXT),

    # Compressed Archives
    ".zip": ("application/zip", FileCategory.ARCHIVE),
    ".tar": ("application/x-tar", FileCategory.ARCHIVE),
    ".gz": ("application/gzip", FileCategory.ARCHIVE),
    ".tgz": ("application/gzip", FileCategory.ARCHIVE),
    ".tar.gz": ("application/gzip", FileCategory.ARCHIVE),
    ".tar.bz2": ("application/x-bzip-compressed-tar", FileCategory.ARCHIVE),
    ".tbz2": ("application/x-bzip-compressed-tar", FileCategory.ARCHIVE),
    ".tar.xz": ("application/x-xz-compressed-tar", FileCategory.ARCHIVE),
    ".txz": ("application/x-xz-compressed-tar", FileCategory.ARCHIVE),
    ".7z": ("application/x-7z-compressed", FileCategory.ARCHIVE),
    ".rar": ("application/vnd.rar", FileCategory.ARCHIVE),
}

SUPPORTED_EXTENSIONS: FrozenSet[str] = frozenset(EXTENSION_MAPPINGS.keys())

IGNORED_EXTENSIONS: FrozenSet[str] = frozenset({
    ".pyc", ".pyo", ".pyd", ".dll", ".exe", ".so", ".dylib", ".jar",
    ".war", ".ear", ".iso", ".msi", ".msp", ".img", ".dmg", ".pkg",
    ".deb", ".rpm", ".rpyc", ".rpymc", ".download", ".tmp", ".temp",
    ".lock", ".ds_store", ".sys", ".drv", ".ocx", ".bat", ".cmd",
    ".sh", ".swp", ".swo", ".git", ".gitignore", ".bin", ".rom",
    ".vmdk", ".qcow2", ".class", ".pdb", ".idb", ".lib", ".a",
    ".whl", ".egg", ".node", ".o", ".obj", ".crdownload", ".part",
    ".ttf", ".otf", ".woff", ".woff2", ".eot", ".cur", ".ico"
})


MIME_TO_CATEGORY: Dict[str, FileCategory] = {
    mapping[0].lower(): mapping[1] for mapping in EXTENSION_MAPPINGS.values()
}
MIME_TO_CATEGORY.update({
    "text/html": FileCategory.HTML,
    "application/xhtml+xml": FileCategory.HTML,
    "application/pdf": FileCategory.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileCategory.DOCX,
    "application/msword": FileCategory.DOCX,
    "application/rtf": FileCategory.DOCX,
    "application/vnd.oasis.opendocument.text": FileCategory.DOCX,
    "image/png": FileCategory.IMAGE,
    "image/jpeg": FileCategory.IMAGE,
    "image/jpg": FileCategory.IMAGE,
    "image/tiff": FileCategory.IMAGE,
    "image/tif": FileCategory.IMAGE,
    "image/webp": FileCategory.IMAGE,
    "image/bmp": FileCategory.IMAGE,
    "image/gif": FileCategory.IMAGE,
    "text/plain": FileCategory.TEXT,
    "text/markdown": FileCategory.TEXT,
    "text/csv": FileCategory.TABULAR,
    "text/tab-separated-values": FileCategory.TABULAR,
    "application/json": FileCategory.TEXT,
    "application/x-ndjson": FileCategory.TEXT,
    "application/xml": FileCategory.TEXT,
    "application/x-yaml": FileCategory.TEXT,
    "message/rfc822": FileCategory.EMAIL,
    "application/mbox": FileCategory.EMAIL,
    "application/vnd.ms-outlook": FileCategory.EMAIL,
    "application/zip": FileCategory.ARCHIVE,
    "application/gzip": FileCategory.ARCHIVE,
    "application/x-tar": FileCategory.ARCHIVE,
})


def _extract_suffix(path_or_ext: Union[str, Path]) -> str:
    """Helper to extract normalized lowercase extension."""
    if isinstance(path_or_ext, Path):
        return path_or_ext.suffix.lower()
    str_val = str(path_or_ext).lower().strip()
    if "." in str_val:
        return Path(str_val).suffix.lower()
    return f".{str_val.lstrip('.')}"


def get_mime_type(path_or_ext: Union[str, Path]) -> str:
    """Returns canonical MIME type for a given file path or extension."""
    s = str(path_or_ext).lower().strip()
    if s in MIME_TO_CATEGORY:
        return s
    ext = _extract_suffix(path_or_ext)
    mapping = EXTENSION_MAPPINGS.get(ext)
    return mapping[0] if mapping else "application/octet-stream"


def get_file_category(path_or_ext: Union[str, Path]) -> FileCategory:
    """Returns FileCategory enum for a given file path, extension, or MIME type."""
    s = str(path_or_ext).lower().strip()
    if s in MIME_TO_CATEGORY:
        return MIME_TO_CATEGORY[s]
    ext = _extract_suffix(path_or_ext)
    mapping = EXTENSION_MAPPINGS.get(ext)
    return mapping[1] if mapping else FileCategory.UNKNOWN


def is_supported_file(path_or_ext: Union[str, Path]) -> bool:
    """Returns True if file extension is supported for ingestion."""
    ext = _extract_suffix(path_or_ext)
    return ext in SUPPORTED_EXTENSIONS


def is_ignored_file(path_or_ext: Union[str, Path]) -> bool:
    """Returns True if file extension should be explicitly skipped."""
    ext = _extract_suffix(path_or_ext)
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
