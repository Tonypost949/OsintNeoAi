import os
from pathlib import Path

# Paths to check for API keys
PATHS_TO_CHECK = [
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/.env"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/hub_server.py"),
    Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/scripts/autonomous_enrichment_worker.py"),
    Path(os.path.expanduser("~/.bashrc")),
    Path(os.path.expanduser("~/.bash_profile")),
    Path(os.path.expanduser("~/.zshrc"))
]

def check_keys():
    print("[+] Scanning environment and key files for Gemini API keys...")
    
    # 1. Check current process environment
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        print(f"[!] Found GEMINI_API_KEY in active memory/environment: {env_key[:6]}...{env_key[-4:]}")
    else:
        print("[ ] No GEMINI_API_KEY found in active memory.")

    # 2. Check files
    for p in PATHS_TO_CHECK:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    found = False
                    for i, line in enumerate(lines):
                        if "GEMINI_API_KEY" in line:
                            print(f"[!] Found reference in {p.name} (Line {i+1}): {line.strip()}")
                            found = True
                    if not found:
                        print(f"[ ] Clean: {p.name}")
            except Exception as e:
                print(f"[?] Could not read {p.name}: {e}")
        else:
            print(f"[ ] File does not exist: {p.name}")

if __name__ == "__main__":
    check_keys()
