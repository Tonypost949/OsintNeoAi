import zipfile
import os

zip_path = r"C:\OSINTNEOAI\makavelli\OSINTNEOAI_EVERYTHING_IN_ONE.zip"
post_text_path = r"C:\OSINTNEOAI\makavelli\POST_THIS_TEXT.txt"

post_content = """⚡ OSINTNeoAi — Official Lead Intelligence Node.

"See More. Know First. Trust Nothing. Verify Everything."

Tactical OSINT Agent (Makaveli) is now live for public forensic correlation:
👉 https://tonypost949.github.io/OsintNeoAi/makavelli/

Drop a target domain, company name, or registry docket below to initiate tracking."""

with open(post_text_path, "w", encoding="utf-8") as f:
    f.write(post_content)

with zipfile.ZipFile(zip_path, "w") as z:
    z.write(r"C:\OSINTNEOAI\makavelli\avatar\circular_transparent.png", "OSINT_NEO_AI_circular_avatar_transparent.png")
    z.write(r"C:\OSINTNEOAI\makavelli\avatar\banner_black.png", "osint_neo_ai_banner.png")
    z.write(r"C:\OSINTNEOAI\scripts\EVERYTHING_IN_ONE_POST.py", "EVERYTHING_IN_ONE_POST.py")
    z.write(post_text_path, "POST_THIS_TEXT.txt")

print(f"[SUCCESS] Built: {zip_path}")
