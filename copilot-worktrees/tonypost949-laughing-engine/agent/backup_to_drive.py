import os
import shutil
from google.cloud import storage

# Paths
BRAIN_DIR = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
WORKSPACE_DIR = r"C:\Users\HP\.gemini\antigravity-ide\scratch\osint-agent"
TRANSCRIPT_SOURCE = os.path.join(BRAIN_DIR, ".system_generated", "logs", "transcript.jsonl")
TRANSCRIPT_BACKUP = os.path.join(WORKSPACE_DIR, "Makaveli_Conversation_Log.jsonl")
CORE_CONTEXT = os.path.join(WORKSPACE_DIR, "antigravity_core_context.md")
BUCKET_NAME = "osint-ai-evidence-vault-m4"

def backup_system():
    print("="*60)
    print("  MAKAVELI / ZEUS SYSTEM BACKUP PROTOCOL  ")
    print("="*60)

    # 1. Backup Transcript Locally
    if os.path.exists(TRANSCRIPT_SOURCE):
        shutil.copy2(TRANSCRIPT_SOURCE, TRANSCRIPT_BACKUP)
        print(f"[+] Local conversation log backed up to {TRANSCRIPT_BACKUP}")
    else:
        print("[!] Transcript source not found.")

    # 2. Upload to Google Cloud Storage (Acting as Cloud Drive)
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)
        
        if os.path.exists(TRANSCRIPT_BACKUP):
            blob = bucket.blob("system_backups/Makaveli_Conversation_Log.jsonl")
            blob.upload_from_filename(TRANSCRIPT_BACKUP)
            print("[+] Uploaded Conversation Log to Cloud Vault.")
            
        if os.path.exists(CORE_CONTEXT):
            blob = bucket.blob("system_backups/Antigravity_Resurrection_Protocol.md")
            blob.upload_from_filename(CORE_CONTEXT)
            print("[+] Uploaded Core Context to Cloud Vault.")
            
        print("[+] Backup successfully secured in Cloud.")

    except Exception as e:
        print(f"[!] Error uploading to Cloud: {e}")

if __name__ == "__main__":
    backup_system()
