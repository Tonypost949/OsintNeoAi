import imaplib
import email
from email.header import decode_header
import json
import os
import sys

def clean_text(text):
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='ignore')
    return text

def safe_print(text):
    try:
        sys.stdout.buffer.write(text.encode('utf-8') + b'\n')
    except Exception:
        try:
            print(text.encode('ascii', errors='ignore').decode('ascii'))
        except Exception:
            pass

def main():
    safe_print("====================================================")
    safe_print("         AUTOMATED GMAIL OSINT SCANNER              ")
    safe_print("====================================================")
    
    user_email = "amd949609@gmail.com"
    app_passwords = ["jsmjmqlaevknfomg", "lszvbfgjkktqefcm"]
    
    mail = None
    success_password = None
    
    for app_password in app_passwords:
        try:
            safe_print(f"[*] Trying App Password: {app_password[:4]}...{app_password[-4:]} for {user_email}...")
            imaplib._MAXLINE = 100000000
            temp_mail = imaplib.IMAP4_SSL("imap.gmail.com")
            temp_mail.login(user_email, app_password)
            safe_print("[+] Login Successful!")
            mail = temp_mail
            success_password = app_password
            break
        except Exception as e:
            safe_print(f"[-] Failed with this password: {e}")
            
    if not mail:
        safe_print("[-] All login attempts failed. Please double check the App Passwords.")
        sys.exit(1)
        
    try:
        # Select Inbox
        mail.select("inbox")
        
        # Search all mail or specifically look for keywords
        safe_print("[*] Searching for whistleblower, Yamada, and case-related communications...")
        keywords = ["Yamada", "Navigation", "Knabb", "disgrace", "whistleblower", "audit", "housing", "toxic"]
        
        all_matches = []
        
        for kw in keywords:
            status, messages = mail.search(None, f'BODY "{kw}"')
            if status == "OK" and messages[0]:
                mail_ids = messages[0].split()
                safe_print(f"[+] Found {len(mail_ids)} messages matching keyword: '{kw}'")
                for m_id in mail_ids[-30:]: # fetch latest 30 matching message IDs for each keyword to keep it efficient and complete
                    if m_id not in [m["id"] for m in all_matches]:
                        all_matches.append({"id": m_id, "keyword": kw})
                        
        if not all_matches:
            # Fallback: search all
            safe_print("[-] No keyword-specific messages found in search. Fetching latest 100 general messages...")
            status, messages = mail.search(None, "ALL")
            if status == "OK" and messages[0]:
                for m_id in messages[0].split()[-100:]:
                    all_matches.append({"id": m_id, "keyword": "latest"})
                    
        connections = []
        safe_print("-" * 120)
        safe_print(f"{'DATE':<25} | {'FROM':<35} | {'SUBJECT'}")
        safe_print("-" * 120)
        
        for item in reversed(all_matches):
            m_id = item["id"]
            try:
                res, msg_data = mail.fetch(m_id, "(RFC822)")
                if res != "OK":
                    continue
                    
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject, encoding = decode_header(msg["Subject"] or "No Subject")[0]
                        subject = clean_text(subject)
                        
                        from_user, encoding = decode_header(msg["From"] or "Unknown")[0]
                        from_user = clean_text(from_user)
                        
                        date_str = msg["Date"] or "Unknown"
                        
                        snippet = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True)
                                        snippet = clean_text(body)[:600].replace("\n", " ").strip()
                                        break
                                    except Exception:
                                        pass
                        else:
                            try:
                                body = msg.get_payload(decode=True)
                                snippet = clean_text(body)[:600].replace("\n", " ").strip()
                            except Exception:
                                pass
                                
                        safe_print(f"{date_str[:25]:<25} | {from_user[:35]:<35} | {subject[:50]}")
                        
                        connections.append({
                            "id": m_id.decode(),
                            "keyword_match": item["keyword"],
                            "date": date_str,
                            "from": from_user,
                            "subject": subject,
                            "snippet": snippet
                        })
            except Exception as e:
                safe_print(f"[-] Skipped message ID {m_id.decode() if isinstance(m_id, bytes) else m_id}: {e}")
                    
        output_file = "C:\\Users\\HP\\.gemini\\antigravity\\brain\\71e7b1d1-f50b-477e-a713-942e8319b97d\\scratch\\automated_gmail_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(connections, f, indent=2, ensure_ascii=False)
            
        safe_print("-" * 120)
        safe_print(f"[+] Scan Complete! Extracted {len(connections)} relevant emails and saved to:\n    {output_file}")
        safe_print("====================================================")
        
    except Exception as e:
        safe_print(f"[-] Error processing inbox: {e}")

if __name__ == '__main__':
    main()
