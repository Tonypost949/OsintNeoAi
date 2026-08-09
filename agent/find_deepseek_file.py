"""
Finds the exact filename of the OSINTNeo JSON file by searching for keywords.
Logs the matches to find_deepseek_file_log.txt.
"""
import os
import shutil

def main():
    dl_dir = r"C:\Users\HP\Downloads"
    files = os.listdir(dl_dir)
    log = []
    
    for f in files:
        if "OSINTNeo" in f:
            log.append(f"Found match: {repr(f)}")
            # Hex representation of name
            hex_name = f.encode('utf-8', errors='replace').hex()
            log.append(f"  Hex: {hex_name}")
            
            # Safe rename immediately
            src = os.path.join(dl_dir, f)
            dst = os.path.join(dl_dir, "OSINTNeoAiXXL_chat.json")
            try:
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copyfile(src, dst)
                log.append(f"  Successfully copied to safe filename: {dst}")
            except Exception as e:
                log.append(f"  Failed to copy: {e}")
                
    with open("find_deepseek_file_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(log))

if __name__ == "__main__":
    main()
