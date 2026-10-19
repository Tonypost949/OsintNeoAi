import urllib.request
import urllib.parse
import json
import re

url = "https://researchhelp.post.edu/az/content.php"
payload = {
    "site_id": "3972",
    "action": "116",
    "first": "",
    "subject_id": "",
    "type_id": "",
    "vendor_id": "",
    "access_mode_id": "",
    "page": "0",
    "search": ""
}

data = urllib.parse.urlencode(payload).encode("utf-8")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest"
}

req = urllib.request.Request(url, data=data, headers=headers)
try:
    with urllib.request.urlopen(req) as resp:
        content = json.loads(resp.read().decode("utf-8"))
        html = content.get("html", "")
        
        # Regex extraction
        entries = re.findall(r'<div[^>]*class="[^"]*s-lg-az-result[^"]*"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        if not entries:
            # Fallback title extraction
            titles = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html)
            print(f"[+] Found {len(titles)} links:")
            for href, text in titles:
                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if clean_text and not clean_text.startswith("More") and len(clean_text) > 2:
                    print(f"• {clean_text:<40} -> {href}")
        else:
            print(f"[+] Found {len(entries)} full database cards.")
            for e in entries:
                t_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', e)
                d_match = re.search(r'class="s-lg-az-result-description"[^>]*>(.*?)</div>', e, re.DOTALL)
                if t_match:
                    title = re.sub(r'<[^>]+>', '', t_match.group(2)).strip()
                    link = t_match.group(1)
                    desc = re.sub(r'<[^>]+>', '', d_match.group(1)).strip() if d_match else ""
                    print(f"\n=======================================================")
                    print(f"📚 {title}")
                    print(f"🔗 URL: {link}")
                    if desc:
                        print(f"📝 Description: {desc[:200]}...")
except Exception as ex:
    print(f"[-] Error fetching A-Z directory: {ex}")
