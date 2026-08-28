import os
import sys
import subprocess
import winreg

print("=== 1. CHECKING RUNNING PROCESSES ===")
try:
    tasks = subprocess.check_output("tasklist", shell=True, text=True)
    for target in ["autohotkey", "powertoys", "sharpkeys", "kanata", "kmonad"]:
        for line in tasks.splitlines():
            if target in line.lower():
                print(f"Found running key mapper: {line}")
except Exception as e:
    print(f"Error checking tasks: {e}")

print("\n=== 2. CHECKING REGISTRY SCANCODE MAP ===")
try:
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Keyboard Layout") as key:
        val, _ = winreg.QueryValueEx(key, "Scancode Map")
        print(f"HKLM Scancode Map found (bytes): {val.hex()}")
except Exception as e:
    print(f"HKLM Scancode Map: {e}")

try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Keyboard Layout") as key:
        val, _ = winreg.QueryValueEx(key, "Scancode Map")
        print(f"HKCU Scancode Map found (bytes): {val.hex()}")
except Exception as e:
    print(f"HKCU Scancode Map: {e}")

print("\n=== 3. CHECKING POWERTOYS KEYBOARD MANAGER ===")
pt_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\PowerToys\Keyboard Manager")
if os.path.exists(pt_path):
    print(f"PowerToys Keyboard Manager dir found: {pt_path}")
    for root, _, files in os.walk(pt_path):
        for f in files:
            fp = os.path.join(root, f)
            print(f"Config file: {fp}")
            try:
                with open(fp, "r", encoding="utf-8") as cfg:
                    print(cfg.read()[:500])
            except Exception as ex:
                print(f"Could not read: {ex}")
else:
    print("PowerToys Keyboard Manager directory not found.")
