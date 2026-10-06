import imaplib
import email
from email.header import decode_header
import sys

def fetch_amd_sent_mail():
    user = "amd949609@gmail.com"
    pas = "hsmajxgytrvzrvwc"
    
    print(f"Connecting to Gmail IMAP for {user}...")
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, pas)
        print("[+] Authentication Successful!")
        
        # Select Sent Mail folder
        status, folder_list = mail.list()
        sent_folder = '"[Gmail]/Sent Mail"'
        mail.select(sent_folder)
        
        # Search for May 23 2022
        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        print(f"[+] Total Sent Messages Found in {user}: {len(mail_ids)}")
        
        found_target = False
        for mid in reversed(mail_ids):
            res, msg_data = mail.fetch(mid, '(RFC822)')
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    subject = str(msg.get("Subject", ""))
                    date_hdr = str(msg.get("Date", ""))
                    
                    if "Shea" in subject or "Angels" in subject or "Moreno" in subject or "23 May 2022" in date_hdr or "May 2022" in date_hdr:
                        found_target = True
                        print(f"\n==========================================")
                        print(f"MATCH FOUND!")
                        print(f"Date: {date_hdr}")
                        print(f"From: {msg.get('From')}")
                        print(f"To: {msg.get('To')}")
                        print(f"Subject: {subject}")
                        print(f"==========================================")
                        
                        body_content = ""
                        if msg.is_multipart():
                            for p in msg.walk():
                                ctype = p.get_content_type()
                                if ctype == "text/plain":
                                    body_content = p.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                        else:
                            body_content = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                            
                        print("FULL VERBATIM BODY:")
                        print(body_content)
                        print("==========================================\n")
                        
                        # Save full body to file
                        out_file = r"C:\Amd949609_Antigravity_v1\tasks\anaheim_evidence_audit\verbatim_may23_email.txt"
                        with open(out_file, "w", encoding="utf-8") as out:
                            out.write(f"Subject: {subject}\nDate: {date_hdr}\nFrom: {msg.get('From')}\nTo: {msg.get('To')}\n\n{body_content}")
                        print(f"[+] Full verbatim email saved to: {out_file}")
                        break
            if found_target:
                break
                
    except Exception as e:
        print(f"[-] Error: {e}")

if __name__ == "__main__":
    fetch_amd_sent_mail()
