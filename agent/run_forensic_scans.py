"""
Master runner for Google forensic scans.
Runs: Drive metadata scan, Photos scan, Drive content extraction.
All data loads into BigQuery.

Usage:
  python run_forensic_scans.py

Each scanner will prompt for OAuth on first run (device flow).
Visit the printed URL, sign in as amd949609@gmail.com, enter the code.
"""

import os, sys, subprocess, time

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(AGENT_DIR)
BACKUP_SCRIPTS = os.path.join(REPO_DIR, "backup-scripts")

SCANNERS = [
    {
        "name": "Drive Metadata Scan",
        "path": os.path.join(AGENT_DIR, "scan_drive.py"),
        "target_table": "national_audits.drive_file_index",
        "description": "Scans ALL Drive files, indexes metadata to BigQuery",
    },
    {
        "name": "Google Photos Scan",
        "path": os.path.join(AGENT_DIR, "scan_google_photos.py"),
        "target_table": "national_audits.google_photos_index",
        "description": "Scans ALL Google Photos, indexes metadata to BigQuery",
    },
    {
        "name": "Drive Content Extraction",
        "path": os.path.join(BACKUP_SCRIPTS, "drive_forensics_pipeline.py"),
        "target_table": "drive_forensics.drive_documents",
        "description": "Extracts text content from Drive files, loads to BigQuery",
    },
]


def print_banner():
    print("=" * 65)
    print("  OSINTNeoAi FORENSIC SCAN RUNNER")
    print("  Account: amd949609@gmail.com")
    print("=" * 65)
    print()


def run_scanner(scanner):
    name = scanner["name"]
    path = scanner["path"]
    table = scanner["target_table"]
    desc = scanner["description"]

    print()
    print("#" * 65)
    print(f"#  {name}")
    print(f"#  Target: {table}")
    print(f"#  {desc}")
    print("#" * 65)
    print()

    if not os.path.exists(path):
        print(f"[!] Script not found: {path}")
        return False

    result = subprocess.run(
        [sys.executable, path],
        cwd=os.path.dirname(path),
        capture_output=False,
    )

    if result.returncode == 0:
        print(f"\n[OK] {name} completed successfully.\n")
        return True
    else:
        print(f"\n[FAIL] {name} exited with code {result.returncode}\n")
        return False


def main():
    print_banner()

    print(f"Found {len(SCANNERS)} scanners to run:")
    for i, s in enumerate(SCANNERS, 1):
        print(f"  {i}. {s['name']} -> {s['target_table']}")
    print()

    success = 0
    fail = 0

    for scanner in SCANNERS:
        ok = run_scanner(scanner)
        if ok:
            success += 1
        else:
            fail += 1
        if scanner != SCANNERS[-1]:
            print("  (pause 3 seconds between scanners...)")
            time.sleep(3)

    print()
    print("=" * 65)
    print(f"  RUN COMPLETE: {success} succeeded, {fail} failed")
    print(f"  Drive metadata:  project-743aab84-f9a5-4ec7-954.national_audits.drive_file_index")
    print(f"  Google Photos:   project-743aab84-f9a5-4ec7-954.national_audits.google_photos_index")
    print(f"  Drive content:   project-743aab84-f9a5-4ec7-954.drive_forensics.drive_documents")
    print("=" * 65)


if __name__ == "__main__":
    main()
