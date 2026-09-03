import os
import json
from pathlib import Path

# Search query helper for August 20, 2021 court transmittals
query = 'in:anywhere (30-2021-01201327 OR rwclegal OR Luege OR "Lockout is STAYED") after:2021/08/19 before:2021/08/22'

print(f"Targeting live Gmail API search for query: {query}")
print("1. Check browser window opened to live search results.")
print("2. Search terms: 30-2021-01201327, efiling@rwclegal.com, Carmen Luege, Lockout is STAYED.")
