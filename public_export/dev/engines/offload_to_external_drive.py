import os
import shutil
import datetime

EXTERNAL_DIR = r"G:\osint_external_backup"
os.makedirs(EXTERNAL_DIR, exist_ok=True)

files_to_offload = [
    r"C:\Users\HP\OsintNeoAi_Git_Backup.zip",
    r"C:\Users\HP\osintneoai\deepseek_data-2026-08-06.zip",
    r"C:\Users\HP\osintneoai\agent\OSINT_Agent_Complete_Backup_20260701_005918.zip",
    r"C:\Users\HP\osintneoai\agent\OSINT_Agent_Complete_Backup_20260702_110000.zip",
    r"C:\Users\HP\osintneoai\agent\osint_agent_backup_20260629_144213.zip",
    r"C:\Users\HP\osintneoai\agent\HBNC_Criminal_Referral_Evidence_Pack_20260619_211612.zip",
    r"C:\Users\HP\osintneoai\agent\HBNC_Criminal_Referral_Evidence_Pack_20260617_161638.zip",
    r"C:\Users\HP\osintneoai\agent\adobe_bulk_download_pro.zip",
    r"C:\Users\HP\osintneoai\agent\onedrive_documents_full.csv",
    r"C:\Users\HP\osintneoai\agent\bq_board_ppp_final.csv",
    r"C:\Users\HP\osintneoai\extracted_tasklets\deepseek_data-2026-08-06\conversations.json"
]

manifest_lines = [
    "# 📦 EXTERNAL DRIVE OFFLOADED FILES MANIFEST",
    f"**Backup Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    f"**Target External Directory:** `{EXTERNAL_DIR}`",
    "",
    "| File Name | Size (Bytes) | Original Path | Offloaded Path |",
    "|---|---|---|---|"
]

total_moved_bytes = 0
moved_count = 0

for src_path in files_to_offload:
    if os.path.exists(src_path):
        size = os.path.getsize(src_path)
        fname = os.path.basename(src_path)
        dst_path = os.path.join(EXTERNAL_DIR, fname)
        
        print(f"Moving: {src_path} ({size:,} bytes) -> {dst_path}")
        try:
            shutil.copy2(src_path, dst_path)
            os.remove(src_path)
            total_moved_bytes += size
            moved_count += 1
            manifest_lines.append(f"| `{fname}` | {size:,} | `{src_path}` | `{dst_path}` |")
        except Exception as e:
            print(f"Error moving {src_path}: {e}")

manifest_path = os.path.join(EXTERNAL_DIR, "OFFLOADED_FILES_MANIFEST.md")
with open(manifest_path, "w", encoding="utf-8") as f:
    f.write("\n".join(manifest_lines))

print(f"\nCompleted offloading {moved_count} files.")
print(f"Total space freed on C drive: {total_moved_bytes / (1024*1024):.2f} MB ({total_moved_bytes / (1024*1024*1024):.2f} GB)")
