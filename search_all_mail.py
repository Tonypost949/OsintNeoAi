import imaplib
import email
from email.header import decode_header

def search_all_mailboxes():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("osintneoai@gmail.com", "dbaptkyadvratiow")
        
        status, folder_list = mail.list()
        print("Available folders:")
        for f in folder_list:
            print(f.decode('utf-8'))
            
        # Search All Mail
        mail.select('"[Gmail]/All Mail"')
        status, data = mail.search(None, 'OR OR (SUBJECT "Anaheim") (SUBJECT "Stadium") (SUBJECT "Sidhu")')
        ids = data[0].split()
        print(f"\nKeyword matches in All Mail: {len(ids)}")
        
        for mid in ids:
            res, msg_data = mail.fetch(mid, '(RFC822)')
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    print(f"Date: {msg.get('Date')} | From: {msg.get('From')} | To: {msg.get('To')} | Subj: {msg.get('Subject')}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_all_mailboxes()
