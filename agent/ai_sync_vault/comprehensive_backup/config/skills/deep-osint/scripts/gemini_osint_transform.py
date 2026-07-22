import sys
import json
import os
from google import genai
from maltego_trx.maltego import MaltegoTransform

def run_transform(raw_data):
    client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY', 'REDACTED'))
    response = client.models.generate_content(model='gemini-2.0-flash', contents=f"Analyze this data for the Master OSINT Sheet schema: {raw_data}. Return ONLY valid JSON.")
    
    transform = MaltegoTransform()
    try:
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(clean_json)
        
        if "Entities" in data:
            for p in data["Entities"].get("People", []):
                transform.addEntity("maltego.Person", p["Name"])
            for g in data["Entities"].get("Gov_Agencies", []):
                transform.addEntity("maltego.Organization", g["Name"])
            for a in data["Entities"].get("Addresses", []):
                transform.addEntity("maltego.Location", a["Address"])
    except Exception as e:
        transform.addUIMessage(f"Error: {str(e)}")
    return transform.returnOutput()

if __name__ == "__main__":
    input_value = sys.argv[-1] if len(sys.argv) > 1 else "Test"
    print(run_transform(input_value))