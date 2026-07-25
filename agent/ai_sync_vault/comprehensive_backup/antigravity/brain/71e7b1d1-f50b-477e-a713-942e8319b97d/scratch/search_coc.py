import os

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
txt_files = [f for f in os.listdir(scratch_dir) if f.endswith(".txt") or f.endswith(".csv") or f.endswith(".html") or f.endswith(".xlsx")]

print("--- Searching for CoC, Continuum, or Homelessness terms in scratch files ---")
for f in os.listdir(scratch_dir):
    path = os.path.join(scratch_dir, f)
    if os.path.isdir(path):
        continue
    # Just check name first
    if "coc" in f.lower() or "continuum" in f.lower() or "homeless" in f.lower():
        print(f"Found file by name: {f}")
    
    # Check contents of text files
    if f.endswith(".txt") or f.endswith(".csv") or f.endswith(".md"):
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                for i, line in enumerate(file, 1):
                    line_lower = line.lower()
                    if "continuum of care" in line_lower or " coc " in line_lower or "cocs" in line_lower:
                        print(f"{f} Line {i}: {line.strip()[:150]}")
                        break
        except Exception:
            pass
