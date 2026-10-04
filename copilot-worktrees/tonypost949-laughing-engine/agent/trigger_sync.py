import requests
import sys

URL = "http://127.0.0.1:5000/api/sync"

def main():
    print(f"Triggering OSINT dashboard sync at {URL}...")
    try:
        response = requests.post(URL, json={"triggered_by": "OpenCode"})
        if response.status_code == 200:
            data = response.json()
            print("[✓] Sync Triggered Successfully!")
            print("\n--- Index Output ---")
            print(data.get("index_output", ""))
            print("\n--- Document Sync Output ---")
            print(data.get("sync_output", ""))
        else:
            print(f"[!] Server returned status code {response.status_code}:")
            print(response.text)
    except Exception as e:
        print(f"[!] Failed to connect to server: {e}")
        print("Please ensure the Flask dashboard is running ('python app.py').")

if __name__ == "__main__":
    main()
