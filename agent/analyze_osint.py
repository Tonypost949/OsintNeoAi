# analyze_osint.py
"""Analyze OSINT data using the Gemini Interactions API.
This script reads the OSINT evidence file and asks Gemini to identify key patterns and themes.
"""
import os

# Ensure the google-genai library is installed (>=2.3.0)
# You can install it with: pip install -U google-genai

from google import genai

# Path to the OSINT evidence file in the workspace
EVIDENCE_PATH = os.path.join(os.path.dirname(__file__), "..", "osint-agent", "evidence.txt")

def load_evidence(path: str) -> str:
    """Load the OSINT evidence text from the given file path."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def analyze_text(text: str) -> str:
    """Send the text to Gemini and request a pattern analysis."""
    prompt = (
        "You are an OSINT analyst. Identify the key patterns, themes, and notable observations "
        "in the following OSINT collection. Summarize them concisely and list any recurring "
        "entities or topics.\n\n" + text
    )
    interaction = genai.Client().interactions.create(
        model="gemini-3.5-flash",
        input=prompt,
        # Optional: store=False if you don't want the interaction cached
    )
    return interaction.output_text or "(no response)"

if __name__ == "__main__":
    if not os.path.exists(EVIDENCE_PATH):
        print(f"Evidence file not found at {EVIDENCE_PATH}")
        exit(1)
    evidence = load_evidence(EVIDENCE_PATH)
    result = analyze_text(evidence)
    print("--- Gemini Pattern Analysis ---")
    print(result)
