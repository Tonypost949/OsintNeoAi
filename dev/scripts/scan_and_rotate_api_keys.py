"""Real key rotator for OsintNeoAi. Uses C:/OsintNeoAi/.env + vault."""
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

REAL_ENV = Path("C:/OsintNeoAi/.env")
VAULT = Path("C:/Amd949609_Antigravity_v1/Amd949609_keys/api_vault.json")
BACKUP_DIR = Path("C:/OsintNeoAi/.env_backups")
BACKUP_DIR.mkdir(exist_ok=True)

def mask(k: str) -> str:
    if not k or len(k) < 10:
        return "(empty/invalid)"
    return f"{k[:6]}...{k[-4:]} len={len(k)}"

def load_vault_keys():
    try:
        data = json.loads(VAULT.read_text(encoding="utf-8"))
        keys = data.get("google_pro_keys", [])
        # keep only plausible AIza keys len 35-45
        valid = [k.strip() for k in keys if isinstance(k, str) and k.strip().startswith("AIza") and 35 <= len(k.strip()) <= 45]
        return keys, valid
    except Exception as e:
        print(f"[X] Vault read failed {VAULT}: {e}")
        return [], []

def parse_env():
    lines = REAL_ENV.read_text(encoding="utf-8").splitlines() if REAL_ENV.exists() else []
    vals = {}
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        vals[k.strip()] = v.strip()
    return lines, vals

def check_keys():
    print(f"[+] ENV: {REAL_ENV} exists={REAL_ENV.exists()}")
    print(f"[+] VAULT: {VAULT} exists={VAULT.exists()}")
    _, vals = parse_env()
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_MAPS_API_KEY", "GITHUB_PAT"):
        v = vals.get(name, "") or os.environ.get(name, "")
        print(f"    {name} = {mask(v)}")
    _, valid = load_vault_keys()
    print(f"[+] Vault total entries incl invalid: check file directly; valid AIza-format: {len(valid)}")
    cur = vals.get("GOOGLE_API_KEY", "")
    if cur in valid:
        print(f"[+] Current GOOGLE_API_KEY is vault index {valid.index(cur)}")
    else:
        print("[!] Current GOOGLE_API_KEY/GEMINI key NOT in vault valid list (custom key in use)")
    mem = os.environ.get("GEMINI_API_KEY", "")
    print(f"[+] Process memory GEMINI_API_KEY = {mask(mem)}")

def rotate(index: int | None = None):
    lines, vals = parse_env()
    _, valid = load_vault_keys()
    if not valid:
        print("[X] No valid vault keys, abort")
        return 1
    cur = vals.get("GOOGLE_API_KEY", "")
    if index is None:
        try:
            cur_i = valid.index(cur)
            index = (cur_i + 1) % len(valid)
        except ValueError:
            index = 0
    index = index % len(valid)
    new_key = valid[index]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = BACKUP_DIR / f".env.bak_{ts}_idx{index}"
    shutil.copy2(REAL_ENV, bak)
    print(f"[+] Backup: {bak}")
    out = []
    seen = set()
    for line in lines:
        s = line.strip()
        if s.startswith("#") or "=" not in s:
            out.append(line)
            continue
        k, _ = s.split("=", 1)
        k = k.strip()
        if k in ("GOOGLE_API_KEY", "GOOGLE_MAPS_API_KEY"):
            if k not in seen:
                out.append(f"{k}={new_key}")
                seen.add(k)
            else:
                out.append(f"{k}={new_key}")
        else:
            out.append(line)
    REAL_ENV.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"[OK] Rotated to vault index {index}: {mask(new_key)}")
    print(f"[OK] Updated GOOGLE_API_KEY + GOOGLE_MAPS_API_KEY in {REAL_ENV}")
    print("[i] GEMINI_API_KEY left untouched (separate Gemini key). Use --also-gemini to sync it.")
    return 0

def live_test(key: str) -> int:
    """Return HTTP status from a real Gemini API call (200 = usable)."""
    import urllib.request, urllib.error
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key=" + key
    body = json.dumps({"contents": [{"parts": [{"text": "ping"}]}], "generationConfig": {"maxOutputTokens": 1}}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0

def write_key(new_key: str, names=("GEMINI_API_KEY", "GOOGLE_API_KEY")):
    lines, _ = parse_env()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(REAL_ENV, BACKUP_DIR / f".env.bak_{ts}_auto")
    out, done = [], set()
    for line in lines:
        s = line.strip()
        k = s.split("=", 1)[0].strip() if "=" in s and not s.startswith("#") else None
        if k in names:
            out.append(f"{k}={new_key}"); done.add(k)
        else:
            out.append(line)
    out += [f"{n}={new_key}" for n in names if n not in done]
    REAL_ENV.write_text("\n".join(out) + "\n", encoding="utf-8")
    if os.name == "nt":
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE) as h:
            for n in names:
                winreg.SetValueEx(h, n, 0, winreg.REG_SZ, new_key)
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x1A, 0, "Environment", 2, 5000, None)

def auto():
    """Keep a WORKING key active: test current, rotate through vault on 429/400/403."""
    _, vals = parse_env()
    cur = vals.get("GEMINI_API_KEY", "")
    st = live_test(cur) if cur else 0
    print(f"[+] Current GEMINI_API_KEY {mask(cur)} -> HTTP {st}")
    if st == 200:
        print("[OK] Current key works, no change."); return 0
    _, valid = load_vault_keys()
    start = valid.index(cur) + 1 if cur in valid else 0
    for i in range(len(valid)):
        idx = (start + i) % len(valid)
        k = valid[idx]
        if k == cur:
            continue
        s = live_test(k)
        print(f"    vault[{idx}] {mask(k)} -> HTTP {s}")
        if s == 200:
            write_key(k)
            print(f"[OK] Switched GEMINI_API_KEY + GOOGLE_API_KEY to vault[{idx}] (.env + Windows User env)")
            return 0
    print("[X] No working key in vault (all exhausted/invalid)."); return 2

if __name__ == "__main__":
    if "--auto" in sys.argv:
        sys.exit(auto())
    if "--rotate" in sys.argv:
        idx = None
        for a in sys.argv[1:]:
            if a.startswith("--index="):
                try:
                    idx = int(a.split("=", 1)[1])
                except ValueError:
                    pass
        sys.exit(rotate(idx))
    else:
        check_keys()
        print('\n[i] Usage: python scan_and_rotate_api_keys.py --check | --rotate [--index=N]')
