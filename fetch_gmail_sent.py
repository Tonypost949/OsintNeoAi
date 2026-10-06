import imaplib
import email
from email.header import decode_header
import sys

def check_sent_mail():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login("osintneoai@gmail.com", "dbaptkyadvratiow")
        
        # Select Sent Mail folder
        status, folder_list = mail.list()
        sent_folder = None
        for f in folder_list:
            decoded_f = f.decode('utf-8')
            if 'Sent' in decoded_f:
                # Extract folder name in quotes or last part
                parts = decoded_f.split(' "/" ')
                if len(parts) > 1:
                    sent_folder = parts[1]
                else:
                    sent_folder = decoded_f.split()[-1]
                break
        
        if not sent_folder:
            sent_folder = '"[Gmail]/Sent Mail"'
            
        print(f"Targeting folder: {sent_folder}")
        mail.select(sent_folder)
        
        # Search for Anaheim / Stadium / Sidhu / May 2022
        status, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        print(f"Total Sent Messages Found: {len(mail_ids)}")
        
        for mid in mail_ids[-30:]:
            res, msg_data = mail.fetch(mid, '(RFC822)')
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    subject = msg.get('Subject', '')
                    date = msg.get('Date', '')
                    to = msg.get('To', '')
                    print(f"Date: {date} | To: {to} | Subj: {subject}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_sent_mail()
