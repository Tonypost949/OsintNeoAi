from pynput import keyboard

print("=========================================================")
print("  🔍 KEY DETECTOR — PRESS ANY KEY TO SEE ITS NAME & CODE  ")
print("=========================================================")

def on_press(key):
    try:
        print(f"-> Key pressed: {key} | vk: {getattr(key, 'vk', None)}")
    except Exception as e:
        print(f"-> Error: {e}")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
