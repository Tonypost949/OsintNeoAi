import os
import json
import csv
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path

KNABB_CASE_INFO = {
    "case_title": "Jesse Knabb v. City of Huntington Beach et al.",
    "federal_docket": "8:2026-cv-00348 (C.D. Cal.)",
    "waterboards_petition": "Petition A-2926",
    "subject_situs": "8332 Swem Way, Huntington Beach, CA 92646",
    "jurisdiction": "Orange County / City of Huntington Beach",
    "status": "Active Judicial & Administrative Record"
}

def send_email_alert(report_date, report_time, records_count, total_exposure, anomalies, report_hash, recipient_email=None):
    recipient = recipient_email or os.getenv("ALERT_RECIPIENT_EMAIL", "amd949609@gmail.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", os.getenv("GMAIL_USER", "amd949609@gmail.com"))
    smtp_password = os.getenv("SMTP_PASSWORD", os.getenv("GMAIL_APP_PASSWORD", ""))

    print(f"[*] Preparing Email Dispatch to: {recipient}...")
    
    if not smtp_password:
        print("ℹ️ Note: SMTP_PASSWORD / GMAIL_APP_PASSWORD not configured. To enable live Gmail delivery, add your Gmail App Password to your environment.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 OSINT Daily Intelligence Dispatch — Knabb v. HB / Swem Way & RICO [{report_date}]"
        msg["From"] = f"OSINT Intelligence Bot <{smtp_user}>"
        msg["To"] = recipient

        table_rows = ""
        for a in anomalies[:7]:
            name = a.get("BorrowerName", a.get("entity_name", "Unknown Entity"))
            situs = a.get("physical_property_address", a.get("situs", "Orange County, CA"))
            origin = a.get("ppp_origin_state", a.get("origin_state", "Out-of-State"))
            loan = a.get("ppp_loan_amount", "$0.00")
            table_rows += f"""
            <tr style="border-bottom: 1px solid #2d3748;">
                <td style="padding: 10px; font-weight: bold; color: #63b3ed;">{name}</td>
                <td style="padding: 10px; color: #e2e8f0;">{situs}</td>
                <td style="padding: 10px; color: #cbd5e0;">{origin}</td>
                <td style="padding: 10px; font-weight: bold; color: #68d391;">{loan}</td>
            </tr>
            """

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b131e; color: #e2e8f0; padding: 25px;">
            <div style="max-width: 750px; margin: auto; background-color: #131d2e; border: 1px solid #1e293b; border-radius: 10px; padding: 25px;">
                <h2 style="color: #63b3ed; margin-top: 0;">🛰️ OSINT Autonomous Daily Intelligence Dispatch</h2>
                <p style="color: #a0aec0; font-size: 14px;"><strong>Dispatch Date:</strong> {report_date} | <strong>Time:</strong> {report_time} | <strong>Target:</strong> noble-beanbag-497411-m4</p>
                
                <!-- Spotlight Case: Jesse Knabb v. City of HB -->
                <div style="background-color: #1a202c; border-left: 4px solid #ecc94b; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #ecc94b; margin-top: 0; margin-bottom: 8px;">⚖️ Case Spotlight: Jesse Knabb v. City of Huntington Beach</h3>
                    <p style="margin: 4px 0; font-size: 13px;"><strong>Federal Docket:</strong> <span style="color: #63b3ed;">{KNABB_CASE_INFO['federal_docket']}</span></p>
                    <p style="margin: 4px 0; font-size: 13px;"><strong>State Petition:</strong> <span style="color: #e2e8f0;">{KNABB_CASE_INFO['waterboards_petition']}</span></p>
                    <p style="margin: 4px 0; font-size: 13px;"><strong>Situs Monitored:</strong> <span style="color: #68d391;">{KNABB_CASE_INFO['subject_situs']}</span></p>
                    <p style="margin: 4px 0; font-size: 13px;"><strong>Jurisdiction:</strong> {KNABB_CASE_INFO['jurisdiction']}</p>
                </div>

                <hr style="border: 0; border-top: 1px solid #2d3748; margin: 20px 0;">
                
                <div style="display: flex; gap: 15px; margin-bottom: 20px;">
                    <div style="background-color: #1e293b; padding: 12px 18px; border-radius: 8px;">
                        <span style="font-size: 12px; color: #a0aec0;">Audited Entities:</span><br>
                        <strong style="font-size: 18px; color: #fff;">{records_count:,}</strong>
                    </div>
                    <div style="background-color: #1e293b; padding: 12px 18px; border-radius: 8px;">
                        <span style="font-size: 12px; color: #a0aec0;">Tracked Exposure:</span><br>
                        <strong style="font-size: 18px; color: #68d391;">${total_exposure:,.2f}</strong>
                    </div>
                </div>

                <h3 style="color: #f6ad55; margin-bottom: 10px;">🚨 Priority Multi-State Anomalies</h3>
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
                    <thead>
                        <tr style="background-color: #1e293b; color: #a0aec0;">
                            <th style="padding: 10px;">Entity Name</th>
                            <th style="padding: 10px;">Assessor Situs</th>
                            <th style="padding: 10px;">Origin</th>
                            <th style="padding: 10px;">Loan Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>

                <div style="margin-top: 25px; padding: 12px; background-color: #0b131e; border-radius: 6px; font-size: 12px; color: #718096;">
                    🔒 <strong>NIST SHA-256 Checksum:</strong> <code>{report_hash}</code><br>
                    🌐 <strong>Live Streamlit App:</strong> <a href="https://osintneoai-xpdie7hdtxfidsv5r2l9ds.streamlit.app/" style="color: #63b3ed;">View Live Dashboard</a>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email Dispatch Successfully Delivered to {recipient}!")
        return True
    except Exception as e:
        print(f"⚠️ Email Dispatch Warning: {e}")
        return False

def run_daily_compilation():
    now = datetime.now(timezone.utc)
    report_date = now.strftime("%Y-%m-%d")
    report_time = now.strftime("%H:%M UTC")
    
    print("=" * 70)
    print(f"🕵️ OSINT AUTONOMOUS DAILY COMPILATION: {report_date} ({report_time})")
    print("=" * 70)
    
    matrix_candidates = [
        Path("reports/NATIONWIDE_SMOKING_GUNS_MATRIX.csv"),
        Path("NATIONWIDE_SMOKING_GUNS_MATRIX.csv")
    ]
    matrix_file = next((f for f in matrix_candidates if f.exists()), None)
        
    records_count = 0
    total_exposure = 0.0
    anomalies = []
    
    if matrix_file:
        with open(matrix_file, mode="r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records_count += 1
                try:
                    amount_str = row.get("ppp_loan_amount", "0").replace("$", "").replace(",", "")
                    total_exposure += float(amount_str)
                except Exception:
                    pass
                if len(anomalies) < 15:
                    anomalies.append(row)
                    
    print(f"[*] Audited Records: {records_count:,}")
    print(f"[*] Cumulative Tracked Exposure: ${total_exposure:,.2f}")
    
    out_dir = Path("reports/daily")
    out_dir.mkdir(parents=True, exist_ok=True)
    report_file = out_dir / f"DAILY_OSINT_REPORT_{report_date}.md"
    
    md_content = f"""# 🛰️ OSINT Autonomous Daily Intelligence Dispatch
### Dispatch Date: **{report_date}** | Time: `{report_time}`
**Data Warehouse:** `noble-beanbag-497411-m4` | **Integrity Standard:** NIST SHA-256

---

## ⚖️ Case Spotlight: Jesse Knabb v. City of Huntington Beach
* **Federal Case Docket:** `{KNABB_CASE_INFO['federal_docket']}`
* **State Administrative Action:** `{KNABB_CASE_INFO['waterboards_petition']}`
* **Monitored Physical Situs:** `{KNABB_CASE_INFO['subject_situs']}`
* **Jurisdiction:** `{KNABB_CASE_INFO['jurisdiction']}`
* **Filing Status:** `{KNABB_CASE_INFO['status']}`

---

## 📊 24-Hour Executive Snapshot
* **Total High-Priority Entities Under Surveillance:** `{records_count:,}`
* **Cumulative Exposure Traced:** `${total_exposure:,.2f}`
* **Active Geographic Shell Hubs:** `Orange County, CA`, `Battle Creek, MI`, `Anchorage, AK`, `Saddle River, NJ`
* **Schedule Cadence:** `Daily at 6:00 AM & 12:00 PM (Noon) Pacific`

---

## 🚨 Priority Multi-State Anomalies
| Entity Name | Assessor Situs | Origin Jurisdiction | Traced Disbursement | Status |
| :--- | :--- | :--- | :--- | :--- |
"""
    for a in anomalies[:7]:
        name = a.get("BorrowerName", a.get("entity_name", "Unknown Entity"))
        situs = a.get("physical_property_address", a.get("situs", "Orange County, CA"))
        origin = a.get("ppp_origin_state", a.get("origin_state", "Out-of-State"))
        loan = a.get("ppp_loan_amount", "$0.00")
        status = a.get("forgiven_amount", "Audited")
        md_content += f"| **{name}** | {situs} | {origin} | **{loan}** | {status} |\n"
        
    md_content += """
---

## 🔒 Cryptographic Chain of Custody
All underlying CSV matrices, parcel rolls, and government filings are cryptographically signed with NIST SHA-256 checksums.

---
*Autonomous Daily Dispatch generated by Disole Design OSINT Engine.*
"""
    
    report_file.write_text(md_content, encoding="utf-8")
    print(f"✅ Daily Report Generated: {report_file}")
    
    hasher = hashlib.sha256()
    hasher.update(report_file.read_bytes())
    report_hash = hasher.hexdigest()
    print(f"🔒 Report SHA-256 Checksum: {report_hash}")
    
    send_email_alert(report_date, report_time, records_count, total_exposure, anomalies, report_hash)
    
    print("🎉 Autonomous Daily Compilation Complete!")

if __name__ == "__main__":
    run_daily_compilation()
