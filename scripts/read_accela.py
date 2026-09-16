import json

out_path = "C:/Users/Amd949609/StudioProjects/OsintNeoAi/data/live_accela_permits.json"
try:
    with open(out_path, "r") as f:
        data = json.load(f)
    print(json.dumps(data, indent=2))
except Exception as e:
    print(f"Error reading file: {e}")
