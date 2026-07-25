import os
import shutil
import stat

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

archive_dir = r"c:\Users\HP\OneDrive\Documents\OsintNeoAi\archive"
for root, dirs, files in os.walk(archive_dir):
    if '.git' in dirs:
        git_path = os.path.join(root, '.git')
        print(f"Removing nested git repo: {git_path}")
        shutil.rmtree(git_path, onerror=remove_readonly)

print("Done cleaning nested .git folders.")
