"""
Live Real-Time A <-> Z Keyboard Swapper for Windows
Uses low-level Windows keyboard hook (WH_KEYBOARD_LL via ctypes)
Works immediately without requiring a system reboot or sign-out.
"""

import sys
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

VK_A = 0x41
VK_Z = 0x5A

KEYEVENTF_KEYUP = 0x0002
EXTRA_MAGIC = 0x55AA1234

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong if sys.maxsize > 2**32 else wintypes.DWORD),
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))

def send_key(vk, is_up):
    flags = KEYEVENTF_KEYUP if is_up else 0
    extra = ctypes.c_ulong(EXTRA_MAGIC)
    user32.keybd_event(vk, 0, flags, extra)

def low_level_keyboard_handler(nCode, wParam, lParam):
    if nCode >= 0 and lParam:
        kb = lParam.contents
        # Check if this is an injected key by us to avoid recursion
        if kb.dwExtraInfo == EXTRA_MAGIC:
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
        is_up = wParam in (WM_KEYUP, WM_SYSKEYUP)

        if is_down or is_up:
            if kb.vkCode == VK_A:
                send_key(VK_Z, is_up)
                return 1  # Block original 'A'
            elif kb.vkCode == VK_Z:
                send_key(VK_A, is_up)
                return 1  # Block original 'Z'

    return user32.CallNextHookEx(None, nCode, wParam, lParam)

callback = HOOKPROC(low_level_keyboard_handler)

def run_hook():
    hook = user32.SetWindowsHookExW(
        WH_KEYBOARD_LL,
        callback,
        0,
        0
    )
    if not hook:
        err = kernel32.GetLastError()
        print(f"Failed to install keyboard hook. Error code: {err}")
        sys.exit(1)

    print("🚀 Real-time A <-> Z key swapper active! Press Ctrl+C to stop.")
    
    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWindowsHookEx(hook)
        print("Keyboard hook removed.")

if __name__ == "__main__":
    run_hook()
