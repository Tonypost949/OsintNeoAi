import hashlib
import json
import os
from google import genai
from google.genai import types

# 1. Define the Cryptographic Vault Tool
def generate_sha256_hash(raw_text: str) -> str:
    """Generates an immutable SHA-256 hash for raw OSINT testimony or target data to secure the chain of custody."""
    encoded_text = raw_text.encode('utf-8')
    secure_hash = hashlib.sha256(encoded_text).hexdigest()
    return f"HASH_LOCKED: {secure_hash}"

# 2. Define the BigQuery Payload Formatter Tool
def format_bigquery_payload(entity_name: str, hash_id: str, tags: list[str]) -> str:
    """Formats the hashed evidence and target entity into a JSON payload for the BigQuery append-only ledger."""
    payload = {
        "entity": entity_name,
        "cryptographic_hash": hash_id,
        "status": "Unverified Shadow Clone",
        "tags": tags,
        "ledger_destination": "noble-beanbag-497411-m4",
        "timestamp": "auto-generated"
    }
    
    output_path = r"C:\OsintNeoAi\data\staged_payload.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=2)
        
    return f"Payload successfully formatted and staged at {output_path}"

# 3. Instantiate the Genesis Ingestion Agent
def initialize_agent():
    print("Initializing Genesis Agent (Native Gemini API Bypass)...")
    
    # Initialize the native Google GenAI client
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    return client

def main():
    client = initialize_agent()
    print("Agent locked and standing by for input...\n")
    
    test_input = "Investigate Woodbridge Apartments and extract all associated entities, permits, and violations."
    print(f"Executing Test Query: '{test_input}'\n")
    
    system_instruction = (
        "You are a forensic ingestion agent for the local OSINT command center. "
        "When provided with raw target data or testimony, you must strictly: "
        "1. Extract the primary entity name. "
        "2. Generate a SHA-256 hash of the raw input using the generate_sha256_hash tool. "
        "3. Format the data for the BigQuery ledger using the format_bigquery_payload tool. "
        "Do not hallucinate data; rely solely on the tools provided."
    )
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=test_input,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[generate_sha256_hash, format_bigquery_payload],
            temperature=0.0,
        ),
    )
    
    print("\n[Agent Execution Output]")
    print(response.text)

if __name__ == "__main__":
    main()
