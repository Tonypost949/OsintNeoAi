import time
import keyboard

print("=========================================================")
print("  🎤 RIGHT ALT DICTATION SHORTCUT LISTENER               ")
print("=========================================================")
print("👉 Press [RIGHT ALT] anywhere to trigger Windows Dictation!")
print("👉 Press [Ctrl + C] in this window to exit.")

def trigger_win_h():
    print("-> Right Alt pressed: Triggering Win+H Dictation...")
    keyboard.send("windows+h")

# Bind Right Alt (also known as alt gr / right alt) to send Windows + H
keyboard.add_hotkey("right alt", trigger_win_h)

if __name__ == '__main__':
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nExiting Right Alt dictation listener.")
