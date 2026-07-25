import os

folder = 'C:\\Users\\HP\\OneDrive\\Documents\\opencode_work'
for r, d, files in os.walk(folder):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(r, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    if '7969270' in file.read():
                        print("Found reference in:", path)
            except Exception as e:
                pass
