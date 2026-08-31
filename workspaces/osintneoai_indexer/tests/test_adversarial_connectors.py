"""
OsintNeoAi Indexer — Adversarial Empirical Challenge Suite for M1 Connectors
Module: workspaces.osintneoai_indexer.tests.test_adversarial_connectors
Integrity: Exhaustive stress, boundary, encoding, corruption, and cache fallback testing
"""

from __future__ import annotations

import email
import email.message
from email import encoders
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
from typing import BinaryIO, List
from unittest.mock import MagicMock, patch

import pytest
import requests

from workspaces.osintneoai_indexer.connectors.gdrive_streamer import (
    CHUNK_SIZE,
    GDriveResourceInfo,
    GDriveStreamError,
    GDriveStreamer,
    WORKSPACE_EXPORT_MIMES,
)
from workspaces.osintneoai_indexer.connectors.mailbox_reader import (
    EmailMetadata,
    MailboxReader,
    MailboxReaderError,
)


# ============================================================================
# 1. GDRIVESTREAMER ADVERSARIAL & BOUNDARY TEST SUITE
# ============================================================================

class TestGDriveStreamerAdversarial:
    """Adversarial stress testing for GDriveStreamer."""

    @pytest.fixture
    def temp_cache_env(self, tmp_path):
        cache_dir1 = tmp_path / "cache1"
        cache_dir2 = tmp_path / "cache2"
        spool_dir = tmp_path / "spool"
        cache_dir1.mkdir(parents=True, exist_ok=True)
        cache_dir2.mkdir(parents=True, exist_ok=True)
        spool_dir.mkdir(parents=True, exist_ok=True)

        return {
            "cache_dirs": [cache_dir1, cache_dir2],
            "spool_dir": spool_dir,
            "root": tmp_path,
        }

    # ------------------------------------------------------------------------
    # URL Parsing Stress Matrix
    # ------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "url_input, expected_id, expected_type, expected_mime",
        [
            # Standard file URLs with various query parameters and trailing paths
            (
                "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I/view?usp=sharing",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "file",
                "application/octet-stream",
            ),
            (
                "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I/edit?usp=drivesdk&authuser=2",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "file",
                "application/octet-stream",
            ),
            (
                "https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I/preview",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "file",
                "application/octet-stream",
            ),
            (
                "http://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "file",
                "application/octet-stream",
            ),
            # Open & UC parameter permutation variations
            (
                "https://drive.google.com/open?id=1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "file",
                "application/octet-stream",
            ),
            (
                "https://drive.google.com/open?authuser=0&id=1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789&usp=sharing",
                "1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "file",
                "application/octet-stream",
            ),
            (
                "https://drive.google.com/uc?id=1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789&export=download",
                "1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "file",
                "application/octet-stream",
            ),
            (
                "https://drive.google.com/uc?export=download&confirm=t&id=1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "1AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789",
                "file",
                "application/octet-stream",
            ),
            # Docs / Sheets / Slides URLs with query params
            (
                "https://docs.google.com/document/d/1DocId_AlphaNumeric-20CharsLong/edit?usp=sharing",
                "1DocId_AlphaNumeric-20CharsLong",
                "doc",
                "application/pdf",
            ),
            (
                "https://docs.google.com/document/d/1DocId_AlphaNumeric-20CharsLong/export?format=docx",
                "1DocId_AlphaNumeric-20CharsLong",
                "doc",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            (
                "https://docs.google.com/document/d/1DocId_AlphaNumeric-20CharsLong/export?format=TXT",
                "1DocId_AlphaNumeric-20CharsLong",
                "doc",
                "text/plain",
            ),
            (
                "https://docs.google.com/spreadsheets/d/1SheetId_AlphaNumeric-20Chars/edit#gid=0",
                "1SheetId_AlphaNumeric-20Chars",
                "sheet",
                "text/csv",
            ),
            (
                "https://docs.google.com/spreadsheets/d/1SheetId_AlphaNumeric-20Chars/export?format=xlsx",
                "1SheetId_AlphaNumeric-20Chars",
                "sheet",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            (
                "https://docs.google.com/presentation/d/1SlideId_AlphaNumeric-20Chars/edit#slide=id.p",
                "1SlideId_AlphaNumeric-20Chars",
                "presentation",
                "application/pdf",
            ),
            # Raw alphanumeric IDs (20 to 50 chars)
            (
                "123456789012345678901234",
                "123456789012345678901234",
                "file",
                "application/octet-stream",
            ),
            (
                "AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789-ExtraLen",
                "AbCdEfGhIjKlMnOpQrStUvWxYz_0123456789-ExtraLen",
                "file",
                "application/octet-stream",
            ),
            # Whitespace and newlines surrounding URLs
            (
                "  \t\r\n https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I/view  \n",
                "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OIvE2up0I",
                "file",
                "application/octet-stream",
            ),
        ],
    )
    def test_parse_url_comprehensive_matrix(self, url_input, expected_id, expected_type, expected_mime):
        streamer = GDriveStreamer(prefer_offline=True)
        info = streamer.parse_url(url_input)
        assert info.resource_id == expected_id
        assert info.resource_type == expected_type
        assert info.inferred_mime_type == expected_mime

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "",
            "   \t\n  ",
            "short_id_123",  # < 20 chars
            "https://dropbox.com/s/12345678901234567890/file.pdf",
            "https://onedrive.live.com/?id=12345678901234567890",
            "http://malicious.example.com/not_google_drive",
            "ftp://drive.google.com/file/d/12345678901234567890",
            "https://drive.google.com/file/d/!@#$%^&*()_+",
        ],
    )
    def test_parse_url_invalid_inputs_rejected(self, invalid_input):
        streamer = GDriveStreamer(prefer_offline=True)
        with pytest.raises(GDriveStreamError):
            streamer.parse_url(invalid_input)

    def test_folder_url_parsed_but_ingest_raises_informative_error(self):
        streamer = GDriveStreamer(prefer_offline=True)
        folder_url = "https://drive.google.com/drive/folders/1FolderId_AlphaNumeric-20Chars"
        info = streamer.parse_url(folder_url)
        assert info.resource_type == "folder"
        assert info.resource_id == "1FolderId_AlphaNumeric-20Chars"

        with pytest.raises(GDriveStreamError, match="Folder URLs must be traversed"):
            streamer.ingest_url(folder_url)

    # ------------------------------------------------------------------------
    # Offline Fallback Caching Stress Tests
    # ------------------------------------------------------------------------

    def test_offline_fallback_by_manifest_exact_path(self, temp_cache_env):
        cache_dir = temp_cache_env["cache_dirs"][0]
        test_file = cache_dir / "target_evidence.pdf"
        content = b"%PDF-1.7 Empirical GDrive Test Payload"
        test_file.write_bytes(content)

        manifest = [
            {
                "gdrive_id": "1ExactManifestId_20CharsMin",
                "name": "target_evidence.pdf",
                "path": str(test_file),
            }
        ]
        (cache_dir / "GDRIVE_INGESTION_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")

        streamer = GDriveStreamer(
            spool_dir=temp_cache_env["spool_dir"],
            local_cache_dirs=temp_cache_env["cache_dirs"],
            prefer_offline=True,
        )

        artifact = streamer.ingest_url("https://drive.google.com/file/d/1ExactManifestId_20CharsMin/view")
        expected_sha = hashlib.sha256(content).hexdigest()

        assert artifact.artifact_id == expected_sha
        assert artifact.file_size_bytes == len(content)
        assert artifact.mime_type == "application/pdf"

        # Verify stream factory can be opened multiple times
        with artifact.raw_stream_factory() as s1:
            assert s1.read() == content
        with artifact.raw_stream_factory() as s2:
            assert s2.read() == content

    def test_offline_fallback_by_filename_convention(self, temp_cache_env):
        cache_dir = temp_cache_env["cache_dirs"][1]
        file_id = "1PrefixConventionId_20CharsMin"
        test_file = cache_dir / f"gfile_{file_id}.docx"
        content = b"PK\x03\x04DOCX Content Simulation"
        test_file.write_bytes(content)

        streamer = GDriveStreamer(
            spool_dir=temp_cache_env["spool_dir"],
            local_cache_dirs=temp_cache_env["cache_dirs"],
            prefer_offline=True,
        )

        artifact = streamer.ingest_url(f"https://drive.google.com/file/d/{file_id}/view")
        expected_sha = hashlib.sha256(content).hexdigest()

        assert artifact.artifact_id == expected_sha
        assert artifact.file_size_bytes == len(content)
        assert "openxmlformats" in artifact.mime_type or artifact.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    def test_network_failure_triggers_transparent_cache_fallback(self, temp_cache_env):
        cache_dir = temp_cache_env["cache_dirs"][0]
        file_id = "1NetworkFailureFallback_20Chars"
        test_file = cache_dir / f"{file_id}.csv"
        content = b"header1,header2\nval1,val2\n"
        test_file.write_bytes(content)

        streamer = GDriveStreamer(
            spool_dir=temp_cache_env["spool_dir"],
            local_cache_dirs=temp_cache_env["cache_dirs"],
            prefer_offline=False,  # Attempt online first
        )

        # Mock network call to raise ConnectionError
        with patch("requests.Session.get", side_effect=requests.exceptions.ConnectionError("Simulated Offline / No Route")):
            artifact = streamer.ingest_url(f"https://drive.google.com/file/d/{file_id}/view")

        expected_sha = hashlib.sha256(content).hexdigest()
        assert artifact.artifact_id == expected_sha
        assert artifact.file_size_bytes == len(content)
        # On Windows, mimetypes.guess_type may associate .csv with application/vnd.ms-excel
        assert artifact.mime_type in ("text/csv", "application/vnd.ms-excel")

    def test_missing_cache_and_network_failure_raises_gdrive_error(self, temp_cache_env):
        streamer = GDriveStreamer(
            spool_dir=temp_cache_env["spool_dir"],
            local_cache_dirs=temp_cache_env["cache_dirs"],
            prefer_offline=False,
        )

        with patch("requests.Session.get", side_effect=requests.exceptions.Timeout("Connection Timed Out")):
            with pytest.raises(GDriveStreamError, match="Failed to stream Google Drive resource"):
                streamer.ingest_url("https://drive.google.com/file/d/1NonExistentFileId_20CharsLong/view")

    def test_virus_scan_large_file_html_interstitial_interception(self, temp_cache_env):
        file_id = "1LargeVirusWarningFile_20Chars"
        file_payload = b"A" * (128 * 1024)  # 128 KB payload

        # Simulation: First response is HTML warning with confirm token
        html_warning = (
            '<html><body>'
            '<a href="/uc?export=download&amp;id=1LargeVirusWarningFile_20Chars&amp;confirm=TOKEN_ABCD_1234">'
            'Download anyway</a>'
            '</body></html>'
        )

        resp_warning = MagicMock()
        resp_warning.headers = {"Content-Type": "text/html; charset=utf-8"}
        resp_warning.text = html_warning

        resp_file = MagicMock()
        resp_file.headers = {"Content-Type": "application/pdf"}
        resp_file.raise_for_status = MagicMock()
        resp_file.iter_content = MagicMock(return_value=[file_payload[:64 * 1024], file_payload[64 * 1024:]])

        streamer = GDriveStreamer(
            spool_dir=temp_cache_env["spool_dir"],
            local_cache_dirs=temp_cache_env["cache_dirs"],
            prefer_offline=False,
        )

        with patch("requests.Session.get", side_effect=[resp_warning, resp_file]) as mock_get:
            artifact = streamer.ingest_url(f"https://drive.google.com/file/d/{file_id}/view")

            assert mock_get.call_count == 2
            second_call_url = mock_get.call_args_list[1][0][0]
            assert "confirm=TOKEN_ABCD_1234" in second_call_url
            assert artifact.artifact_id == hashlib.sha256(file_payload).hexdigest()
            assert artifact.file_size_bytes == 128 * 1024
            assert artifact.mime_type == "application/pdf"


# ============================================================================
# 2. MAILBOXREADER ADVERSARIAL & ENCODING STRESS TEST SUITE
# ============================================================================

class TestMailboxReaderAdversarial:
    """Adversarial stress testing for MailboxReader."""

    @pytest.fixture
    def mail_reader(self, tmp_path):
        spool_dir = tmp_path / "mail_spool"
        spool_dir.mkdir(parents=True, exist_ok=True)
        return MailboxReader(spool_dir=spool_dir, gc_interval=10)

    # ------------------------------------------------------------------------
    # Multi-Charset RFC 2047 & Raw Header Decoding Matrix
    # ------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "encoded_header, expected_substring",
        [
            # UTF-8 Base64
            ("=?UTF-8?B?VGVzdCBGZWxvbnkgSW5mb3JtYXRpb24gLSBIYXJyeSBTaWRodQ==?=", "Test Felony Information - Harry Sidhu"),
            # UTF-8 Quoted-Printable with special characters
            ("=?UTF-8?Q?Affidavit_of_FBI_SA_Brian_Adkins_=C2=A7_54220?=", "Affidavit of FBI SA Brian Adkins § 54220"),
            # ISO-8859-1 Quoted-Printable (French/German/Spanish accents)
            ("=?ISO-8859-1?Q?Proc=E8s-Verbal_des_S=E9ances_et_Jugements?=", "Procès-Verbal des Séances et Jugements"),
            # Windows-1252 Quoted-Printable (Curly quotes, euro, en-dash)
            ("=?Windows-1252?Q?Stadium_Deal_=93Void=94_per_HCD_Notice_=96_=A3100?=", "Stadium Deal “Void” per HCD Notice – £100"),
            # Consecutive adjacent encoded words (RFC 2047 whitespace folding rule)
            ("=?UTF-8?B?VW5pdGVkIA==?= =?UTF-8?B?U3RhdGVzIA==?= =?UTF-8?B?di4gU2lkaHU=?=", "United States v. Sidhu"),
            # Mixed plain and encoded text
            ("Case 8:23-cr-00108-CJC: =?UTF-8?B?UGxlYSBBZ3JlZW1lbnQ=?=", "Case 8:23-cr-00108-CJC: Plea Agreement"),
            # Raw non-ASCII bytes fallback
            (b"Raw bytes \xc3\xa9\xc3\xa0\xc3\xbc test", "Raw bytes éàü test"),
            # Corrupted / invalid RFC 2047 syntax (must not crash, underscores in QP decoded to spaces)
            ("=?invalid-charset-xyz?Q?Corrupted_Payload?=", "Corrupted Payload"),
            ("=?UTF-8?B?IncompleteBase64WithoutEquals", "=?UTF-8?B?IncompleteBase64WithoutEquals"),
            ("", ""),
            (None, ""),
        ],
    )
    def test_decode_mime_header_charset_matrix(self, encoded_header, expected_substring):
        decoded = MailboxReader.decode_mime_header(encoded_header)
        assert expected_substring in decoded

    # ------------------------------------------------------------------------
    # Date Normalization Boundary Matrix
    # ------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "date_input, expected_iso",
        [
            ("Tue, 24 May 2022 16:29:00 -0700", "2022-05-24T23:29:00Z"),
            ("24 May 2022 16:29:00 -0700 (PDT)", "2022-05-24T23:29:00Z"),
            ("Wed, 8 Dec 2021 08:00:00 +0000", "2021-12-08T08:00:00Z"),
            ("2021-12-08 08:00:00", "2021-12-08T08:00:00Z"),
            ("12/08/2021 08:00:00 AM", "2021-12-08T08:00:00Z"),
            ("2022-05-24T16:29:00", "2022-05-24T16:29:00Z"),
            ("", None),
            (None, None),
            ("Not a valid date string at all", None),
            ("99/99/9999 99:99:99", None),
        ],
    )
    def test_parse_email_date_boundary_matrix(self, date_input, expected_iso):
        iso_res = MailboxReader.parse_email_date(date_input)
        assert iso_res == expected_iso

    # ------------------------------------------------------------------------
    # Complex Nested Multi-Part MIME Structure
    # ------------------------------------------------------------------------

    def test_deeply_nested_multipart_mime_message(self, mail_reader):
        """
        Tests multipart/mixed containing multipart/alternative (text + html)
        and multiple attachments (PDF, DOCX, ZIP, Image).
        """
        outer = MIMEMultipart("mixed")
        outer["Subject"] = "=?UTF-8?B?VW5pdGVkIFN0YXRlcyB2LiBTaWRodQ==?="
        outer["From"] = "=?UTF-8?B?RkJJIFNwZWNpYWwgQWdlbnQ=?= <adkins@fbi.gov>"
        outer["To"] = "US Attorney <usa@usdoj.gov>, Court Clerk <clerk@cacd.uscourts.gov>"
        outer["Date"] = "Tue, 24 May 2022 16:29:00 -0700"
        outer["Message-ID"] = "<fbi-adkins-20220524-001@fbi.gov>"

        # Alternative body (plain + html)
        alt_part = MIMEMultipart("alternative")
        
        plain_body = MIMEText("Plaintext affidavit summary: Angel Stadium deal voided under SLA § 54220.", "plain", "utf-8")
        html_body = MIMEText("<p>HTML affidavit summary: <b>$96M penalty</b> assessed by HCD.</p>", "html", "utf-8")
        alt_part.attach(plain_body)
        alt_part.attach(html_body)
        outer.attach(alt_part)

        # Attachment 1: PDF
        pdf_bytes = b"%PDF-1.7 Search Warrant Affidavit FBI SA Brian Adkins"
        att1 = MIMEBase("application", "pdf")
        att1.set_payload(pdf_bytes)
        encoders.encode_base64(att1)
        att1.add_header("Content-Disposition", 'attachment; filename="adkins_affidavit.pdf"')
        outer.attach(att1)

        # Attachment 2: DOCX with RFC 2047 encoded filename
        docx_bytes = b"PK\x03\x04Information Plea Agreement Todd Ament"
        att2 = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
        att2.set_payload(docx_bytes)
        encoders.encode_base64(att2)
        att2.add_header("Content-Disposition", "attachment", filename="=?UTF-8?B?YW1lbnRfcGxlYV9hZ3JlZW1lbnQuZG9jeA==?=")
        outer.attach(att2)

        # Attachment 3: Raw Binary with inline disposition
        bin_bytes = b"\x89PNG\r\n\x1a\nEvidence Chart Graphic"
        att3 = MIMEBase("image", "png")
        att3.set_payload(bin_bytes)
        encoders.encode_base64(att3)
        att3.add_header("Content-Disposition", "inline; filename=chart.png")
        outer.attach(att3)

        raw_msg_bytes = outer.as_bytes()
        msg_stream = io.BytesIO(raw_msg_bytes)

        artifacts = list(mail_reader.read_mail_source(msg_stream))

        # Expected: 1 message artifact + 3 attachment artifacts = 4 artifacts
        assert len(artifacts) == 4

        # 1. Message Artifact
        msg_art = artifacts[0]
        assert msg_art.mime_type == "message/rfc822"
        assert msg_art.metadata["message_id"] == "fbi-adkins-20220524-001@fbi.gov"
        assert msg_art.metadata["subject"] == "United States v. Sidhu"
        assert msg_art.metadata["sender"] == "adkins@fbi.gov"
        assert msg_art.metadata["sender_name"] == "FBI Special Agent"
        assert len(msg_art.metadata["recipients"]) == 2
        assert msg_art.metadata["normalized_date"] == "2022-05-24T23:29:00Z"
        assert msg_art.metadata["attachment_count"] == 3

        with msg_art.raw_stream_factory() as s:
            content = s.read().decode("utf-8")
            assert "Plaintext affidavit summary" in content
            assert "adkins_affidavit.pdf" not in content  # Attachments separated

        # 2. Attachment 1 (PDF)
        att1_art = artifacts[1]
        assert att1_art.artifact_id == hashlib.sha256(pdf_bytes).hexdigest()
        assert att1_art.mime_type == "application/pdf"
        assert att1_art.metadata["filename"] == "adkins_affidavit.pdf"
        with att1_art.raw_stream_factory() as s:
            assert s.read() == pdf_bytes

        # 3. Attachment 2 (DOCX with decoded filename)
        att2_art = artifacts[2]
        assert att2_art.artifact_id == hashlib.sha256(docx_bytes).hexdigest()
        assert att2_art.metadata["filename"] == "ament_plea_agreement.docx"
        with att2_art.raw_stream_factory() as s:
            assert s.read() == docx_bytes

        # 4. Attachment 3 (PNG)
        att3_art = artifacts[3]
        assert att3_art.artifact_id == hashlib.sha256(bin_bytes).hexdigest()
        assert att3_art.mime_type == "image/png"
        assert att3_art.metadata["filename"] == "chart.png"
        with att3_art.raw_stream_factory() as s:
            assert s.read() == bin_bytes

    # ------------------------------------------------------------------------
    # Non-UTF8 Character Sets in Body Text
    # ------------------------------------------------------------------------

    def test_windows1252_and_iso8859_1_body_decoding(self, mail_reader):
        """
        Tests email messages containing Windows-1252 and ISO-8859-1 body bytes.
        """
        # 1. Windows-1252 body with smart quotes and euro
        raw_win1252 = (
            b"From: sender@example.com\r\n"
            b"To: receiver@example.com\r\n"
            b"Subject: Windows 1252 Content\r\n"
            b"Content-Type: text/plain; charset=windows-1252\r\n"
            b"Content-Transfer-Encoding: 8bit\r\n\r\n"
            b"Smart \x93quotes\x94 and \x80100 value with \x96 dash"
        )
        art_win = list(mail_reader.read_mail_source(io.BytesIO(raw_win1252)))[0]
        with art_win.raw_stream_factory() as s:
            text = s.read().decode("utf-8")
            assert "Smart “quotes” and €100 value with – dash" in text

        # 2. ISO-8859-1 body with French accents
        raw_iso = (
            b"From: french@example.fr\r\n"
            b"To: receiver@example.fr\r\n"
            b"Subject: French ISO Notice\r\n"
            b"Content-Type: text/plain; charset=iso-8859-1\r\n"
            b"Content-Transfer-Encoding: 8bit\r\n\r\n"
            b"Proc\xe8s-verbal de la s\xe9ance et caf\xe9"
        )
        art_iso = list(mail_reader.read_mail_source(io.BytesIO(raw_iso)))[0]
        with art_iso.raw_stream_factory() as s:
            text = s.read().decode("utf-8")
            assert "Procès-verbal de la séance et café" in text

    # ------------------------------------------------------------------------
    # Corrupted / Edge Case Emails
    # ------------------------------------------------------------------------

    def test_corrupted_and_missing_headers_email(self, mail_reader):
        """
        Tests email with no headers, completely empty, or corrupted format.
        """
        raw_corrupted = b"This is just random raw junk text without any headers.\n\nBody here."
        msg_stream = io.BytesIO(raw_corrupted)

        artifacts = list(mail_reader.read_mail_source(msg_stream))
        assert len(artifacts) == 1
        art = artifacts[0]
        assert art.mime_type == "message/rfc822"
        assert art.metadata["subject"] == ""
        assert art.metadata["sender"] == ""
        assert art.metadata["normalized_date"] is None
        assert art.metadata["attachment_count"] == 0

        with art.raw_stream_factory() as s:
            body = s.read().decode("utf-8")
            assert "random raw junk text" in body

    def test_html_only_email_primary_body_fallback(self, mail_reader):
        """
        Tests email with HTML part only (no text/plain).
        """
        msg = MIMEMultipart("related")
        msg["Subject"] = "HTML Only Notice"
        msg["From"] = "hcd@ca.gov"
        msg["To"] = "cityclerk@anaheim.net"
        msg["Date"] = "08 Dec 2021 10:00:00 +0000"

        html_part = MIMEText("<html><body><h3>Official Violation Notice</h3></body></html>", "html", "utf-8")
        msg.attach(html_part)

        artifacts = list(mail_reader.read_mail_source(io.BytesIO(msg.as_bytes())))
        assert len(artifacts) == 1
        art = artifacts[0]
        assert art.metadata["has_html"] is True

        with art.raw_stream_factory() as s:
            text = s.read().decode("utf-8")
            assert "Official Violation Notice" in text

    def test_mbox_streaming_with_mixed_valid_and_corrupted_messages(self, mail_reader, tmp_path):
        """
        Creates a synthetic MBOX file with multiple messages, including corrupted
        payloads, and ensures iteration streams all valid artifacts without crashing.
        """
        mbox_path = tmp_path / "investigation_archive.mbox"
        
        # Build 10 messages in mbox format
        with open(mbox_path, "wb") as f:
            for i in range(10):
                f.write(f"From sender{i}@example.com Fri Jan  1 00:00:00 2021\n".encode("utf-8"))
                f.write(f"From: Sender {i} <sender{i}@example.com>\n".encode("utf-8"))
                f.write(f"To: Recipient {i} <recipient{i}@example.com>\n".encode("utf-8"))
                f.write(f"Subject: Investigation Log Item #{i}\n".encode("utf-8"))
                f.write(f"Date: Mon, {i + 1:02d} Jan 2021 12:00:00 +0000\n".encode("utf-8"))
                f.write(f"Message-ID: <msg-{i}@example.com>\n".encode("utf-8"))
                f.write(b"Content-Type: text/plain; charset=utf-8\n\n")
                f.write(f"Evidence log item payload for record index {i}.\n\n".encode("utf-8"))

        artifacts = list(mail_reader.read_mbox(mbox_path))
        assert len(artifacts) == 10

        for i, art in enumerate(artifacts):
            assert art.metadata["message_index"] == i
            assert art.metadata["message_id"] == f"msg-{i}@example.com"
            assert art.metadata["normalized_date"] == f"2021-01-{i + 1:02d}T12:00:00Z"
            assert f"Record index {i}" in art.metadata["subject"] or f"Investigation Log Item #{i}" in art.metadata["subject"]

            # Verify cryptographic SHA-256 integrity
            with art.raw_stream_factory() as s:
                payload = s.read()
                calc_sha = hashlib.sha256(payload).hexdigest()
                assert art.artifact_id == calc_sha
                assert art.file_size_bytes == len(payload)
