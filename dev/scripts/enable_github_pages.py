import subprocess
import json

repo = "Tonypost949/OsintNeoAi"
print(f"=== ENABLING GITHUB PAGES FOR {repo} ===")

# Check current Pages status
cmd_status = f"gh api repos/{repo}/pages 2>&1"
res_status = subprocess.run(cmd_status, shell=True, capture_output=True, text=True)

if res_status.returncode == 0:
    pdata = json.loads(res_status.stdout)
    print("✓ GitHub Pages is ALREADY ENABLED!")
    print(f"  - Status: {pdata.get('status')}")
    print(f"  - HTML URL: {pdata.get('html_url')}")
    print(f"  - Source Branch: {pdata.get('source', {}).get('branch')} (path: {pdata.get('source', {}).get('path')})")
else:
    print("GitHub Pages is currently disabled. Sending enable request...")
    # Enable Pages on main branch / docs folder or root
    cmd_enable = f'gh api --method POST -H "Accept: application/vnd.github+json" repos/{repo}/pages -f "source[branch]=main" -f "source[path]=/docs" 2>&1'
    res_enable = subprocess.run(cmd_enable, shell=True, capture_output=True, text=True)
    if res_enable.returncode == 0:
        pdata = json.loads(res_enable.stdout)
        print("✓ SUCCESS! GitHub Pages has been ENABLED!")
        print(f"  - HTML URL: {pdata.get('html_url')}")
    else:
        # Fallback to root /
        print("Trying fallback to root / path...")
        cmd_fallback = f'gh api --method POST -H "Accept: application/vnd.github+json" repos/{repo}/pages -f "source[branch]=main" -f "source[path]=/" 2>&1'
        res_fb = subprocess.run(cmd_fallback, shell=True, capture_output=True, text=True)
        print("Fallback Output:", res_fb.stdout or res_fb.stderr)
