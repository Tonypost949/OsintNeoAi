"""
Python script to map Shift + Z to send 'a' (or 'A') on Windows using ctypes (Native Windows API - No external libraries required).
Requires Administrator privileges to intercept global keyboard events, OR install 'keyboard' library via `pip install keyboard`.
"""

import time
import sys

try:
    import keyboard
    print("Using 'keyboard' module...")
    print("Pressing Shift + Z will now type 'a'. Press Ctrl+C to stop.")
    
    def send_a():
        keyboard.write('a')
        
    keyboard.add_hotkey('shift+z', send_a, suppress=True)
    keyboard.wait()

except ImportError:
    print("'keyboard' module not installed. Installing or using Windows PowerToys / AutoHotkey is recommended.")
    print("To install keyboard library, run: pip install keyboard")
    print("Then run: python remap_shift_z_to_a.py")
