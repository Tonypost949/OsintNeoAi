import os
import sys
import urllib.request
import urllib.error
import re
import ssl

urls = [
    ("tab_01_tab_copy_options", "chrome-extension://micdllihgoppmejpecmkilggmaagfdmb/options.html"),
    ("tab_02_gemini_videos", "https://gemini.google.com/videos"),
    ("tab_03_ai_studio_projects", "https://aistudio.google.com/projects"),
    ("tab_04_gcp_iam_admin", "https://console.cloud.google.com/iam-admin/asset-inventory/dashboard?project=fast-booster-jlw03"),
    ("tab_05_ai_studio_rate_limits", "https://aistudio.google.com/docs/rate-limits"),
    ("tab_06_android_design_plan", "https://developer.android.com/design"),
    ("tab_07_scholar_pdf_extension", "chrome://extensions/?id=dahenjhkoodjbpjheillcadbppiidmhp"),
    ("tab_08_new_tab", "chrome://newtab/"),
    ("tab_09_gemini_fraud_court_service", "https://gemini.google.com/app/dd16f3040e871005"),
    ("tab_10_gdoc_fraud_court_1", "https://docs.google.com/document/d/1V7RWfJuzUrDhezT316aztUfwHft2g7iJD0u7Y-DjIro/edit?tab=t.0"),
    ("tab_11_gdoc_fraud_court_2", "https://docs.google.com/document/d/1NVIimKRlqU9G9GY1VSmmsv4-9mY7Xx8rj8tQboqukCo/edit?tab=t.0"),
    ("tab_12_google_search", "https://www.google.com/search?q=google"),
    ("tab_13_google_search_process_server", "https://www.google.com/search?q=what+company+serves+documents+to+people+for+court"),
    ("tab_14_extensions_shortcuts", "chrome://extensions/shortcuts")
]

output_dir = r"C:\OsintNeoAi\reports\spark_digests\tab_html_dumps"
os.makedirs(output_dir, exist_ok=True)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
}

results = []

for name, url in urls:
    filename = f"{name}.html"
    filepath = os.path.join(output_dir, filename)
    
    if url.startswith("chrome://") or url.startswith("chrome-extension://"):
        placeholder = f"<!-- Internal Browser URL: {url} -->\n<html><body><h1>Internal Browser Protocol</h1><p>{url}</p></body></html>"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(placeholder)
        print(f"[INTERNAL PROTOCOL] Saved placeholder for {url} -> {filename}")
        results.append((name, url, "INTERNAL_PROTOCOL", len(placeholder)))
        continue
        
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[SUCCESS] Downloaded {url} -> {filename} ({len(content)} bytes)")
            results.append((name, url, "DOWNLOADED", len(content)))
    except Exception as e:
        err_msg = str(e)
        placeholder = f"<!-- Download Attempt Failed: {err_msg} -->\n<html><body><h1>URL: {url}</h1><p>Error: {err_msg}</p><p>Note: Requires active session cookies/auth to fetch full DOM.</p></body></html>"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(placeholder)
        print(f"[REQUIRES AUTH / REDIRECT] Saved status placeholder for {url} ({err_msg}) -> {filename}")
        results.append((name, url, f"AUTH_REQUIRED ({err_msg})", len(placeholder)))

print("\n--- DOWNLOAD SUMMARY ---")
for r in results:
    print(r)
