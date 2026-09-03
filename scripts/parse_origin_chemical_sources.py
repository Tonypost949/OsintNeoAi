import re
from pathlib import Path

txt_file = Path(r'C:\OsintNeoAi\evidence\geotracker_17631_cameron_full_text.txt')
content = txt_file.read_text(encoding='utf-8', errors='ignore')

# Search for section 2.0 Background, 2.1 Site Description, History, Former Use, Agricultural, Industrial
match_history = re.findall(r'BACKGROUND[\s\S]{1,4000}3\.0', content, re.IGNORECASE)

print("=== HISTORICAL SITE BACKGROUND & CONTAMINATION ORIGIN ===")
if match_history:
    print(match_history[0][:3500])
else:
    print("Background section not matched directly. Searching key terms...")
    for p in content.split('--- PAGE '):
        if '2.0 BACKGROUND' in p or '2.1 SITE DESCRIPTION' in p or 'historical' in p.lower():
            print(f"--- PAGE {p[:2000]}\n")
