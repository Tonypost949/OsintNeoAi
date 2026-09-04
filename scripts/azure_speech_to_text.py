import os
import subprocess
import json
import azure.cognitiveservices.speech as speechsdk

def get_speech_key():
    """Retrieve Azure Speech API key from environment variable or Azure CLI dynamically."""
    key = os.environ.get("AZURE_SPEECH_KEY")
    if not key:
        cmd = "az cognitiveservices account keys list --name osintneoai-speech --resource-group opencode-rg --output json"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            key = data.get("key1")
    return key

SPEECH_REGION = "eastus"

def transcribe_from_microphone():
    """Transcribes real-time audio input from your computer's microphone."""
    speech_key = get_speech_key()
    if not speech_key:
        print("❌ Error: Could not retrieve Azure Speech key.")
        return

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=SPEECH_REGION)
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print("\n🎤 Speak into your microphone... (Press Ctrl+C or stop speaking to end)")
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"\n✓ RECOGNIZED TEXT: {result.text}")
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("❌ No speech could be recognized.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"❌ Recognition Canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error Details: {cancellation_details.error_details}")

def transcribe_audio_file(audio_file_path):
    """Transcribes speech from a WAV audio file."""
    if not os.path.exists(audio_file_path):
        print(f"❌ Audio file not found: {audio_file_path}")
        return

    speech_key = get_speech_key()
    if not speech_key:
        print("❌ Error: Could not retrieve Azure Speech key.")
        return

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=SPEECH_REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    print(f"\n🔊 Transcribing audio file: {audio_file_path}...")
    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"\n✓ TRANSCRIPTION OUTPUT:\n{result.text}")
    else:
        print("❌ Transcription failed or no speech found.")

if __name__ == '__main__':
    print("=== AZURE SPEECH-TO-TEXT DEMO ===")
    print("1. Azure Speech Service: osintneoai-speech")
    print("2. Region: eastus")
    print(f"3. Key Status: {'Loaded' if get_speech_key() else 'Missing'}")
