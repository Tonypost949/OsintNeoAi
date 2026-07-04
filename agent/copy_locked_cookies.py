"""
Locked file copier using win32file with FILE_SHARE_READ flags.
Bypasses Windows file locking for active Chrome profiles.
"""
import os
import shutil
import win32file
import win32con

def copy_locked_file(src, dst):
    try:
        # Open source file with sharing flags
        handle = win32file.CreateFile(
            src,
            win32con.GENERIC_READ,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        # Open destination file
        out_handle = win32file.CreateFile(
            dst,
            win32con.GENERIC_WRITE,
            0,
            None,
            win32con.CREATE_ALWAYS,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )
        
        # Read and write chunks
        chunk_size = 4096
        while True:
            err, data = win32file.ReadFile(handle, chunk_size)
            if not data:
                break
            win32file.WriteFile(out_handle, data)
            
        win32file.CloseHandle(handle)
        win32file.CloseHandle(out_handle)
        print(f"Successfully copied locked file: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"Failed to copy locked file {src}: {e}")
        return False

def main():
    user_data = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data')
    locked_profiles = ['Profile 8', 'Profile 10', 'Profile 11']
    
    for p in locked_profiles:
        src = os.path.join(user_data, p, 'Network', 'Cookies')
        dst = f"temp_cookies_{p}.db"
        if os.path.exists(src):
            copy_locked_file(src, dst)

if __name__ == "__main__":
    main()
