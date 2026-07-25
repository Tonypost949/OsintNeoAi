import os

target_dirs = [
    r"C:\Users\HP\Downloads",
    r"c:\Users\HP\OneDrive\Documents\AG2OSINTNEOMAXX",
    r"C:\Users\HP\.gemini\config"
]

print("Searching for existing token.json or credentials.json...")
for target in target_dirs:
    for root, dirs, files in os.walk(target):
        if "node_modules" in root or ".git" in root or ".venv" in root:
            continue
        for file in files:
            if file in ["token.json", "credentials.json", "service_account.json"]:
                print(f"FOUND: {os.path.join(root, file)}")
