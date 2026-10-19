"""Test route resolution and content serving in simple_map_server.py."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from simple_map_server import MAP_ROUTES, ROOT_DIR

def test_routes():
    print("[+] Validating simple_map_server MAP_ROUTES...")
    missing = []
    for route, target_file in MAP_ROUTES.items():
        file_path = ROOT_DIR / target_file
        if not file_path.exists():
            missing.append((route, target_file))
        else:
            print(f"  ✓ {route:<30} -> {target_file}")

    if missing:
        print(f"[-] {len(missing)} routes point to missing files:")
        for r, f in missing:
            print(f"    ✗ {r} -> {f}")
        return False
    print(f"[✅] All {len(MAP_ROUTES)} routes verified successfully!")
    return True

if __name__ == "__main__":
    assert test_routes()
