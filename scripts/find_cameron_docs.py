import os
import sys

TARGET_DIRS = [
    r"C:\OsintNeoAi\evidence",
    r"C:\OsintNeoAi\cases",
    r"C:\OsintNeoAi\reports",
    r"C:\OsintNeoAi\docs",
    r"C:\OsintNeoAi\archive",
    r"C:\OsintNeoAi\data",
    r"C:\OsintNeoAi\forensic",
    r"C:\OsintNeoAi\extracted_documents",
    r"C:\OsintNeoAi\noble_beanbag_evidence",
    r"C:\Amd949609_Antigravity_v1"
]

KEYWORDS = ["17631", "cameron", "cpra", "legistar", "laserfiche", "permit"]

print("=" * 60)
print(" SEARCHING LOCAL VERIFIED 17631 CAMERON RECORD SET ")
print("=" * 60)

found = []
for base in TARGET_DIRS:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in {"node_modules", ".git", ".venv", "venv", "__pycache__"}]
        for f in files:
            low = f.lower()
            if any(k in low for k in KEYWORDS):
                full_p = os.path.join(root, f)
                found.append(full_p)
                print(f"[FOUND] {full_p}")

print("=" * 60)
print(f"Total matching files found: {len(found)}")
