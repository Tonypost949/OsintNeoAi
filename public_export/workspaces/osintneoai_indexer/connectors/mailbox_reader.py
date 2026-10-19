"""
OsintNeoAi Indexer — Streaming Mailbox & EML Connector
Module: workspaces.osintneoai_indexer.connectors.mailbox_reader
Integrity: Zero-Memory-Bloat MBOX/EML Iterator, RFC 2047 MIME Header Decoding, Stream Attachment Hasher
"""

from __future__ import annotations

import email
import gc
import hashlib
import io
import json
import logging
import mailbox
import mimetypes
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email import policy
from email.header import decode_header
from email.utils import getaddresses, parseaddr, parsedate_to_datetime
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

logger = logging.getLogger("osintneoai.connectors.mailbox")

CHUNK_SIZE: int = 64 * 1024  # 64 KB block buffer


@dataclass(frozen=True)
class IngestedArtifact:
    artifact_id: str             # Canonical SHA-256 hex string (64 chars)
    source_uri: str              # Compound URI (e.g., 'mbox://path/file.mbox#msg_000001')
    mime_type: str               # Canonical MIME type
    file_size_bytes: int         # Exact file/payload size
    raw_stream_factory: Callable[[], BinaryIO] # Reusable stream factory
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class EmailMetadata:
    message_id: str
    subject: str
    sender_name: str
    sender_email: str
    recipients: List[Dict[str, str]]
    cc: List[Dict[str, str]]
    date_iso: Optional[str]
    date_raw: str
    in_reply_to: Optional[str]
    has_attachments: bool
    attachment_count: int


class MailboxReaderError(Exception):
    """Exception raised for mailbox parsing failures."""
    pass


class MailboxReader:
    """
    Streaming reader for Unix MBOX files (.mbox) and individual EML files (.eml, .msg),
    yielding IngestedArtifact instances for message bodies and attachments.
    """

    def __init__(self, spool_dir: Optional[Union[str, Path]] = None, gc_interval: int = 500):
        self.spool_dir = Path(spool_dir) if spool_dir else Path(tempfile.gettempdir()) / "osintneoai_mail_spool"
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        self.gc_interval = gc_interval

    @staticmethod
    def decode_mime_header(header_value: Optional[Union[str, bytes]]) -> str:
        """
        Decodes RFC 2047 MIME encoded header string across multiple charsets.
        """
        if not header_value:
            return ""
        if isinstance(header_value, bytes):
            try:
                header_value = header_value.decode("utf-8", errors="replace")
            except Exception:
                header_value = str(header_value)

        try:
            decoded_parts = decode_header(header_value)
            result = []
            for part, charset in decoded_parts:
                if isinstance(part, bytes):
                    encoding = charset or "utf-8"
                    try:
                        result.append(part.decode(encoding, errors="replace"))
                    except (LookupError, UnicodeDecodeError):
                        try:
                            result.append(part.decode("windows-1252", errors="replace"))
                        except Exception:
                            result.append(part.decode("iso-8859-1", errors="replace"))
                else:
                    result.append(str(part))
            return "".join(result).strip()
        except Exception:
            return str(header_value).strip()

    @staticmethod
    def parse_email_date(date_raw: Optional[str]) -> Optional[str]:
        """
        Normalizes RFC 2822 / 822 date string into canonical ISO 8601 UTC string.
        """
        if not date_raw or not date_raw.strip():
            return None
        
        cleaned = re.sub(r"\s*\([^)]*\)", "", date_raw).strip()
        
        try:
            dt = parsedate_to_datetime(cleaned)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass

        # Fallback date formats
        for fmt in (
            "%a, %d %b %Y %H:%M:%S %z",
            "%d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %Z",
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %I:%M:%S %p",
            "%Y-%m-%dT%H:%M:%S",
        ):
            try:
                dt = datetime.strptime(cleaned, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                continue

        return None

    def _extract_addresses(self, header_val: Optional[str]) -> List[Dict[str, str]]:
        """Parses address header into list of {name, email} dicts."""
        if not header_val:
            return []
        decoded = self.decode_mime_header(header_val)
        pairs = getaddresses([decoded])
        results = []
        for name, addr in pairs:
            name_clean = self.decode_mime_header(name).strip('"\' ')
            addr_clean = addr.strip().lower()
            if addr_clean or name_clean:
                results.append({"name": name_clean, "email": addr_clean})
        return results

    def parse_message_headers(self, msg: email.message.Message) -> EmailMetadata:
        """Extracts and normalizes RFC headers into EmailMetadata."""
        msg_id = (msg.get("Message-ID") or "").strip("<> \n\r")
        subject = self.decode_mime_header(msg.get("Subject", ""))
        
        from_hdr = msg.get("From", "")
        from_pairs = self._extract_addresses(from_hdr)
        sender_name = from_pairs[0]["name"] if from_pairs else ""
        sender_email = from_pairs[0]["email"] if from_pairs else ""
        
        recipients = self._extract_addresses(msg.get("To", ""))
        cc = self._extract_addresses(msg.get("Cc", ""))
        
        date_raw = str(msg.get("Date", ""))
        date_iso = self.parse_email_date(date_raw)
        
        in_reply_to = (msg.get("In-Reply-To") or "").strip("<> \n\r") or None
        
        # Check attachments
        has_attachments = False
        attachment_count = 0
        if msg.is_multipart():
            for part in msg.walk():
                disposition = part.get_content_disposition()
                filename = part.get_filename()
                if disposition in ("attachment", "inline") and filename:
                    has_attachments = True
                    attachment_count += 1

        return EmailMetadata(
            message_id=msg_id,
            subject=subject,
            sender_name=sender_name,
            sender_email=sender_email,
            recipients=recipients,
            cc=cc,
            date_iso=date_iso,
            date_raw=date_raw,
            in_reply_to=in_reply_to,
            has_attachments=has_attachments,
            attachment_count=attachment_count
        )

    def extract_body_content(self, msg: email.message.Message) -> Tuple[str, str, str]:
        """
        Extracts (plain_text, html_text, primary_body) from message tree.
        """
        plain_parts: List[str] = []
        html_parts: List[str] = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                disposition = part.get_content_disposition()
                
                # Skip explicit attachments
                if disposition == "attachment":
                    continue
                if part.get_filename():
                    continue

                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                charset = part.get_content_charset() or "utf-8"
                try:
                    text_decoded = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    try:
                        text_decoded = payload.decode("windows-1252", errors="replace")
                    except Exception:
                        text_decoded = payload.decode("iso-8859-1", errors="replace")

                if content_type == "text/plain":
                    plain_parts.append(text_decoded)
                elif content_type == "text/html":
                    html_parts.append(text_decoded)
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                try:
                    text_decoded = payload.decode(charset, errors="replace")
                except (LookupError, UnicodeDecodeError):
                    try:
                        text_decoded = payload.decode("windows-1252", errors="replace")
                    except Exception:
                        text_decoded = payload.decode("iso-8859-1", errors="replace")
                
                if msg.get_content_type() == "text/html":
                    html_parts.append(text_decoded)
                else:
                    plain_parts.append(text_decoded)

        plain_text = "\n".join(plain_parts).strip()
        html_text = "\n".join(html_parts).strip()
        primary_body = plain_text if plain_text else html_text

        return plain_text, html_text, primary_body

    def process_message(
        self,
        msg: email.message.Message,
        source_uri: str,
        message_index: int = 0
    ) -> Iterator[IngestedArtifact]:
        """
        Processes an individual email message, yielding IngestedArtifact for message body
        followed by an IngestedArtifact for each attachment.
        """
        headers = self.parse_message_headers(msg)
        plain_text, html_text, primary_body = self.extract_body_content(msg)
        
        # 1. Synthesize canonical message text & hash
        canonical_id_seed = headers.message_id if headers.message_id else f"{source_uri}_{message_index}_{headers.date_raw}"
        msg_hasher = hashlib.sha256()
        
        recipients_str = ", ".join(
            [f'{r.get("name", "")} <{r.get("email", "")}>'.strip() for r in headers.recipients]
        )
        
        # Represent email body as UTF-8 bytes
        email_body_bytes = (
            f"Subject: {headers.subject}\n"
            f"From: {headers.sender_name} <{headers.sender_email}>\n"
            f"To: {recipients_str}\n"
            f"Date: {headers.date_iso or headers.date_raw}\n"
            f"Message-ID: {headers.message_id}\n\n"
            f"{primary_body}"
        ).encode("utf-8")
        
        msg_hasher.update(email_body_bytes)
        msg_sha256 = msg_hasher.hexdigest().lower()
        msg_uri = f"{source_uri}#msg_{message_index:06d}"

        def msg_stream_factory() -> BinaryIO:
            return io.BytesIO(email_body_bytes)

        yield IngestedArtifact(
            artifact_id=msg_sha256,
            source_uri=msg_uri,
            mime_type="message/rfc822",
            file_size_bytes=len(email_body_bytes),
            raw_stream_factory=msg_stream_factory,
            metadata={
                "message_index": message_index,
                "message_id": headers.message_id,
                "subject": headers.subject,
                "sender": headers.sender_email,
                "sender_name": headers.sender_name,
                "recipients": [r["email"] for r in headers.recipients if r.get("email")],
                "normalized_date": headers.date_iso,
                "has_html": bool(html_text),
                "attachment_count": headers.attachment_count,
            }
        )

        # 2. Extract and yield attachments
        if msg.is_multipart():
            att_idx = 0
            for part in msg.walk():
                filename = part.get_filename()
                disposition = part.get_content_disposition()
                
                if not filename and disposition != "attachment":
                    continue
                if not filename:
                    filename = f"attachment_{att_idx}.bin"

                filename_decoded = self.decode_mime_header(filename)
                payload = part.get_payload(decode=True)
                if not payload:
                    continue

                att_idx += 1
                att_hasher = hashlib.sha256()
                att_hasher.update(payload)
                att_sha256 = att_hasher.hexdigest().lower()
                
                att_mime = part.get_content_type()
                if att_mime in ("application/octet-stream", None):
                    guessed, _ = mimetypes.guess_type(filename_decoded)
                    att_mime = guessed or "application/octet-stream"

                att_uri = f"{msg_uri}#att_{att_idx}_{filename_decoded}"
                
                # Closure capturing immutable payload bytes
                def make_att_factory(data: bytes) -> Callable[[], BinaryIO]:
                    return lambda: io.BytesIO(data)

                yield IngestedArtifact(
                    artifact_id=att_sha256,
                    source_uri=att_uri,
                    mime_type=att_mime,
                    file_size_bytes=len(payload),
                    raw_stream_factory=make_att_factory(payload),
                    metadata={
                        "parent_message_id": headers.message_id,
                        "parent_artifact_id": msg_sha256,
                        "filename": filename_decoded,
                        "attachment_index": att_idx,
                        "normalized_date": headers.date_iso
                    }
                )

    def read_mbox(self, mbox_path: Union[str, Path]) -> Iterator[IngestedArtifact]:
        """
        Lazily iterates through an MBOX file with constant memory usage.
        """
        mbox_path = Path(mbox_path)
        if not mbox_path.exists():
            raise MailboxReaderError(f"MBOX file not found: {mbox_path}")

        logger.info(f"Opening MBOX archive: {mbox_path}")
        mbox = mailbox.mbox(str(mbox_path), create=False)

        try:
            for i, msg in enumerate(mbox):
                try:
                    for artifact in self.process_message(msg, str(mbox_path), i):
                        yield artifact
                except Exception as e:
                    logger.warning(f"Error processing message #{i} in {mbox_path}: {e}")

                if (i + 1) % self.gc_interval == 0:
                    gc.collect()
        finally:
            mbox.close()

    def read_eml_file(self, eml_path: Union[str, Path]) -> Iterator[IngestedArtifact]:
        """
        Reads a standalone .eml or .msg file and yields IngestedArtifact instances.
        """
        eml_path = Path(eml_path)
        if not eml_path.exists():
            raise MailboxReaderError(f"EML file not found: {eml_path}")

        with open(eml_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
            
        for artifact in self.process_message(msg, str(eml_path), 0):
            yield artifact

    def read_mail_source(self, path_or_stream: Union[str, Path, BinaryIO]) -> Iterator[IngestedArtifact]:
        """
        Dispatches format based on file extension or stream.
        """
        if isinstance(path_or_stream, (str, Path)):
            p = Path(path_or_stream)
            suffix = p.suffix.lower()
            if suffix == ".mbox":
                return self.read_mbox(p)
            elif suffix in (".eml", ".msg"):
                return self.read_eml_file(p)
            else:
                # Attempt MBOX first, fallback to EML
                try:
                    return self.read_mbox(p)
                except Exception:
                    return self.read_eml_file(p)
        else:
            msg = email.message_from_binary_file(path_or_stream, policy=policy.default)
            return self.process_message(msg, "stream://raw_email", 0)
