import os
import urllib.request
import json
import time

def main():
    username = "Tonypost949"
    backup_dir = r"C:\Users\HP\OneDrive\Documents\github_backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"[*] Starting backup of repositories for user: {username}")
    print(f"[*] Target directory: {backup_dir}")
    
    # 1. Fetch repositories
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    req = urllib.request.Request(url, headers={"User-Agent": "Antigravity-Backup-Script"})
    
    try:
        with urllib.request.urlopen(req) as response:
            repos = json.loads(response.read().decode())
    except Exception as e:
        print(f"[-] Error fetching repository list: {e}")
        return
        
    print(f"[+] Found {len(repos)} repositories to process.")
    
    # 2. Download zipballs
    for idx, repo in enumerate(repos, 1):
        repo_name = repo["name"]
        default_branch = repo.get("default_branch", "main")
        print(f"\n[{idx}/{len(repos)}] Processing: {repo_name} (Default branch: {default_branch})")
        
        # Canonical zipball URL
        zipball_url = f"https://api.github.com/repos/{username}/{repo_name}/zipball"
        dest_path = os.path.join(backup_dir, f"{repo_name}.zip")
        
        # Skip if already exists (resume support)
        if os.path.exists(dest_path):
            print(f"[!] Already exists at {dest_path}. Skipping.")
            continue
            
        print(f"[*] Downloading zipball from {zipball_url}...")
        try:
            zip_req = urllib.request.Request(zipball_url, headers={"User-Agent": "Antigravity-Backup-Script"})
            with urllib.request.urlopen(zip_req) as zip_res:
                with open(dest_path, "wb") as f:
                    f.write(zip_res.read())
            print(f"[+] Successfully downloaded to {dest_path}")
        except Exception as e:
            print(f"[-] Failed to download {repo_name}: {e}")
            
        # Respect rate limits
        time.sleep(1)
        
    print("\n[+] Backup process finished!")

if __name__ == "__main__":
    main()
