import imaplib
import email
import os
from email.header import decode_header

EMAIL_ADDRESS = "anthonymichaeldimarcello@gmail.com"
APP_PASSWORD = "nsqj quiv snfr wvaf"
TARGET_FILENAME = "OSINT-NeoAI-Manus-Export.tar.gz"
DEST_DIR = r"C:\Users\HP\OneDrive\Documents\opencode_work"

def main():
    print(f"[*] Connecting to Gmail IMAP for {EMAIL_ADDRESS}...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDRESS, APP_PASSWORD)
        print("[+] Login successful!")
    except Exception as e:
        print(f"[ERROR] Failed to login: {e}")
        return
        
    mail.select("inbox")
    
    # Search for emails
    print(f"[*] Searching inbox for attachments...")
    status, messages = mail.search(None, 'ALL')
    
    if status != "OK" or not messages[0]:
        print("[!] No messages found.")
        return
        
    msg_ids = messages[0].split()
    print(f"[*] Found {len(msg_ids)} total message(s). Scanning from newest to oldest...")
    
    found = False
    for msg_id in reversed(msg_ids):
        res, msg_data = mail.fetch(msg_id, "(RFC822)")
        if res != "OK":
            continue
            
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")
                
                # Strip out non-ascii characters for terminal printing
                clean_subject = subject.encode('ascii', 'ignore').decode('ascii')
                print(f"  - Checking: '{clean_subject}'")
                
                # Check for attachments
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue
                        
                    filename = part.get_filename()
                    if filename:
                        filename, encoding = decode_header(filename)[0]
                        if isinstance(filename, bytes):
                            filename = filename.decode(encoding or "utf-8", errors="ignore")
                            
                        filename = filename.strip()
                        if TARGET_FILENAME.lower() in filename.lower() or filename.lower().endswith(".tar.gz"):
                            print(f"    [+] Match found! Filename: {filename}")
                            os.makedirs(DEST_DIR, exist_ok=True)
                            filepath = os.path.join(DEST_DIR, TARGET_FILENAME)
                            
                            print(f"    [*] Downloading attachment to: {filepath}...")
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                                
                            print(f"[SUCCESS] Saved attachment to {filepath}")
                            found = True
                            break
                            
            if found:
                break
        if found:
            break
            
    mail.logout()
    
    if not found:
        print("[!] Target attachment was not found in the email scan.")

if __name__ == "__main__":
    main()
