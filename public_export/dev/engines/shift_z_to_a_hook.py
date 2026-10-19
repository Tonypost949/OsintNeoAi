import keyboard

# add_hotkey uses string shortcut syntax
def send_a():
    keyboard.send('backspace')
    keyboard.write('a')

keyboard.add_hotkey('shift+z', send_a)
print("HotKey listener active! Press Shift+Z...")
keyboard.wait()
