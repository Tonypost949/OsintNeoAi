"""
OsintNeoAi Indexer: Continuous Streaming Cryptographic SHA-256 Hasher
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\storage\\hasher.py

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

# Default chunk size: 64 KB (65,536 bytes)
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
        return self._hasher.hexdigest().lower()

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
        super().__init__()
        self._stream = raw_stream
        self._hasher = hasher if hasher is not None else StreamHasher()

    def readable(self) -> bool:
        return hasattr(self._stream, "readable") and self._stream.readable() if hasattr(self._stream, "readable") else True

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

    def readinto(self, b) -> int:
        """Reads bytes directly into buffer and updates hash."""
        if hasattr(self._stream, "readinto"):
            n = self._stream.readinto(b)
            if n is not None and n > 0:
                self._hasher.update(bytes(b[:n]))
            return n if n is not None else 0
        else:
            chunk = self._stream.read(len(b))
            n = len(chunk)
            b[:n] = chunk
            if n > 0:
                self._hasher.update(chunk)
            return n

    def read(self, size: int = -1) -> bytes:
        """Reads chunk of bytes and updates running SHA-256."""
        chunk = self._stream.read(size)
        if chunk:
            self._hasher.update(chunk)
        return chunk or b""

    def close(self) -> None:
        super().close()
        if hasattr(self._stream, "close"):
            self._stream.close()

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

    def __enter__(self) -> HashingReader:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False


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
    return hashlib.sha256(data).hexdigest().lower()


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
    except (FileNotFoundError, PermissionError, IsADirectoryError, OSError):
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
