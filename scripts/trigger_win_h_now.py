import time
import ctypes

# Windows API Virtual Key Code constants
VK_LWIN = 0x5B
VK_H = 0x48
KEYEVENTF_KEYUP = 0x0002

def trigger_dictation_win_api():
    print("=== TRIGGERING WINDOWS DICTATION VIA WINDOWS API ===")
    # Press Win
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, 0, 0)
    # Press H
    ctypes.windll.user32.keybd_event(VK_H, 0, 0, 0)
    time.sleep(0.05)
    # Release H
    ctypes.windll.user32.keybd_event(VK_H, 0, KEYEVENTF_KEYUP, 0)
    # Release Win
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)
    print("✓ Win+H key sequence sent!")

if __name__ == '__main__':
    trigger_dictation_win_api()
