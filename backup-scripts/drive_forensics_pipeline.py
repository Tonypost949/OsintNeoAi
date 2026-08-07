"""
Google Drive Forensics Pipeline for amd949609@gmail.com
Scans entire Drive, extracts file metadata + text content, loads to BigQuery.

Usage:
  python drive_forensics_pipeline.py

On first run, it opens a device auth URL in your browser.
Visit the URL, sign in as amd949609@gmail.com, enter the code.
"""

import os, sys, json, re, io, time, base64, logging
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

# Google API
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import bigquery

# ─── CONFIG ─────────────────────────────────────────────────────────────────

SCOPE_LABEL = "drive_scan_amd949609"
DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.file"]

BQ_PROJECT = "project-743aab84-f9a5-4ec7-954"
BQ_DATASET = "drive_forensics"
BQ_TABLE = "drive_documents"

AGENT_DIR = Path(__file__).resolve().parent.parent / "agent"

BATCH_SIZE = 50
MAX_RETRIES = 5
PAGE_SIZE = 200

RELEVANT_KEYWORDS = [
    "edr", "environmental", "huntington", "beach", "groundwater",
    "contamination", "plume", "perchlorate", "chromium", "shea",
    "cameron", "navigation center", "mercy house", "phase i",
    "phase ii", "site assessment", "geotracker", "water board",
    "cleanup", "hazardous", "tank", "ust", "deed restriction",
    "brownfield", "remediation", "soil", "vapor", "well",
    "aquifer", "monitoring", "water quality", "hb", "nav center",
    "17631", "17642", "17672", "17661", "17641", "7942",
    "speer", "kukui", "liberty", "slater", "rico", "hbnc",
    "toxic", "lawsuit", "demand letter", "cela", "prop 65",
    "safe drinking water", "mercy", "yamada", "wintersburg",
    "navigation", "ochca", "lmihaf", "form 700", "qui tam",
    "fca", "whistleblower", "cr vi", "hexavalent", "cr-vi",
    "chromium-6", "chromium 6", "pfas", "forensic", "osint",
    "shelter", "homeless", "beds", "permit", "violation",
    "hazmat", "waste", "underground", "storage tank", "luster",
    "swrcb", "rwqcb", "epa", "dtsc", "prop 65", "cela action",
    "clean water", "safe water", "mcl", "maximum contaminant",
]

TEXT_MIMES = {
    "text/plain", "text/csv", "text/html", "text/xml",
    "application/json", "application/xml", "application/javascript",
    "application/rtf",
}
GOOGLE_DOC_MIMES = {
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
}
EXTRACT_MIMES = TEXT_MIMES | GOOGLE_DOC_MIMES | {"application/pdf"}

# ─── LOGGING ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(TOKEN_DIR / "drive_scan.log", mode="a"),
    ],
)
log = logging.getLogger("drive_forensics")

# ─── AUTH ───────────────────────────────────────────────────────────────────

def get_authenticated_service() -> tuple:
    """Get Drive service and user email via device OAuth."""
    import sys as _sys
    _sys.path.insert(0, str(AGENT_DIR))
    from auth_helper import authenticate

    DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.readonly",
                    "https://www.googleapis.com/auth/drive.metadata.readonly"]
    creds = authenticate("Drive (forensics)", DRIVE_SCOPES, "token_drive_forensics.json")

    drive_service = build("drive", "v3", credentials=creds)
    about = drive_service.about().get(fields="user").execute()
    user_email = about.get("user", {}).get("emailAddress", "unknown")
    log.info("Authenticated as: %s", user_email)

    return drive_service, user_email, creds


# ─── DRIVE SCANNER ──────────────────────────────────────────────────────────

def scan_drive_files(drive_service) -> list:
    """List ALL files in Drive, handling pagination. Returns list of file dicts."""
    files = []
    page_token = None
    page_count = 0

    fields = "files(id,name,mimeType,size,createdTime,modifiedTime,parents,trashed,webViewLink,md5Checksum,owners/lastModifyingUser/capabilities/shared,permissionIds),nextPageToken"

    while True:
        page_count += 1
        try:
            request = drive_service.files().list(
                pageSize=PAGE_SIZE,
                fields=fields,
                orderBy="modifiedTime desc",
                q="trashed=false",
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            response = request.execute()
        except HttpError as e:
            if e.resp.status == 403:
                log.warning("Rate limited. Sleeping 30s...")
                time.sleep(30)
                continue
            elif e.resp.status == 429:
                log.warning("Quota exceeded. Sleeping 60s...")
                time.sleep(60)
                continue
            else:
                raise

        batch = response.get("files", [])
        files.extend(batch)
        log.info("Page %d: fetched %d files (total: %d)", page_count, len(batch), len(files))

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return files


# ─── FILE CONTENT EXTRACTION ────────────────────────────────────────────────

def extract_content(drive_service, file_id: str, mime_type: str, creds) -> Optional[str]:
    """Extract text content from a file."""
    try:
        if mime_type == "application/vnd.google-apps.document":
            request = drive_service.files().export_media(fileId=file_id, mimeType="text/plain")
            data = request.execute()
            return data.decode("utf-8", errors="replace")[:50000]

        elif mime_type == "application/vnd.google-apps.spreadsheet":
            request = drive_service.files().export_media(fileId=file_id, mimeType="text/csv")
            data = request.execute()
            text = data.decode("utf-8", errors="replace")[:50000]
            return text

        elif mime_type == "application/pdf":
            request = drive_service.files().get_media(fileId=file_id)
            data = request.execute()
            raw = data[:50000]
            text_parts = []
            for match in re.finditer(rb'\((.*?)\)', raw):
                decoded = match.group(1).decode("latin-1", errors="replace")
                if len(decoded) > 3 and all(32 <= ord(c) < 127 or c in " \n\r\t" for c in decoded):
                    text_parts.append(decoded)
            return "\n".join(text_parts)[:50000] if text_parts else None

        elif mime_type in TEXT_MIMES:
            request = drive_service.files().get_media(fileId=file_id)
            data = request.execute()
            return data.decode("utf-8", errors="replace")[:50000]

    except HttpError as e:
        if e.resp.status in (403, 404, 410):
            return None
        log.warning("  Extract error for %s: %s", file_id, str(e)[:100])
    except Exception as e:
        log.warning("  Extract error for %s: %s", file_id, str(e)[:100])

    return None


# ─── BIGQUERY ───────────────────────────────────────────────────────────────

def ensure_bq_table(bq_client):
    """Create dataset and table if they don't exist."""
    dataset_ref = bigquery.DatasetReference(BQ_PROJECT, BQ_DATASET)

    try:
        bq_client.get_dataset(dataset_ref)
        log.info("Dataset %s exists.", BQ_DATASET)
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        bq_client.create_dataset(dataset)
        log.info("Created dataset %s", BQ_DATASET)

    table_ref = dataset_ref.table(BQ_TABLE)
    schema = [
        bigquery.SchemaField("file_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("mime_type", "STRING"),
        bigquery.SchemaField("size_bytes", "INTEGER"),
        bigquery.SchemaField("created_time", "TIMESTAMP"),
        bigquery.SchemaField("modified_time", "TIMESTAMP"),
        bigquery.SchemaField("web_view_link", "STRING"),
        bigquery.SchemaField("md5_checksum", "STRING"),
        bigquery.SchemaField("is_relevant", "BOOLEAN"),
        bigquery.SchemaField("content_preview", "STRING"),
        bigquery.SchemaField("parent_ids", "STRING", mode="REPEATED"),
        bigquery.SchemaField("owner_email", "STRING"),
        bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("scan_account", "STRING", mode="REQUIRED"),
    ]

    try:
        table = bq_client.get_table(table_ref)
        log.info("Table %s exists (%d rows)", BQ_TABLE, table.num_rows)
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        bq_client.create_table(table)
        log.info("Created table %s", BQ_TABLE)

    return table_ref


def is_relevant(file_name: str) -> bool:
    name_lower = file_name.lower()
    return any(kw in name_lower for kw in RELEVANT_KEYWORDS)


def main():
    log.info("=" * 60)
    log.info("GOOGLE DRIVE FORENSICS PIPELINE")
    log.info("Account: amd949609@gmail.com")
    log.info("Target:  %s:%s.%s", BQ_PROJECT, BQ_DATASET, BQ_TABLE)
    log.info("=" * 60)

    # Step 1: Auth
    log.info("\n[1/5] Authenticating with Drive API...")
    drive_service, user_email, creds = get_authenticated_service()

    # Step 2: BigQuery setup
    log.info("\n[2/5] Setting up BigQuery table...")
    bq_client = bigquery.Client(project=BQ_PROJECT)
    table_ref = ensure_bq_table(bq_client)

    # Step 3: Scan files
    log.info("\n[3/5] Scanning Drive (this may take a while)...")
    all_files = scan_drive_files(drive_service)
    log.info("Total files found: %d", len(all_files))

    # Step 4: Process and extract
    log.info("\n[4/5] Processing files and extracting content...")
    relevant_count = 0
    batch_rows = []
    total_rows = 0
    start_time = time.time()

    for idx, f in enumerate(all_files):
        fid = f.get("id")
        name = f.get("name", "unnamed")
        mime = f.get("mimeType", "unknown")
        rel = is_relevant(name)

        row = {
            "file_id": fid,
            "file_name": name,
            "mime_type": mime,
            "size_bytes": int(f.get("size", 0)) if f.get("size") else None,
            "created_time": f.get("createdTime"),
            "modified_time": f.get("modifiedTime"),
            "web_view_link": f.get("webViewLink"),
            "md5_checksum": f.get("md5Checksum"),
            "is_relevant": rel,
            "content_preview": None,
            "parent_ids": f.get("parents", []),
            "owner_email": user_email,
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            "scan_account": "amd949609@gmail.com",
        }

        # Extract content for relevant files + text-based types
        if rel or mime in EXTRACT_MIMES:
            snippet = extract_content(drive_service, fid, mime, creds)
            if snippet:
                row["content_preview"] = snippet[:50000]

        if rel:
            relevant_count += 1
            if relevant_count <= 5:
                log.info("  RELEVANT: %s (%s)", name, mime)

        batch_rows.append(row)
        total_rows += 1

        if len(batch_rows) >= BATCH_SIZE:
            errors = bq_client.insert_rows_json(table_ref, batch_rows)
            if errors:
                log.warning("  BQ insert errors: %s", errors[:3])
            else:
                log.info("  Inserted %d rows (total: %d)", len(batch_rows), total_rows)
            batch_rows = []
            elapsed = time.time() - start_time
            rate = total_rows / elapsed if elapsed > 0 else 0
            log.info("  Progress: %d/%d files, %.1f files/sec", total_rows, len(all_files), rate)

        if (idx + 1) % 100 == 0:
            pct = (idx + 1) / len(all_files) * 100
            log.info("  Progress: %d/%d (%.1f%%)", idx + 1, len(all_files), pct)

    # Final batch
    if batch_rows:
        errors = bq_client.insert_rows_json(table_ref, batch_rows)
        if errors:
            log.warning("  BQ insert errors: %s", errors[:3])
        else:
            log.info("  Inserted final %d rows", len(batch_rows))

    # Step 5: Summary
    log.info("\n[5/5] SCAN COMPLETE")
    elapsed = time.time() - start_time
    log.info("  Total files: %d", total_rows)
    log.info("  Relevant files flagged: %d", relevant_count)
    log.info("  Elapsed: %.1f minutes", elapsed / 60)
    log.info("  Rate: %.1f files/sec", total_rows / elapsed if elapsed > 0 else 0)
    log.info("  Destination: %s:%s.%s", BQ_PROJECT, BQ_DATASET, BQ_TABLE)
    log.info("  Log: %s", TOKEN_DIR / "drive_scan.log")

    # Save file list as JSON backup
    backup_file = TOKEN_DIR / f"drive_filelist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, "w") as f:
        json.dump([{
            "id": ff["id"],
            "name": ff.get("name"),
            "mime": ff.get("mimeType"),
            "size": ff.get("size"),
            "modified": ff.get("modifiedTime"),
            "relevant": is_relevant(ff.get("name", "")),
        } for ff in all_files], f, indent=2)
    log.info("File list backup: %s", backup_file)


if __name__ == "__main__":
    main()
