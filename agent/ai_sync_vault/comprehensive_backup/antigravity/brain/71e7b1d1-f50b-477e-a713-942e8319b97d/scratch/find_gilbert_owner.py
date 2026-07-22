import os
import pandas as pd

scratch_dir = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch"
out_path = os.path.join(scratch_dir, "gilbert_search_hits.txt")

with open(out_path, "w", encoding="utf-8") as out:
    out.write("GILBERT AND EAST COVENANT HOUSE DETAILED SEARCH HITS\n")
    out.write("===================================================\n\n")

    # Search Excel Files
    out.write("--- Excel Files Search ---\n")
    excel_files = [f for f in os.listdir(scratch_dir) if f.endswith(".xlsx")]
    for f in excel_files:
        path = os.path.join(scratch_dir, f)
        try:
            xl = pd.ExcelFile(path)
            for sheet in xl.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet)
                mask = df.astype(str).apply(lambda x: x.str.contains("Gilbert|East St|Covenant", case=False, na=False))
                matches = df[mask.any(axis=1)]
                if len(matches) > 0:
                    out.write(f"File: {f}, Sheet: {sheet}\n")
                    out.write(matches.to_string() + "\n")
                    out.write("-" * 50 + "\n")
        except Exception as e:
            out.write(f"Error reading Excel {f}: {e}\n")

    # Search Text Files
    out.write("\n--- Text Files Search ---\n")
    txt_files = [f for f in os.listdir(scratch_dir) if f.endswith(".txt") or f.endswith(".csv") or f.endswith(".html")]
    for f in txt_files:
        # Skip gilbert_search_hits.txt itself
        if f == "gilbert_search_hits.txt":
            continue
        path = os.path.join(scratch_dir, f)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                for i, line in enumerate(file, 1):
                    # Check for address patterns
                    line_lower = line.lower()
                    if "213" in line_lower and "gilbert" in line_lower:
                        out.write(f"File: {f}, Line {i}: {line.strip()}\n")
                    elif "632" in line_lower and "east" in line_lower:
                        out.write(f"File: {f}, Line {i}: {line.strip()}\n")
                    elif "covenant" in line_lower and "anaheim" in line_lower:
                        out.write(f"File: {f}, Line {i}: {line.strip()}\n")
                    elif "gilbert" in line_lower and ("trust" in line_lower or "llc" in line_lower or "holdings" in line_lower):
                        out.write(f"File: {f}, Line {i}: {line.strip()}\n")
        except Exception as e:
            out.write(f"Error reading Text {f}: {e}\n")

print("Gilbert and Covenant House search completed successfully. Output written to gilbert_search_hits.txt")
