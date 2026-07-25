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

def search_mailbox(mail, folder, query):
    try:
        print(f"[*] Selecting folder '{folder}'...")
        status, _ = mail.select(folder, readonly=True)
        if status != "OK":
            print(f"[-] Could not select folder '{folder}'")
            return []
            
        print(f"[*] Searching for '{query}' in '{folder}'...")
        status, messages = mail.search(None, f'TEXT "{query}"')
        if status != "OK":
            print(f"[-] Search failed in folder '{folder}'")
            return []
            
        mail_ids = messages[0].split()
        print(f"[+] Found {len(mail_ids)} matching emails in '{folder}'")
        
        results = []
        for m_id in mail_ids:
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
                    
                    to_user, encoding = decode_header(msg["To"] or "Unknown")[0]
                    to_user = clean_text(to_user)
                    
                    date_str = msg["Date"] or "Unknown"
                    
                    # Extract body/snippet
                    body_text = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                try:
                                    body_text = clean_text(part.get_payload(decode=True))
                                    break
                                except Exception:
                                    pass
                    else:
                        try:
                            body_text = clean_text(msg.get_payload(decode=True))
                        except Exception:
                            pass
                            
                    results.append({
                        "folder": folder,
                        "id": m_id.decode(),
                        "date": date_str,
                        "from": from_user,
                        "to": to_user,
                        "subject": subject,
                        "snippet": body_text[:300].replace("\n", " ").strip(),
                        "body": body_text
                    })
        return results
    except Exception as e:
        print(f"[-] Error searching folder '{folder}': {e}")
        return []

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
        
    user_email = "amd949609@gmail.com"
    app_password = "rvem jbyp ckdj vvob"
    query = "Marshall Wu"
    
    print("====================================================")
    print(f"    GMAIL SEARCH: TARGET [{query}]")
    print("====================================================")
    
    try:
        print("[*] Connecting to imap.gmail.com...")
        imaplib._MAXLINE = 100000000
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        
        print(f"[*] Logging in as {user_email}...")
        mail.login(user_email, app_password)
        print("[+] Login Successful!")
        
        all_results = []
        
        # Search common folders (excluding All Mail for speed)
        folders_to_search = ["inbox", '"[Gmail]/Sent Mail"']
        for folder in folders_to_search:
            results = search_mailbox(mail, folder, query)
            all_results.extend(results)
            
        output_file = "marshall_wu_search_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
            
        print("====================================================")
        print(f"[+] Scan completed. Total matches: {len(all_results)}")
        print(f"[+] Saved results to: {os.path.abspath(output_file)}")
        print("====================================================")
        
    except Exception as e:
        print(f"[-] Connection or Search failed: {e}")

if __name__ == '__main__':
    main()
