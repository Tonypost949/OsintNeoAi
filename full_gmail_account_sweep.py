import imaplib
import email
from email.header import decode_header
import json
import os

def full_gmail_sweep():
    user = "amd949609@gmail.com"
    pas = "hsmajxgytrvzrvwc"
    
    print(f"[+] Authenticating to Gmail for full account sweep: {user}")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, pas)
    print("[+] Successfully logged in via App Password!")
    
    # Search all mailboxes / All Mail
    mail.select('"[Gmail]/All Mail"')
    
    keywords = ["Shea", "Angels", "Moreno", "Roundtree", "Stadium", "Sidhu", "Ament", "Flint", "Mercy House"]
    
    all_corroborations = []
    
    for kw in keywords:
        print(f"[+] Searching All Mail for keyword: {kw}...")
        status, data = mail.search(None, f'OR (TEXT "{kw}") (SUBJECT "{kw}")')
        ids = data[0].split()
        print(f"    Found {len(ids)} matching emails for '{kw}'.")
        
        for eid in ids[-25:]: # Analyze top 25 per keyword
            try:
                res, msg_data = mail.fetch(eid, '(RFC822)')
                for part in msg_data:
                    if isinstance(part, tuple):
                        msg = email.message_from_bytes(part[1])
                        subject = str(msg.get("Subject", ""))
                        date_hdr = str(msg.get("Date", ""))
                        from_hdr = str(msg.get("From", ""))
                        to_hdr = str(msg.get("To", ""))
                        
                        body = ""
                        if msg.is_multipart():
                            for p in msg.walk():
                                if p.get_content_type() == "text/plain":
                                    body = p.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                            
                        item = {
                            "keyword": kw,
                            "email_id": eid.decode('utf-8'),
                            "date": date_hdr,
                            "from": from_hdr,
                            "to": to_hdr,
                            "subject": subject,
                            "body_snippet": body[:500] if body else ""
                        }
                        all_corroborations.append(item)
            except Exception as e:
                pass
                
    out_dir = r"C:\Amd949609_Antigravity_v1\tasks\anaheim_evidence_audit"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "full_gmail_account_corroboration.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_corroborations, f, indent=2)
        
    print(f"\n[+] Full Gmail Sweep Complete! Total Corroborating Matches: {len(all_corroborations)}")
    print(f"[+] Saved master corroboration database to: {out_file}")

if __name__ == "__main__":
    full_gmail_sweep()
