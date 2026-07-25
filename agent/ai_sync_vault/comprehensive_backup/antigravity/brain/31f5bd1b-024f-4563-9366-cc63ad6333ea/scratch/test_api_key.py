import urllib.request
import json

keys_to_test = {
    "GCP Key (UsFFc)": "AIzaSyDO5fKdpoBFxbk-9Tv8W1DAH0G8VcUsFFc",
    "Old Key (e6FQ)": "AIzaSyBc2q4I5fbjLFCM8q-lR-H_-lrJwbxGh9Q"
}

models = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash"
]

payload = {
    "contents": [{
        "parts": [{
            "text": "Hello! Confirm connection."
        }]
    }]
}

data = json.dumps(payload).encode('utf-8')

for name, key in keys_to_test.items():
    print(f"\n==================================================")
    print(f"TESTING KEY: {name}")
    print(f"==================================================")
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
        print(f"Trying model: {model_name}...")
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urllib.request.urlopen(req) as response:
                res_data = response.read().decode('utf-8')
                res_json = json.loads(res_data)
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                print(f"  SUCCESS! Response: {text.strip()}")
                break
        except Exception as e:
            print(f"  FAILED: {type(e).__name__}")
            if hasattr(e, 'read'):
                err_msg = e.read().decode('utf-8').strip()
                # Parse short error
                try:
                    err_json = json.loads(err_msg)
                    print(f"    Message: {err_json['error']['message']}")
                except Exception:
                    print(f"    Message: {err_msg[:200]}")
            else:
                print(f"    Message: {e}")
