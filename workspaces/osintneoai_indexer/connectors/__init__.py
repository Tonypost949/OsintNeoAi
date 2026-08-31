"""
OsintNeoAi Indexer: Connectors Subsystem
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\connectors\\__init__.py
"""

from .local_crawler import (
    CrawlStats,
    IngestedArtifact,
    LocalCrawler,
    ManagedTarStream,
    ManagedZipStream,
    crawl_local_files,
    detect_mime_type,
)
from .gdrive_streamer import (
    GDriveResourceInfo,
    GDriveStreamError,
    GDriveStreamer,
)
from .mailbox_reader import (
    EmailMetadata,
    MailboxReader,
    MailboxReaderError,
)

__all__ = [
    "CrawlStats",
    "EmailMetadata",
    "GDriveResourceInfo",
    "GDriveStreamError",
    "GDriveStreamer",
    "IngestedArtifact",
    "LocalCrawler",
    "MailboxReader",
    "MailboxReaderError",
    "ManagedTarStream",
    "ManagedZipStream",
    "crawl_local_files",
    "detect_mime_type",
]
