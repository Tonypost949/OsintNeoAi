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

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("====================================================")
    print("         QAG2 IMAP DIRECT GMAIL SCANNER             ")
    print("====================================================")
    print("[*] Bypassing Google Cloud Console OAuth restrictions...")
    
    # Prompt user for credentials securely via standard input
    # To prevent blocks, we use an App Password: https://myaccount.google.com/apppasswords
    print("\n[!] To connect, you need a Google App Password.")
    print("    1. Go to: https://myaccount.google.com/apppasswords")
    print("    2. Generate an app password (e.g. named 'QAG2 OSINT').")
    print("    3. Enter it below along with your email.")
    
    user_email = input("\nEnter your Gmail address: ").strip()
    if not user_email:
        user_email = "amd949609@gmail.com"
        print(f"Using default: {user_email}")
        
    app_password = input("Enter your 16-character App Password: ").replace(" ", "").strip()
    if not app_password:
        print("[-] Error: App Password cannot be empty.")
        sys.exit(1)
        
    try:
        print(f"\n[*] Connecting to imap.gmail.com...")
        imaplib._MAXLINE = 100000000 # Support large mailboxes
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        print(f"[*] Logging in as {user_email}...")
        mail.login(user_email, app_password)
        print("[+] Login Successful!")
        
        # Select Inbox
        mail.select("inbox")
        
        # Search for all emails
        print("[*] Fetching latest 30 messages...")
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            print("[-] Error searching mail.")
            sys.exit(1)
            
        mail_ids = messages[0].split()
        latest_ids = mail_ids[-30:] # Get latest 30
        
        connections = []
        
        print("-" * 80)
        print(f"{'DATE':<20} | {'FROM':<30} | {'SUBJECT'}")
        print("-" * 80)
        
        for m_id in reversed(latest_ids):
            res, msg_data = mail.fetch(m_id, "(RFC822)")
            if res != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Parse subject
                    subject, encoding = decode_header(msg["Subject"] or "No Subject")[0]
                    subject = clean_text(subject)
                    
                    # Parse sender
                    from_user, encoding = decode_header(msg["From"] or "Unknown")[0]
                    from_user = clean_text(from_user)
                    
                    # Parse date
                    date_str = msg["Date"] or "Unknown"
                    
                    # Brief text body extraction
                    snippet = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    body = part.get_payload(decode=True)
                                    snippet = clean_text(body)[:150].replace("\n", " ").strip()
                                    break
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True)
                            snippet = clean_text(body)[:150].replace("\n", " ").strip()
                        except Exception:
                            pass
                            
                    print(f"{date_str[:20]:<20} | {from_user[:30]:<30} | {subject[:26]}")
                    
                    connections.append({
                        "id": m_id.decode(),
                        "date": date_str,
                        "from": from_user,
                        "subject": subject,
                        "snippet": snippet
                    })
                    
        output_file = "gmail_imap_connections_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(connections, f, indent=2)
            
        print("-" * 80)
        print(f"[+] Successfully scanned Gmail! Connections saved to: {os.path.abspath(output_file)}")
        print("====================================================")
        
    except Exception as e:
        print(f"[-] IMAP Connection failed: {e}")
        print("[!] Make sure IMAP access is enabled in Gmail Settings -> Forwarding and POP/IMAP.")

if __name__ == '__main__':
    main()
