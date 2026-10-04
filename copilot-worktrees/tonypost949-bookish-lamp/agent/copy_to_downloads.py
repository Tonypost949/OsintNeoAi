"""
Saves the formatted Markdown chat sessions directly back into the user's Downloads folder.
"""
import os
import shutil

def main():
    dl_dir = r"C:\Users\HP\Downloads"
    
    # Files to copy
    files_to_copy = [
        ("deepseek_session_dehashed_hbpd.md", "Dehashed-HBPD-scan.md"),
        ("gemini_session_osint_neoai_xxl.md", "OSINTNeoAiXXL-Terminal-Assistance.md")
    ]
    
    for src, dst_name in files_to_copy:
        dst = os.path.join(dl_dir, dst_name)
        try:
            if os.path.exists(dst):
                os.remove(dst)
            shutil.copyfile(src, dst)
            print(f"Copied {src} -> {dst}")
        except Exception as e:
            print(f"Failed to copy {src}: {e}")

if __name__ == "__main__":
    main()
