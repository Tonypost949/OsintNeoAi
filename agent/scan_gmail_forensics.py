import imaplib
import email
import json
import os
import sys
from email.header import decode_header

imaplib._MAXLINE = 100000000
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EMAIL_USER = "amd949609@gmail.com"
APP_PASS = "ykdduybiuexoejxk"

def safe_decode(header_val):
    if not header_val:
        return ""
    try:
        decoded_parts = decode_header(header_val)
        result = []
        for text, encoding in decoded_parts:
            if isinstance(text, bytes):
                try:
                    result.append(text.decode(encoding or "utf-8", errors="replace"))
                except Exception:
                    result.append(text.decode("latin1", errors="replace"))
            else:
                result.append(str(text))
        return "".join(result)
    except Exception:
        return str(header_val)

def extract_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if ctype == "text/plain" and "attachment" not in cdispo:
                try:
                    body += part.get_payload(decode=True).decode("utf-8", errors="replace") + "\n"
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
        except Exception:
            pass
    return body.strip()

def main():
    print("[*] Logging into IMAP for amd949609@gmail.com...")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL_USER, APP_PASS)
    print("[✓] Login successful!")

    target_folders = [
        "legal",
        "openclasssuits",
        "[Gmail]/Sent Mail",
        "[Gmail]/All Mail",
        "INBOX"
    ]

    keywords = ["shea", "stadium", "anaheim", "moreno", "k5", "evict", "sidhu", "ament", "surplus", "hcd", "pringle"]

    all_matches = []
    seen_ids = set()

    for folder in target_folders:
        try:
            status, _ = mail.select(f'"{folder}"', readonly=True)
            if status != "OK":
                status, _ = mail.select(folder, readonly=True)
            if status != "OK":
                print(f"[-] Could not select {folder}")
                continue
            
            print(f"\n=== Scanning Folder: {folder} ===")
            
            for kw in keywords:
                try:
                    status, data = mail.search(None, f'(OR SUBJECT "{kw}" BODY "{kw}")')
                    if status == "OK" and data[0]:
                        msg_ids = data[0].split()
                        print(f"  [+] Keyword '{kw}' in {folder}: {len(msg_ids)} matches")
                        for mid in msg_ids[-15:]:
                            mid_str = mid.decode("utf-8", errors="ignore")
                            dedup_key = f"{folder}_{mid_str}"
                            if dedup_key in seen_ids:
                                continue
                            seen_ids.add(dedup_key)

                            res, mdata = mail.fetch(mid, "(RFC822)")
                            if res == "OK" and mdata[0] and isinstance(mdata[0], tuple):
                                msg = email.message_from_bytes(mdata[0][1])
                                sub = safe_decode(msg.get("Subject"))
                                sender = safe_decode(msg.get("From"))
                                to = safe_decode(msg.get("To"))
                                date = safe_decode(msg.get("Date"))
                                body = extract_body(msg)
                                
                                match_obj = {
                                    "folder": folder,
                                    "keyword": kw,
                                    "id": mid_str,
                                    "subject": sub,
                                    "from": sender,
                                    "to": to,
                                    "date": date,
                                    "body": body[:3000],
                                    "body_snippet": body[:400]
                                }
                                all_matches.append(match_obj)
                                print(f"    -> [{date}] {sender} -> {to}: {sub[:80]}")
                except Exception as e:
                    pass
        except Exception as e:
            print(f"[-] Error in folder {folder}:", e)

    out_file = r"C:\Users\Amd949609\OsintNeoAi-1\data\gmail_shea_stadium_raw_hits.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_matches, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Search complete! Total distinct emails extracted: {len(all_matches)}")
    print(f"[✓] Saved to {out_file}")

if __name__ == "__main__":
    main()
