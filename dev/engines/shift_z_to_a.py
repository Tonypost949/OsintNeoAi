import pynput.keyboard as keyboard
from pynput.keyboard import Key, KeyCode

controller = keyboard.Controller()

current_keys = set()

def on_press(key):
    try:
        current_keys.add(key)
        # Check if Shift and z are pressed together
        if (Key.shift in current_keys or Key.shift_r in current_keys or Key.shift_l in current_keys) and (key == KeyCode.from_char('z') or key == KeyCode.from_char('Z')):
            # Backspace to remove z if typed
            controller.tap(Key.backspace)
            controller.type('a')
    except Exception as e:
        pass

def on_release(key):
    try:
        current_keys.remove(key)
    except KeyError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
