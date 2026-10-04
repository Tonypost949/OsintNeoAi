import os
import json
import hashlib
from datetime import datetime

class OneDriveConnector:
    """Consolidated OneDrive directory forensic crawler and local folder indexer."""
    
    DEFAULT_ONEDRIVE_PATHS = [
        r"C:\Users\HP\OneDrive",
        r"C:\Users\HP\OneDrive - Post University,inc"
    ]
    
    TEXT_EXTENSIONS = {".txt", ".md", ".json", ".ini", ".conf", ".log"}
    SHEET_EXTENSIONS = {".csv", ".xlsx", ".xls"}
    DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".doc"}
    
    EXCLUSIONS = {
        "node_modules", ".venv", "appdata", "bin", "obj", ".git", ".gradle",
        "me_pe_log", "memu", ".vmdk", ".exe", ".msi", ".dll", ".zip", ".old"
    }

    def __init__(self, target_folders=None, index_file='onedrive_ingestion_index.json'):
        self.target_folders = target_folders or self.DEFAULT_ONEDRIVE_PATHS
        self.index_file = index_file
        self.processed_index = self.load_index()

    def load_index(self):
        """Load previously processed file index if available."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[OneDrive] Error loading index: {e}")
                return {}
        return {}

    def save_index(self):
        """Persist index state back to local disk."""
        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.processed_index, f, indent=2)
        except Exception as e:
            print(f"[OneDrive] Error saving index: {e}")

    def should_skip(self, file_path):
        """Exclusion filter to keep indexing clean and performance fast."""
        path_lower = file_path.lower()
        for kw in self.EXCLUSIONS:
            if kw in path_lower:
                return True
        return False

    def scan(self, force_reindex=False):
        """Recursively scan target folders, generating metadata summaries for target file types."""
        indexed_count = 0
        skipped_count = 0
        scanned_files = []
        
        for folder in self.target_folders:
            if not os.path.exists(folder):
                print(f"[OneDrive] Target folder not found: {folder}")
                continue
                
            print(f"[OneDrive] Scanning recursive directory: {folder}")
            for root, dirs, files in os.walk(folder):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if self.should_skip(file_path):
                        skipped_count += 1
                        continue
                        
                    ext = os.path.splitext(filename)[1].lower()
                    is_target_type = (
                        ext in self.TEXT_EXTENSIONS or
                        ext in self.SHEET_EXTENSIONS or
                        ext in self.DOCUMENT_EXTENSIONS
                    )
                    
                    if not is_target_type:
                        continue
                        
                    try:
                        stat = os.stat(file_path)
                        modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        file_size = stat.st_size
                        
                        # Generate unique identification hash of file path
                        file_id = hashlib.sha256(file_path.encode('utf-8')).hexdigest()
                        
                        # Check index cache to avoid re-calculating unless forced or modified
                        cached = self.processed_index.get(file_id)
                        if cached and cached.get('modified_time') == modified_time and not force_reindex:
                            scanned_files.append(cached)
                            continue
                            
                        # Catalog new or modified record
                        record = {
                            "id": file_id,
                            "path": file_path,
                            "name": filename,
                            "extension": ext,
                            "size_bytes": file_size,
                            "modified_time": modified_time,
                            "ingested_at": datetime.utcnow().isoformat()
                        }
                        
                        self.processed_index[file_id] = record
                        scanned_files.append(record)
                        indexed_count += 1
                        
                    except Exception as e:
                        print(f"[OneDrive] Error indexing {file_path}: {e}")
                        
        self.save_index()
        print(f"[OneDrive] Scan complete. Indexed: {indexed_count}, Skipped: {skipped_count}, Total: {len(scanned_files)}")
        return scanned_files
