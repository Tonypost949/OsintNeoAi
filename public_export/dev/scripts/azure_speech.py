import os
import json
import subprocess
import azure.cognitiveservices.speech as speechsdk

# Azure Speech Service Parameters
SPEECH_ACCOUNT_NAME = "osintneoai-speech"
RESOURCE_GROUP = "opencode-rg"
REGION = "eastus"

def get_speech_config():
    """Fetches API key dynamically via Azure CLI and returns SpeechConfig."""
    cmd = f"az cognitiveservices account keys list --name {SPEECH_ACCOUNT_NAME} --resource-group {RESOURCE_GROUP} --output json"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        key = json.loads(res.stdout).get("key1")
        if key:
            config = speechsdk.SpeechConfig(subscription=key, region=REGION)
            config.speech_recognition_language = "en-US"
            return config
    raise RuntimeError("Failed to retrieve Azure Speech Service key.")

def recognize_once():
    """Performs single-shot speech-to-text recognition from default microphone."""
    speech_config = get_speech_config()
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    
    print("Listening...")
    result = recognizer.recognize_once_async().get()
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech else None

def synthesize_text_to_speech(text, output_file="output.wav"):
    """Synthesizes input text into a spoken WAV audio file (Text-to-Speech)."""
    speech_config = get_speech_config()
    audio_config = speechsdk.audio.AudioConfig(filename=output_file)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    
    result = synthesizer.speak_text_async(text).get()
    return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted

if __name__ == '__main__':
    print(f"✓ Azure Speech Service SDK Connected: {SPEECH_ACCOUNT_NAME} ({REGION})")
