import time
import keyboard
from scripts.azure_speech_to_text import transcribe_from_microphone

HOTKEY = "ctrl+shift+s"

def on_hotkey_pressed():
    print(f"\n[HOTKEY TRIGGERED: {HOTKEY}] Starting Azure Speech-to-Text...")
    transcribe_from_microphone()

if __name__ == '__main__':
    print("=========================================================")
    print("  🎙️ AZURE SPEECH-TO-TEXT GLOBAL KEYBOARD HOTKEY LISTEN  ")
    print("=========================================================")
    print(f"👉 Press [{HOTKEY.upper()}] anywhere to start voice dictation!")
    print("👉 Press [Ctrl + C] in this window to exit.")
    
    keyboard.add_hotkey(HOTKEY, on_hotkey_pressed)
    keyboard.wait()
