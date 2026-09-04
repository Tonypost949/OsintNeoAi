import os
import sys
import json
import subprocess
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk

# Service Metadata
SPEECH_ACCOUNT_NAME = "osintneoai-speech"
RESOURCE_GROUP = "opencode-rg"
REGION = "eastus"

def get_azure_speech_config():
    """Dynamically fetches Azure Speech credentials and returns a SpeechConfig object."""
    key = os.environ.get("AZURE_SPEECH_KEY")
    if not key:
        cmd = f"az cognitiveservices account keys list --name {SPEECH_ACCOUNT_NAME} --resource-group {RESOURCE_GROUP} --output json"
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            key = data.get("key1")
    
    if not key:
        raise ValueError("Could not retrieve Azure Speech key via Azure CLI or Environment Variables.")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=REGION)
    speech_config.speech_recognition_language = "en-US"
    return speech_config

def recognize_speech_from_mic():
    """Transcribes real-time speech from the computer microphone using Azure Speech STT."""
    print("=========================================================")
    print("  🎙️ AZURE SPEECH-TO-TEXT — MICROPHONE TRANSCRIPTION     ")
    print("=========================================================")
    print(f"Service: {SPEECH_ACCOUNT_NAME} | Region: {REGION}")
    print("🎤 Speak into your microphone now...")

    speech_config = get_azure_speech_config()
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("\n✓ SUCCESSFUL TRANSCRIPTION:")
        print(f"👉 \"{result.text}\"")
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("\n❌ No speech could be recognized.")
        return None
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"\n❌ Recognition Canceled: {cancellation.reason}")
        if cancellation.reason == speechsdk.CancellationReason.Error:
            print(f"Error Details: {cancellation.error_details}")
        return None

def transcribe_audio_file(file_path):
    """Transcribes a WAV audio file using Azure Speech STT."""
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None

    print(f"🔊 Transcribing Audio File: {file_path.name}...")
    speech_config = get_azure_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=str(file_path))
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("\n✓ TRANSCRIPTION COMPLETED:")
        print(result.text)
        return result.text
    else:
        print("❌ Failed to transcribe audio file.")
        return None

if __name__ == '__main__':
    # Test credentials check on script execution
    try:
        config = get_azure_speech_config()
        print("✓ Azure Speech STT Module Initialized Successfully!")
        print(f"✓ Target Service: {SPEECH_ACCOUNT_NAME} ({REGION})")
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
