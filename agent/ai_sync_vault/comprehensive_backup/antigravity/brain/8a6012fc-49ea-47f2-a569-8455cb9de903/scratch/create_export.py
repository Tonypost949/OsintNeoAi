import os
import tarfile
from pathlib import Path

# Paths
source_dir = Path(r"c:\Users\HP\OneDrive\Documents\OsintNeoAi")
output_archive = Path(r"c:\Users\HP\OneDrive\Documents\OSINT-NeoAI-Manus-Export.tar.gz")

readme_content = """# 📦 OSINT NeoAI - Complete Export Package

This package contains the complete Manus OSINT NeoAI project for handoff.

### Setup Instructions

```bash
tar -xzf OSINT-NeoAI-Manus-Export.tar.gz
cd OSINT-NeoAI-web
pnpm install
pnpm dev
```
"""

todo_content = """# 📋 OSINT NeoAI - TODO List

- [x] Full database schema (analyses, entities, relationships, files, reports)
- [x] Backend infrastructure (tRPC routers, database helpers, entity extraction)
- [x] Landing page with hero section
- [x] Dual-theme system (newspaper light + Matrix dark)
- [x] Theme toggle component
- [x] D3.js network visualization component
- [x] Vanilla CSS (no Tailwind bloat)
- [x] File processing utilities
- [x] LLM integration ready
- [ ] S3 file storage integration
- [ ] End-to-end file upload pipeline
- [ ] Entity filtering and search
- [ ] CSV export functionality
- [ ] Report generation
- [ ] Mobile responsive polish
"""

def should_ignore(path: Path):
    # Ignore list
    parts = path.parts
    for p in parts:
        if p in [
            "node_modules", ".git", ".manus-logs", ".venv", "__pycache__", 
            "github_backups", ".manus", "uploads", ".backup_sync_status.json"
        ]:
            return True
            
    # File patterns to exclude
    if path.is_file():
        name = path.name
        if name.endswith(".zip") or name.endswith(".tar.gz") or name.endswith(".xlsx") or name.endswith(".xlsb"):
            if name not in ["business_workbook.xlsx", "people_data_system.xlsx"]:
                return True
    return False

def main():
    print("[*] Creating tar.gz archive directly...")
    if output_archive.exists():
        output_archive.unlink()
        
    errors = 0
    with tarfile.open(output_archive, "w:gz") as tar:
        # Recursively scan and add files
        for root, dirs, files in os.walk(source_dir):
            root_path = Path(root)
            if should_ignore(root_path):
                continue
                
            for file in files:
                file_path = root_path / file
                if should_ignore(file_path):
                    continue
                    
                # Calculate relative path to place it inside "OSINT-NeoAI-web" folder in tar
                rel_path = file_path.relative_to(source_dir)
                archive_name = Path("OSINT-NeoAI-web") / rel_path
                
                try:
                    tar.add(file_path, arcname=str(archive_name))
                except Exception as e:
                    print(f"[!] Warning: Skipping {rel_path} due to error: {e}")
                    errors += 1
                    
        # Write metadata files directly to tar
        print("[*] Injecting handoff metadata docs...")
        
        # Write README
        readme_file = Path("readme_temp.md")
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
        tar.add(readme_file, arcname="OSINT-NeoAI-web/OSINT-NeoAI-EXPORT-README.md")
        readme_file.unlink()
        
        # Write TODO
        todo_file = Path("todo_temp.md")
        with open(todo_file, "w", encoding="utf-8") as f:
            f.write(todo_content)
        tar.add(todo_file, arcname="OSINT-NeoAI-web/OSINT-NeoAI-TODO.md")
        todo_file.unlink()
        
    print(f"[SUCCESS] Export package created at: {output_archive} (Warnings/Skipped files: {errors})")

if __name__ == "__main__":
    main()
