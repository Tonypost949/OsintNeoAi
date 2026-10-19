import os
from pathlib import Path

ENV_FILE = Path("C:/Users/Amd949609/StudioProjects/OsintNeoAi/.env")

def update_env():
    print("[+] Ensuring .env is set up for cross-repo access...")
    if not ENV_FILE.exists():
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write("GEMINI_API_KEY=\n")
        print(f"[✓] Created empty .env file at {ENV_FILE.name}")
    else:
        print(f"[-] .env file already exists at {ENV_FILE.name}")

if __name__ == "__main__":
    update_env()
    print("\n[!] IMPORTANT: Paste your new API key directly into the .env file located at:")
    print(f"    {ENV_FILE.absolute()}")
