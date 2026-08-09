#!/usr/bin/env python3
import os
import sys
import smtplib
from email.mime.text import MIMEText

sender = os.environ.get("GMAIL_USER", "your_email@gmail.com")
password = os.environ.get("GMAIL_APP_PASSWORD", "your_app_password")  # Generate via Google Account security settings
receiver = os.environ.get("RECIPIENT_EMAIL", "recipient@gmail.com")

if len(sys.argv) > 1:
    receiver = sys.argv[1]

msg = MIMEText("Automated message sent directly from Termux terminal.")
msg["Subject"] = "Termux Alert"
msg["From"] = sender
msg["To"] = receiver

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()
    print("Email sent successfully.")
except Exception as e:
    print(f"Failed to send email: {e}")
