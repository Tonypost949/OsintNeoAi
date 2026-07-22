import smtplib
from email.message import EmailMessage

sender_email = "amd949609@gmail.com"
app_password = "shyivmhfjeyakvpe"
receiver_email = "amd949609@gmail.com"
subject = "Antigravity Resurrection Protocol (Makaveli)"
body = "Attached is the requested ZIP file containing the Makaveli Resurrection Protocol."
file_path = r"C:\OsintNeoAi\Antigravity_Resurrection_Protocol_makaveli.zip"

msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email
msg.set_content(body)

with open(file_path, 'rb') as f:
    file_data = f.read()
    file_name = "Antigravity_Resurrection_Protocol_makaveli.zip"

msg.add_attachment(file_data, maintype='application', subtype='zip', filename=file_name)

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
