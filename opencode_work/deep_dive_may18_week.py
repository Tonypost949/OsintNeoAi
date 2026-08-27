import json, pathlib, datetime, glob, re
from datetime import datetime, timezone
from collections import Counter

week_start = datetime(2022,5,15,tzinfo=timezone.utc)
week_end = datetime(2022,5,25,23,59,59,tzinfo=timezone.utc)

print(f"Deep dive week {week_start.date()} to {week_end.date()}")

# Check gmail hits
for path in [r"C:\OsintNeoAi\gmail_amd949609_hits.json", r"C:\OsintNeoAi\gmail_govt_responses_hits.json", r"C:\OsintNeoAi\all_photos_metadata.json", r"C:\OsintNeoAi\GEMINI_NEW_INTEL_EXTRACT.md"]:
    p = pathlib.Path(path)
    if not p.exists():
        print(f"Missing {path}")
        continue
    print(f"\n=== {p.name} ===")
    text = p.read_text(encoding="utf-8", errors="ignore")
    # try json
    try:
        data = json.loads(text)
        if isinstance(data, list):
            print(f"List with {len(data)} entries")
            # try to find date field
            for item in data[:3]:
                print(str(item)[:500])
            # filter by date if possible
            matched = []
            for item in data:
                date_str = item.get("date") or item.get("Date") or item.get("timestamp") or ""
                if not date_str:
                    continue
                # try parse
                try:
                    # handle various formats
                    # e.g., "2022-05-23T22:16:00Z" or "Mon, 23 May 2022 22:16:00 GMT"
                    dt = None
                    for fmt in ["%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d"]:
                        try:
                            dt = datetime.strptime(date_str.split(" (")[0].strip(), fmt)
                            if dt.tzinfo is None:
                                dt = dt.replace(tzinfo=timezone.utc)
                            break
                        except: continue
                    if dt is None:
                        # try fromisoformat
                        try:
                            dt = datetime.fromisoformat(date_str.replace("Z","+00:00"))
                        except: continue
                    if week_start <= dt <= week_end:
                        matched.append((dt, item))
                except Exception as e:
                    pass
            print(f"Matched in week: {len(matched)}")
            for dt, item in sorted(matched)[:20]:
                print(f"{dt.date()} | {item.get('subject') or item.get('snippet','')[:120]} | {item.get('from_user') or ''}")
        elif isinstance(data, dict):
            print(f"Dict keys: {list(data.keys())[:10]}")
    except Exception as e:
        # text file, grep for dates
        print(f"Text file, searching for May 2022 dates...")
        lines = text.split("\n")
        hits = [l for l in lines if "2022" in l and ("May" in l or "05" in l)]
        # filter week
        week_hits = []
        for line in hits:
            if any(d in line for d in ["May 15","May 16","May 17","May 18","May 19","May 20","May 21","May 22","May 23","May 24","May 25","2022-05-1","2022-05-2"]):
                week_hits.append(line)
        print(f"Found {len(week_hits)} lines with May dates")
        for l in week_hits[:20]:
            print(l[:400])

# Also scan exports
print("\n=== exports/chat_export_latest.md May week ===")
p = pathlib.Path(r"C:\OsintNeoAi\exports\chat_export_latest.md")
if p.exists():
    text = p.read_text(encoding="utf-8", errors="ignore")
    for pat in ["May 18","May 19","May 20","May 21","May 22","May 23","May 24","2022-05"]:
        if pat in text:
            idx = text.find(pat)
            print(text[max(0,idx-200):idx+400].replace("\n"," ")[:600])

# Scan GEMINI files
for p in pathlib.Path(r"C:\OsintNeoAi").glob("GEMINI*.md"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    if "2022" in text and "May" in text:
        print(f"\n=== {p.name} ===")
        for line in text.split("\n"):
            if "May" in line and "2022" in line:
                print(line[:500])

# Scan .agents handoff
for p in pathlib.Path(r"C:\OsintNeoAi\.agents").rglob("*.md"):
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "2022-05-1" in text or "May 18" in text or "May 23" in text or "2022-05-23" in text:
            print(f"\n=== .agents {p.relative_to(r'C:\OsintNeoAi')} ===")
            for line in text.split("\n"):
                if "2022-05" in line or "May 18" in line or "May 23" in line:
                    print(line[:500])
    except: pass

# Scan BigQuery local json if exists?
print("\n=== Done ===")
