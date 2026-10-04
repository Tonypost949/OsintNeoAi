import os
import shutil
import sys
import argparse

# Default Antigravity paths on Windows
APP_DATA_DIR = os.path.expanduser(r"~\.gemini\antigravity")
CONVERSATIONS_DIR = os.path.join(APP_DATA_DIR, "conversations")
BRAIN_DIR = os.path.join(APP_DATA_DIR, "brain")

def resurrect_chat(orphaned_id, dummy_id):
    print(f"[*] Starting Antigravity PB Injection / Resurrection...")
    print(f"[*] Orphaned ID (Data to restore): {orphaned_id}")
    print(f"[*] Dummy ID (Target UI slot): {dummy_id}")

    # 1. Paths
    orphan_db = os.path.join(CONVERSATIONS_DIR, f"{orphaned_id}.db")
    dummy_db = os.path.join(CONVERSATIONS_DIR, f"{dummy_id}.db")
    
    orphan_brain = os.path.join(BRAIN_DIR, orphaned_id)
    dummy_brain = os.path.join(BRAIN_DIR, dummy_id)

    # 2. Validation
    if not os.path.exists(orphan_db):
        print(f"[!] Error: Orphaned DB file not found: {orphan_db}")
        return False
        
    if not os.path.exists(dummy_db):
        print(f"[!] Error: Dummy DB file not found. Create a new chat in the UI first!")
        return False

    # 3. Inject DB (UI History)
    print(f"[*] Overwriting dummy UI history with orphaned data...")
    try:
        shutil.copy2(orphan_db, dummy_db)
        # Handle WAL and SHM files if they exist for sqlite
        for ext in ['-wal', '-shm']:
            if os.path.exists(orphan_db + ext):
                shutil.copy2(orphan_db + ext, dummy_db + ext)
    except Exception as e:
        print(f"[!] Error copying DB: {e}")
        return False

    # 4. Inject Brain (Agent Memory / Context)
    if os.path.exists(orphan_brain):
        print(f"[*] Overwriting dummy brain with orphaned agent memory...")
        try:
            if os.path.exists(dummy_brain):
                shutil.rmtree(dummy_brain)
            shutil.copytree(orphan_brain, dummy_brain)
        except Exception as e:
            print(f"[!] Error copying brain directory: {e}")
            return False
    else:
        print("[!] Warning: Orphaned brain directory not found. Agent memory may be lost (only UI history restored).")

    print("[+] Resurrection complete! Please completely restart the Antigravity App/IDE to load the restored chat.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Chat Resurrection Script (PB Injection)")
    parser.add_argument("orphaned_id", help="The UUID of the lost/orphaned chat you want to recover")
    parser.add_argument("dummy_id", help="The UUID of a brand new, empty chat you just created in the UI")
    
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nHow to use:")
        print("1. Find your lost chat UUID in ~/.gemini/antigravity/conversations/")
        print("2. Open Antigravity and create a NEW chat (this is the dummy). Note its UUID from the URL or log.")
        print("3. Run: python antigravity_resurrection.py <orphaned_uuid> <dummy_uuid>")
        print("4. Restart Antigravity.")
        sys.exit(0)
        
    args = parser.parse_args()
    resurrect_chat(args.orphaned_id, args.dummy_id)
