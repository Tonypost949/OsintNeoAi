#!/usr/bin/env python3
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email, from_email=None, app_password=None):
    from_email = from_email or os.environ.get("GMAIL_USER")
    app_password = app_password or os.environ.get("GMAIL_APP_PASSWORD")

    if not from_email or not app_password:
        print("Error: Missing GMAIL_USER or GMAIL_APP_PASSWORD environment variables.")
        print("Usage: export GMAIL_USER='your_email@gmail.com'")
        print("       export GMAIL_APP_PASSWORD='your_16_char_app_password'")
        sys.exit(1)

    # Construct Email Message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP Server (Port 587 with STARTTLS)
        print("Connecting to Gmail SMTP server (smtp.gmail.com:587)...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()  # Secure connection via TLS
        server.ehlo()

        # Authenticate
        print("Authenticating...")
        server.login(from_email, app_password)

        # Send Email
        print(f"Sending email to {to_email}...")
        server.send_message(msg)
        server.quit()

        print("SUCCESS: Email sent successfully!")
        return True

    except Exception as e:
        print(f"FAILED to send email: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 send_email.py <recipient_email> <subject> [body_text]")
        sys.exit(1)

    recipient = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3] if len(sys.argv) > 3 else "Notification from OSINTNeoAI Termux Engine."

    send_email(subject, body, recipient)
