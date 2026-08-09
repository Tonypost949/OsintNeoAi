import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuration for automated email alerts using generated app password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "anthonymichaeldimarcello@gmail.com"
APP_PASSWORD = "nsqj quiv snfr wvaf" # Generated app password

def send_evidence_alert(subject, body_content, recipient="anthonymichaeldimarcello@gmail.com"):
    print("=" * 60)
    print("  INITIATING SECURE EMAIL NOTIFICATION  ")
    print("=" * 60)
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body_content, 'plain'))
    
    try:
        print(f"Connecting to SMTP server {SMTP_SERVER}:{SMTP_PORT}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        
        print("Logging in using secure App Password...")
        server.login(SENDER_EMAIL, APP_PASSWORD)
        
        print(f"Sending email to {recipient}...")
        server.sendmail(SENDER_EMAIL, recipient, msg.as_string())
        server.quit()
        print("[OK] Alert email sent successfully!")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to send email alert: {e}")
        return False

if __name__ == "__main__":
    # Test alert
    send_evidence_alert("TEST ALERT: OSINT Automated Mail Active", "Secure connection established using app password.")
