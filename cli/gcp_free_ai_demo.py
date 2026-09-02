"""
TASK-015 — GCP Free AI Quotas Harness
Free tier: Vision OCR 1k/mo, Speech 60m, NL 5k/mo, Gemini AI Studio
Project: noble-beanbag-497411-m4 (BigQuery)
Usage: python cli/gcp_free_ai_demo.py [--vision|--speech|--nl|--gemini]
"""
import os, json, sys
PROJECT = os.getenv("GCP_PROJECT", "noble-beanbag-497411-m4")

def demo_vision():
    try:
        from google.cloud import vision
        client = vision.ImageAnnotatorClient()
        print("[Vision] client ready — 1k free units/mo")
        return True
    except Exception as e:
        print(f"[Vision] pip install google-cloud-vision ; {e}")
        return False

def demo_speech():
    try:
        from google.cloud import speech
        client = speech.SpeechClient()
        print("[Speech] client ready — 60m free")
        return True
    except Exception as e:
        print(f"[Speech] pip install google-cloud-speech ; {e}")
        return False

def demo_nl():
    try:
        from google.cloud import language_v1
        client = language_v1.LanguageServiceClient()
        doc = {"content": "Huntington Beach Ascon Superfund parcel 114-481-32 deed $0", "type_": language_v1.Document.Type.PLAIN_TEXT}
        print("[NL] client ready — 5k free units")
        return True
    except Exception as e:
        print(f"[NL] pip install google-cloud-language ; {e}")
        return False

def demo_gemini():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        print(f"[Gemini] key present {key[:8]}... — AI Studio free tier")
        return True
    print("[Gemini] set GEMINI_API_KEY for https://aistudio.google.com")
    return False

if __name__ == "__main__":
    print(f"Project {PROJECT} — TASK-015 harness")
    for fn in [demo_vision, demo_speech, demo_nl, demo_gemini]:
        fn()
    print("See https://cloud.google.com/use-cases/free-ai-tools + data/tasks.json:340")
