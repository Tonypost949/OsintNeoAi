import urllib.request
import json
import subprocess
import sys

print("Fetching active gcloud access token...")
try:
    token = subprocess.check_output("gcloud auth print-access-token", shell=True).decode('utf-8').strip()
    print("Token fetched successfully.")
except Exception as e:
    print("Failed to fetch token:", e)
    sys.exit(1)

project_id = "project-743aab84-f9a5-4ec7-954"
url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent"

payload = {
    "contents": [{
        "role": "user",
        "parts": [{
            "text": "Hello! Confirm that you are working and billed correctly through my Google Cloud credits."
        }]
    }]
}

data = json.dumps(payload).encode('utf-8')
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

req = urllib.request.Request(url, data=data, headers=headers, method='POST')

try:
    with urllib.request.urlopen(req) as response:
        res_data = response.read().decode('utf-8')
        res_json = json.loads(res_data)
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        print("\n--- VERTEX AI REST SUCCESS ---")
        print("Response text:", text.strip())
        print("------------------------------")
except Exception as e:
    print(f"\n--- VERTEX AI REST FAILED ---")
    if hasattr(e, 'read'):
        print(e.read().decode('utf-8'))
    else:
        print(type(e).__name__, ":", e)
    print("------------------------------")
