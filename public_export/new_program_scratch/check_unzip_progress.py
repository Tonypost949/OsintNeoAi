import os

OUTPUT_DIR = r"C:\Users\HP\OneDrive\Documents\new_program_scratch\unzipped_data"

def get_progress():
    if not os.path.exists(OUTPUT_DIR):
        print("[-] unzipped_data directory does not exist yet.")
        return
        
    count = 0
    folders = []
    for root, dirs, files in os.walk(OUTPUT_DIR):
        for file in files:
            count += 1
        for d in dirs:
            folders.append(d)
            
    print(f"[*] Current extracted file count: {count}")
    print(f"[*] Folders created: {set(folders)}")

if __name__ == "__main__":
    get_progress()
