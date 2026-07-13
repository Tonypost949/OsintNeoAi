import subprocess
import datetime
import os

def run_cmd(cmd, cwd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        print(f"Command: {cmd}\nStdout: {res.stdout.strip()}\nStderr: {res.stderr.strip()}\nCode: {res.returncode}\n")
        return res.returncode == 0
    except Exception as e:
        print(f"Error running {cmd}: {e}")
        return False

def main():
    cwd = r"C:\Users\HP\OneDrive\Documents"
    print(f"--- Git Auto-Push Started at {datetime.datetime.now()} ---")
    run_cmd("git add -A", cwd)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_cmd(f'git commit -m "Auto-commit from Antigravity - {timestamp}"', cwd)
    run_cmd("git push origin main", cwd)
    print("--- Git Auto-Push Finished ---")

if __name__ == "__main__":
    main()
