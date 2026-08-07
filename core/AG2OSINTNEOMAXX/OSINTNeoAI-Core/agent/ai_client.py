import os

class AIClient:
    """Consolidated gateway client linking core routines to the Gemini API."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.api_key:
            print("[AI] GEMINI_API_KEY is not set. Running in offline/deterministic matching mode.")
            return
            
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
            print("[AI] Gemini Generative Client initialized successfully.")
        except Exception as e:
            print(f"[AI] Error importing or initializing google-genai: {e}")

    def generate_text(self, prompt, model="gemini-2.5-flash"):
        """Generate plain-text or structured summaries from prompts."""
        if not self.client:
            print("[AI] Client is offline; returning fallback empty response.")
            return "AI Client Offline (No API Key)"
            
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"[AI] Generation failed: {e}")
            return f"Error: {e}"

    def extract_entity_relationships(self, raw_unstructured_text):
        """Uses semantic reasoning to extract graph relationships directly from raw text block."""
        prompt = (
            f"Analyze the following intelligence data and extract all entities and their connections.\n"
            f"Format the output strictly as a JSON list of objects containing source, relationship, and target.\n"
            f"Allowed relationship types: OWNS, RECEIVED_PPP, REGISTERED_AT, LOCATED_IN, OFFICER_OF, DIRECTOR_OF, LITIGANT_IN, REPRESENTED_BY, CONNECTED_TO.\n\n"
            f"Data:\n{raw_unstructured_text}"
        )
        return self.generate_text(prompt)
