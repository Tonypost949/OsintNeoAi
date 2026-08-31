"""
OsintNeoAi Indexer — Google Drive Streaming Connector
Module: workspaces.osintneoai_indexer.connectors.gdrive_streamer
Integrity: Constant O(1) Memory Streaming, Automatic Virus-Scan Bypass, Offline Fallback
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import mimetypes
import os
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)
from urllib.parse import parse_qs, urlparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger("osintneoai.connectors.gdrive")

CHUNK_SIZE: int = 64 * 1024  # 64 KB streaming buffer

# Standard export format mappings for Google Workspace Docs
WORKSPACE_EXPORT_MIMES: Dict[str, Dict[str, str]] = {
    "doc": {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "txt": "text/plain",
    },
    "sheet": {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pdf": "application/pdf",
    },
    "presentation": {
        "pdf": "application/pdf",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "txt": "text/plain",
    }
}


@dataclass(frozen=True)
class IngestedArtifact:
    artifact_id: str             # Canonical SHA-256 hex string (64 chars)
    source_uri: str              # Original URL or Local Fallback Path
    mime_type: str               # Normalized MIME type
    file_size_bytes: int         # Exact file size
    raw_stream_factory: Callable[[], BinaryIO] # Reusable stream factory
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class GDriveResourceInfo:
    resource_id: str
    resource_type: str  # 'file', 'doc', 'sheet', 'presentation', 'folder'
    export_format: Optional[str]
    download_url: str
    original_url: str
    inferred_filename: Optional[str] = None
    inferred_mime_type: Optional[str] = None


class GDriveStreamError(Exception):
    """Custom exception raised when GDrive resolution and fallback fail."""
    pass


class GDriveStreamer:
    """
    Streaming Google Drive connector that resolves public/shared links,
    streams bytes in 64 KB chunks, bypasses virus-scan tokens,
    and falls back to local cache when offline.
    """

    PATTERNS: Dict[str, re.Pattern] = {
        "file_d": re.compile(r"https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]{20,})"),
        "open_id": re.compile(r"https?://drive\.google\.com/open\?(?:.*&)?id=([a-zA-Z0-9_-]{20,})"),
        "uc_id": re.compile(r"https?://drive\.google\.com/uc\?(?:.*&)?id=([a-zA-Z0-9_-]{20,})"),
        "folder_d": re.compile(r"https?://drive\.google\.com/drive/(?:u/\d+/)?folders/([a-zA-Z0-9_-]{20,})"),
        "doc_d": re.compile(r"https?://docs\.google\.com/document/d/([a-zA-Z0-9_-]{20,})"),
        "sheet_d": re.compile(r"https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_-]{20,})"),
        "presentation_d": re.compile(r"https?://docs\.google\.com/presentation/d/([a-zA-Z0-9_-]{20,})"),
        "raw_id": re.compile(r"^[a-zA-Z0-9_-]{20,50}$"),
    }

    def __init__(
        self,
        spool_dir: Optional[Union[str, Path]] = None,
        local_cache_dirs: Optional[List[Union[str, Path]]] = None,
        timeout_seconds: int = 30,
        prefer_offline: bool = False
    ):
        self.spool_dir = Path(spool_dir) if spool_dir else Path(tempfile.gettempdir()) / "osintneoai_gdrive_spool"
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        
        raw_dirs = local_cache_dirs or [
            Path(r"C:\OsintNeoAi\evidence\google_drive"),
            Path(r"C:\OsintNeoAi\evidence"),
            Path(r"C:\Users\Amd949609\Downloads")
        ]
        self.local_cache_dirs = [Path(d) for d in raw_dirs]
        self.timeout_seconds = timeout_seconds
        self.prefer_offline = prefer_offline
        self._manifest_cache: Dict[str, Dict[str, Any]] = {}
        self._load_local_manifests()

    def _load_local_manifests(self) -> None:
        """Loads GDRIVE_INGESTION_MANIFEST.json from cache directories."""
        for cache_dir in self.local_cache_dirs:
            manifest_file = cache_dir / "GDRIVE_INGESTION_MANIFEST.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                gid = item.get("gdrive_id")
                                if gid:
                                    self._manifest_cache[gid] = item
                except Exception as e:
                    logger.warning(f"Failed to parse manifest {manifest_file}: {e}")

    def parse_url(
        self,
        url_or_id: str,
        default_doc_format: str = "pdf",
        default_sheet_format: str = "csv"
    ) -> GDriveResourceInfo:
        """
        Parses a Google Drive URL or raw File ID into a structured GDriveResourceInfo.
        """
        raw = url_or_id.strip()
        
        # Check raw ID
        if self.PATTERNS["raw_id"].match(raw) and not raw.startswith("http"):
            file_id = raw
            return GDriveResourceInfo(
                resource_id=file_id,
                resource_type="file",
                export_format=None,
                download_url=f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
                original_url=url_or_id,
                inferred_mime_type="application/octet-stream"
            )

        # Check Google Docs
        m = self.PATTERNS["doc_d"].search(raw)
        if m:
            file_id = m.group(1)
            fmt = default_doc_format
            parsed_q = parse_qs(urlparse(raw).query)
            if "format" in parsed_q:
                fmt = parsed_q["format"][0].lower()
            return GDriveResourceInfo(
                resource_id=file_id,
                resource_type="doc",
                export_format=fmt,
                download_url=f"https://docs.google.com/document/d/{file_id}/export?format={fmt}",
                original_url=url_or_id,
                inferred_filename=f"{file_id}.{fmt}",
                inferred_mime_type=WORKSPACE_EXPORT_MIMES["doc"].get(fmt, "application/pdf")
            )

        # Check Google Sheets
        m = self.PATTERNS["sheet_d"].search(raw)
        if m:
            file_id = m.group(1)
            fmt = default_sheet_format
            parsed_q = parse_qs(urlparse(raw).query)
            if "format" in parsed_q:
                fmt = parsed_q["format"][0].lower()
            return GDriveResourceInfo(
                resource_id=file_id,
                resource_type="sheet",
                export_format=fmt,
                download_url=f"https://docs.google.com/spreadsheets/d/{file_id}/export?format={fmt}",
                original_url=url_or_id,
                inferred_filename=f"{file_id}.{fmt}",
                inferred_mime_type=WORKSPACE_EXPORT_MIMES["sheet"].get(fmt, "text/csv")
            )

        # Check Google Slides
        m = self.PATTERNS["presentation_d"].search(raw)
        if m:
            file_id = m.group(1)
            fmt = "pdf"
            return GDriveResourceInfo(
                resource_id=file_id,
                resource_type="presentation",
                export_format=fmt,
                download_url=f"https://docs.google.com/presentation/d/{file_id}/export?format={fmt}",
                original_url=url_or_id,
                inferred_filename=f"{file_id}.{fmt}",
                inferred_mime_type="application/pdf"
            )

        # Check File View / Open / UC
        for key in ("file_d", "open_id", "uc_id"):
            m = self.PATTERNS[key].search(raw)
            if m:
                file_id = m.group(1)
                return GDriveResourceInfo(
                    resource_id=file_id,
                    resource_type="file",
                    export_format=None,
                    download_url=f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t",
                    original_url=url_or_id,
                    inferred_filename=file_id,
                    inferred_mime_type="application/octet-stream"
                )

        # Check Folder
        m = self.PATTERNS["folder_d"].search(raw)
        if m:
            file_id = m.group(1)
            return GDriveResourceInfo(
                resource_id=file_id,
                resource_type="folder",
                export_format=None,
                download_url=f"https://drive.google.com/drive/folders/{file_id}",
                original_url=url_or_id,
                inferred_mime_type="inode/directory"
            )

        raise GDriveStreamError(f"Could not parse valid Google Drive file/doc ID from URL: {url_or_id}")

    def find_local_cached_file(self, resource_info: GDriveResourceInfo) -> Optional[Path]:
        """
        Searches configured local cache directories for matching mirrored files.
        """
        file_id = resource_info.resource_id
        
        # 1. Check manifest cache entry
        if file_id in self._manifest_cache:
            meta = self._manifest_cache[file_id]
            raw_path = meta.get("path")
            if raw_path and Path(raw_path).exists():
                return Path(raw_path)
            name = meta.get("name")
            if name:
                for cdir in self.local_cache_dirs:
                    candidate = cdir / name
                    if candidate.exists():
                        return candidate

        # 2. Check direct naming conventions across cache directories
        prefixes = [
            f"gfile_{file_id}",
            f"gdoc_{file_id}",
            f"gsheet_{file_id}",
            file_id
        ]
        
        for cdir in self.local_cache_dirs:
            if not cdir.exists():
                continue
            try:
                for entry in cdir.iterdir():
                    if entry.is_file():
                        name_lower = entry.name.lower()
                        for pref in prefixes:
                            if pref.lower() in name_lower:
                                return entry
            except (PermissionError, OSError):
                continue

        return None

    def stream_to_spool(self, resource_info: GDriveResourceInfo) -> Tuple[Path, str, int, str]:
        """
        Streams resource to local spool file using 64 KB chunks, handling virus confirmation.
        Returns: (spool_path, sha256_hex, file_size_bytes, canonical_mime_type)
        """
        # If offline preferred, attempt local cache first
        if self.prefer_offline:
            cached_path = self.find_local_cached_file(resource_info)
            if cached_path:
                return self._hash_local_file(cached_path, resource_info)

        # Attempt online download if requests is available
        if REQUESTS_AVAILABLE:
            try:
                return self._download_online_requests(resource_info)
            except Exception as e:
                logger.warning(f"Online download failed for {resource_info.resource_id}: {e}. Trying local cache fallback.")
        
        # Fallback to local mirrored cache
        cached_path = self.find_local_cached_file(resource_info)
        if cached_path:
            return self._hash_local_file(cached_path, resource_info)

        raise GDriveStreamError(
            f"Failed to stream Google Drive resource {resource_info.resource_id} online, and no local cache was found."
        )

    def _download_online_requests(self, resource_info: GDriveResourceInfo) -> Tuple[Path, str, int, str]:
        """Streams HTTP response via requests.Session, bypassing virus confirmation page."""
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        url = resource_info.download_url
        response = session.get(url, stream=True, timeout=self.timeout_seconds)
        
        # Detect virus scan confirmation HTML interstitial
        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type and resource_info.resource_type == "file":
            html_text = response.text
            confirm_token = None
            # Check cookies
            for k, v in session.cookies.items():
                if k.startswith("download_warning"):
                    confirm_token = v
                    break
            # Check HTML forms/links
            if not confirm_token:
                m = re.search(r'href="(/uc\?export=download[^"]*confirm=([^"&]+)[^"]*)"', html_text)
                if m:
                    confirm_token = m.group(2)
            if not confirm_token:
                m = re.search(r'name="confirm"\s+value="([^"]+)"', html_text)
                if m:
                    confirm_token = m.group(1)

            if confirm_token:
                url = f"https://drive.google.com/uc?export=download&id={resource_info.resource_id}&confirm={confirm_token}"
                response = session.get(url, stream=True, timeout=self.timeout_seconds)

        response.raise_for_status()

        # Infer MIME type from headers
        resp_mime = response.headers.get("Content-Type", "").split(";")[0].strip()
        if not resp_mime or resp_mime == "application/octet-stream":
            resp_mime = resource_info.inferred_mime_type or "application/octet-stream"

        # Stream into temporary spool file in 64 KB chunks
        spool_file = self.spool_dir / f"spool_{resource_info.resource_id}_{os.getpid()}.bin"
        hasher = hashlib.sha256()
        total_bytes = 0

        with open(spool_file, "wb") as f_out:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    hasher.update(chunk)
                    f_out.write(chunk)
                    total_bytes += len(chunk)

        sha256_hex = hasher.hexdigest().lower()
        return spool_file, sha256_hex, total_bytes, resp_mime

    def _hash_local_file(self, local_path: Path, resource_info: GDriveResourceInfo) -> Tuple[Path, str, int, str]:
        """Computes SHA-256 and size from local cached file in 64 KB blocks."""
        hasher = hashlib.sha256()
        total_bytes = 0
        
        with open(local_path, "rb") as f_in:
            while True:
                chunk = f_in.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
                total_bytes += len(chunk)
                
        sha256_hex = hasher.hexdigest().lower()
        
        # Determine MIME type
        mime, _ = mimetypes.guess_type(str(local_path))
        if not mime:
            ext = local_path.suffix.lower()
            if ext == ".docx":
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ext == ".csv":
                mime = "text/csv"
            elif ext == ".pdf":
                mime = "application/pdf"
            else:
                mime = resource_info.inferred_mime_type or "application/octet-stream"

        return local_path, sha256_hex, total_bytes, mime

    def ingest_url(self, url_or_id: str) -> IngestedArtifact:
        """
        Main entrypoint: parses URL, streams binary, and returns IngestedArtifact.
        """
        info = self.parse_url(url_or_id)
        if info.resource_type == "folder":
            raise GDriveStreamError("Folder URLs must be traversed using ingest_folder generator.")

        spool_or_local_path, sha256_hex, file_size, mime = self.stream_to_spool(info)
        
        def stream_factory() -> BinaryIO:
            return open(spool_or_local_path, "rb")

        return IngestedArtifact(
            artifact_id=sha256_hex,
            source_uri=info.original_url,
            mime_type=mime,
            file_size_bytes=file_size,
            raw_stream_factory=stream_factory,
            metadata={
                "gdrive_id": info.resource_id,
                "resource_type": info.resource_type,
                "export_format": info.export_format,
                "spool_path": str(spool_or_local_path)
            }
        )

    def ingest_urls(self, urls: List[str]) -> Iterator[IngestedArtifact]:
        """Streams and yields IngestedArtifact instances for a list of URLs."""
        for url in urls:
            try:
                yield self.ingest_url(url)
            except Exception as e:
                logger.error(f"Failed to ingest GDrive URL {url}: {e}")
