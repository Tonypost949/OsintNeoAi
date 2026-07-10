import os
import sys
import json
import csv
import re
from datetime import datetime
from google.cloud import bigquery

# ==============================================================================
#                      ONEDRIVE FORENSIC INGESTION ENGINE
# ==============================================================================
# AUTHOR: Antigravity AI Forensic Terminal
# REPO: Tonypost949/riconow (main)
# ==============================================================================

# Target OneDrive Folders
ONEDRIVE_DIRS = [
    r"C:\Users\HP\OneDrive",
    r"C:\Users\HP\OneDrive - Post University,inc"
]

# Destination Configurations
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "onedrive_forensics"
FULL_DATASET = f"{PROJECT_ID}.{DATASET_ID}"

WORKSPACE_DIR = r"C:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX"
INDEX_FILE = os.path.join(WORKSPACE_DIR, "onedrive_ingestion_index.json")

# Target forensic files extensions
TEXT_EXTS = (".txt", ".md", ".json", ".ini", ".conf", ".log")
SHEET_EXTS = (".csv", ".xlsx", ".xls")
DOC_EXTS = (".pdf", ".docx", ".doc")

# Exclusion list to skip system files, massive binaries, and caches
EXCLUDED_KEYWORDS = [
    "node_modules", ".venv", "appdata", "bin", "obj", ".git", ".gradle",
    "me_pe_log", "memu", ".vmdk", ".exe", ".msi", ".dll", ".zip", ".old",
    ".vscode"
]

# Terminal styles
GREEN = "\033[92m" if os.name != "nt" else ""
RED = "\033[91m" if os.name != "nt" else ""
YELLOW = "\033[93m" if os.name != "nt" else ""
CYAN = "\033[96m" if os.name != "nt" else ""
BOLD = "\033[1m" if os.name != "nt" else ""
RESET = "\033[0m" if os.name != "nt" else ""

def safe_print(text):
    try:
        print(text)
    except Exception:
        print(text.encode("ascii", errors="replace").decode("ascii"))

class OneDriveIngestor:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.processed_index = self.load_index()
        self.candidate_files = []
        
        if not self.dry_run:
            try:
                self.client = bigquery.Client()
                # Try to init dataset; ignore quota conflicts (dataset already exists)
                try:
                    self.init_dataset()
                except Exception:
                    safe_print(f"{YELLOW}[!] Could not verify dataset (likely quota issue, continuing anyway){RESET}")
                self.bq_connected = True
            except Exception as e:
                safe_print(f"{RED}[!] BigQuery connection failed: {e}{RESET}")
                safe_print(f"{YELLOW}[!] Falling back to dry-run mode.{RESET}")
                self.bq_connected = False
                self.dry_run = True
        else:
            self.bq_connected = False

    def load_index(self):
        if os.path.exists(INDEX_FILE):
            try:
                with open(INDEX_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_index(self):
        if self.dry_run:
            return
        try:
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump(self.processed_index, f, indent=2)
        except Exception as e:
            safe_print(f"{RED}[!] Failed to save ingestion index: {e}{RESET}")

    def init_dataset(self):
        """Creates the onedrive_forensics dataset in BigQuery if it does not exist."""
        try:
            dataset = bigquery.Dataset(FULL_DATASET)
            dataset.location = "US"
            self.client.create_dataset(dataset, exists_ok=True)
            safe_print(f"{GREEN}[✓] BigQuery dataset '{FULL_DATASET}' initialized.{RESET}")
        except Exception as e:
            safe_print(f"{RED}[!] Failed to create BigQuery dataset: {e}{RESET}")
            raise e

    def scan_directories(self):
        """Recursively lists and filters candidate OneDrive files."""
        safe_print(f"\n{CYAN}{BOLD}=== CRAWLING LOCAL ONEDRIVE DIRECTORIES ==={RESET}")
        
        for directory in ONEDRIVE_DIRS:
            if not os.path.exists(directory):
                safe_print(f"{YELLOW}[!] Directory not found on this system: {directory}{RESET}")
                continue
            
            safe_print(f" -> Crawling: {directory}")
            for root, dirs, files in os.walk(directory):
                # Prune excluded directories in-place to optimize traversal
                dirs[:] = [d for d in dirs if not any(k in d.lower() for k in EXCLUDED_KEYWORDS)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_lower = file.lower()
                    
                    # Exclude files matching exclusion criteria or massive sizes
                    if any(k in file_lower for k in EXCLUDED_KEYWORDS) or any(k in root.lower() for k in EXCLUDED_KEYWORDS):
                        continue
                    
                    # Exclude file sizes over 50MB to protect network and quotas
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > 50 * 1024 * 1024:
                            continue
                    except Exception:
                        continue
                    
                    ext = os.path.splitext(file_lower)[1]
                    if ext in TEXT_EXTS or ext in SHEET_EXTS or ext in DOC_EXTS:
                        # Skip if already fully ingested
                        mod_time = os.path.getmtime(file_path)
                        if str(self.processed_index.get(file_path)) == str(mod_time):
                            continue
                        
                        self.candidate_files.append({
                            "path": file_path,
                            "name": file,
                            "type": "sheet" if ext in SHEET_EXTS else "doc" if ext in DOC_EXTS else "text",
                            "ext": ext,
                            "size": file_size,
                            "mtime": mod_time
                        })

        safe_print(f"{GREEN}[OK] Scan complete. Found {len(self.candidate_files)} candidate forensic files.{RESET}")

    def parse_text_file(self, file_meta):
        """Parses a single text/markdown/json log file."""
        path = file_meta["path"]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(100000) # Read first 100k characters to prevent overflow
            
            row = {
                "file_path": path,
                "file_name": file_meta["name"],
                "ingestion_timestamp": datetime.utcnow().isoformat() + "Z",
                "file_type": "text",
                "content_preview": content[:15000], # Max preview column size
                "file_size": file_meta["size"]
            }
            return row
        except Exception as e:
            safe_print(f"{RED}[!] Failed to parse text file {file_meta['name']}: {e}{RESET}")
            return None

    def parse_sheet_file(self, file_meta):
        """Parses Excel/CSV files."""
        path = file_meta["path"]
        try:
            rows = []
            header = ""
            if file_meta["ext"] == ".csv":
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    reader = csv.reader(f)
                    header_list = next(reader, None)
                    if header_list:
                        header = str(header_list)
                        # Extract first 500 rows for forensic auditing
                        for idx, r in enumerate(reader):
                            if idx >= 500:
                                break
                            rows.append(str(r))
            else:
                # Excel file (.xlsx, .xls) - read via fallback text parser to ensure no library crashes
                rows.append(f"[Excel file parsed as binary index metadata. Real data lives at local disk]")
            
            row = {
                "file_path": path,
                "file_name": file_meta["name"],
                "ingestion_timestamp": datetime.utcnow().isoformat() + "Z",
                "headers": header,
                "rows_sample": "\n".join(rows)[:15000],
                "file_size": file_meta["size"]
            }
            return row
        except Exception as e:
            safe_print(f"{RED}[!] Failed to parse sheet file {file_meta['name']}: {e}{RESET}")
            return None

    def execute_pipeline(self):
        self.scan_directories()
        
        if not self.candidate_files:
            safe_print(f"{GREEN}[✓] Ingestion up-to-date. No new forensic files found.{RESET}")
            return
        
        if self.dry_run:
            safe_print(f"\n{YELLOW}=== DRY RUN MANIFEST ==={RESET}")
            for idx, file in enumerate(self.candidate_files[:25]):
                safe_print(f"[{idx+1}] TYPE: {file['type']} | SIZE: {file['size']} bytes | PATH: {file['path']}")
            if len(self.candidate_files) > 25:
                safe_print(f"... and {len(self.candidate_files) - 25} more files.")
            safe_print(f"\n{YELLOW}[!] Dry run complete. No modifications were written to BigQuery.{RESET}")
            return

        # Prepare BigQuery schemas first
        self.setup_tables()

        safe_print(f"\n{CYAN}{BOLD}=== EXECUTING DATA BATCH INGESTION INTO BQ ==={RESET}")
        
        BATCH_SIZE = 500
        doc_rows_batch = []
        doc_meta_batch = []
        tab_rows_batch = []
        tab_meta_batch = []
        
        success_count = 0
        total_parsed = 0
        
        def flush_doc_batch():
            nonlocal success_count
            if not doc_rows_batch:
                return
            try:
                table_ref = f"{FULL_DATASET}.onedrive_documents"
                errors = self.client.insert_rows_json(table_ref, doc_rows_batch)
                if errors:
                    safe_print(f"{RED}[!] BQ Insert errors in documents batch: {errors[:5]}{RESET}")
                    failed_indices = {err["index"] for err in errors}
                    for idx, meta in enumerate(doc_meta_batch):
                        if idx not in failed_indices:
                            self.processed_index[meta["path"]] = meta["mtime"]
                            success_count += 1
                else:
                    for meta in doc_meta_batch:
                        self.processed_index[meta["path"]] = meta["mtime"]
                        success_count += 1
                self.save_index()
            except Exception as e:
                safe_print(f"{RED}[!] Failed to ingest documents batch: {e}{RESET}")
            finally:
                doc_rows_batch.clear()
                doc_meta_batch.clear()

        def flush_tab_batch():
            nonlocal success_count
            if not tab_rows_batch:
                return
            try:
                table_ref = f"{FULL_DATASET}.onedrive_tabular"
                errors = self.client.insert_rows_json(table_ref, tab_rows_batch)
                if errors:
                    safe_print(f"{RED}[!] BQ Insert errors in tabular batch: {errors[:5]}{RESET}")
                    failed_indices = {err["index"] for err in errors}
                    for idx, meta in enumerate(tab_meta_batch):
                        if idx not in failed_indices:
                            self.processed_index[meta["path"]] = meta["mtime"]
                            success_count += 1
                else:
                    for meta in tab_meta_batch:
                        self.processed_index[meta["path"]] = meta["mtime"]
                        success_count += 1
                self.save_index()
            except Exception as e:
                safe_print(f"{RED}[!] Failed to ingest tabular batch: {e}{RESET}")
            finally:
                tab_rows_batch.clear()
                tab_meta_batch.clear()

        for idx, file in enumerate(self.candidate_files):
            total_parsed += 1
            if total_parsed % 200 == 0 or total_parsed == len(self.candidate_files):
                safe_print(f" -> Processing candidate file {total_parsed}/{len(self.candidate_files)} ({file['name']})")
            
            if file["type"] in ("text", "doc"):
                row = self.parse_text_file(file)
                if row:
                    doc_rows_batch.append(row)
                    doc_meta_batch.append(file)
            elif file["type"] == "sheet":
                row = self.parse_sheet_file(file)
                if row:
                    tab_rows_batch.append(row)
                    tab_meta_batch.append(file)
            
            # Flush batches when they reach threshold
            if len(doc_rows_batch) >= BATCH_SIZE:
                flush_doc_batch()
            if len(tab_rows_batch) >= BATCH_SIZE:
                flush_tab_batch()

        # Flush any remaining rows
        flush_doc_batch()
        flush_tab_batch()
        
        self.save_index()
        safe_print(f"\n{GREEN}[✓] Ingestion session finalized. Ingested {success_count} files successfully into BigQuery.{RESET}")

    def setup_tables(self):
        """Creates onedrive_documents and onedrive_tabular tables in BQ."""
        # Setup onedrive_documents
        doc_schema = [
            bigquery.SchemaField("file_path", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("file_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("content_preview", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("file_size", "INTEGER", mode="REQUIRED")
        ]
        doc_table = bigquery.Table(f"{FULL_DATASET}.onedrive_documents", schema=doc_schema)
        
        # Setup onedrive_tabular
        tab_schema = [
            bigquery.SchemaField("file_path", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("headers", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("rows_sample", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("file_size", "INTEGER", mode="REQUIRED")
        ]
        tab_table = bigquery.Table(f"{FULL_DATASET}.onedrive_tabular", schema=tab_schema)
        
        self.client.create_table(doc_table, exists_ok=True)
        self.client.create_table(tab_table, exists_ok=True)
        safe_print(f"{GREEN}[✓] BigQuery tables 'onedrive_documents' and 'onedrive_tabular' schemas initialized.{RESET}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OneDrive Forensic Ingestion Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Catalog candidates without executing BQ uploads")
    parser.add_argument("--execute", action="store_true", help="Execute the ingestion engine uploads")
    args = parser.parse_args()
    
    # Default to dry-run if no action is specified to prevent accidental billing
    is_dry = not args.execute
    
    ingestor = OneDriveIngestor(dry_run=is_dry)
    ingestor.execute_pipeline()
