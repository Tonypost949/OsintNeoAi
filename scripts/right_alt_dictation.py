import time
import subprocess
from pynput import keyboard
from pynput.keyboard import Key, Controller

kb_controller = Controller()

print("=========================================================")
print("  🎤 RIGHT ALT DICTATION LISTENER (pynput VK-165)        ")
print("=========================================================")
print("👉 Tap [RIGHT ALT] on your keyboard to start dictation!")

def on_press(key):
    # Detect Right Alt key (Key.alt_r or Key.alt_gr)
    if key == Key.alt_r or key == Key.alt_gr:
        print("-> [RIGHT ALT PRESSED] -> Triggering Windows Dictation (Win+H)...")
        # Trigger Win+H via pynput
        kb_controller.press(Key.cmd)
        kb_controller.press('h')
        kb_controller.release('h')
        kb_controller.release(Key.cmd)

if __name__ == '__main__':
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
