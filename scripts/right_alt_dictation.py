import time
import ctypes
from pynput import keyboard
from pynput.keyboard import Key

VK_LWIN = 0x5B
VK_H = 0x48
KEYEVENTF_KEYUP = 0x0002

def send_win_h():
    print("-> Triggering Windows Dictation (Win+H)...")
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_H, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(VK_H, 0, KEYEVENTF_KEYUP, 0)
    ctypes.windll.user32.keybd_event(VK_LWIN, 0, KEYEVENTF_KEYUP, 0)

def on_press(key):
    # Check for Right Alt (vk: 165), AltGr, or Key.alt_r / Key.alt_gr
    vk = getattr(key, 'vk', None)
    if key in (Key.alt_r, Key.alt_gr) or vk in (165, 163, 162):
        send_win_h()

if __name__ == '__main__':
    print("=========================================================")
    print("  🎤 NATIVE WINDOWS API RIGHT ALT DICTATION LISTENER      ")
    print("=========================================================")
    print("👉 Tap [RIGHT ALT] to open Dictation!")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
