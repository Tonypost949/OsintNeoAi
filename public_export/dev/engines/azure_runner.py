"""
azure_runner.py — Run all Azure AI services in sequence.
Usage: python azure_runner.py [--ocr] [--search] [--transcribe] [--all]
"""
import subprocess, sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_script(name):
    path = os.path.join(SCRIPT_DIR, name)
    if os.path.exists(path):
        print(f"\n=== Running {name} ===")
        subprocess.run([sys.executable, path], check=False)
    else:
        print(f"Script not found: {path}")

if __name__ == "__main__":
    if len(sys.argv) == 1 or "--all" in sys.argv:
        run_script("azure_search_index.py")
        run_script("azure_ocr_permits.py")
        run_script("azure_transcribe_audio.py")
    else:
        for arg in sys.argv[1:]:
            if "--ocr" in arg: run_script("azure_ocr_permits.py")
            if "--search" in arg: run_script("azure_search_index.py")
            if "--transcribe" in arg: run_script("azure_transcribe_audio.py")
    print("\n=== Azure runner complete ===")
