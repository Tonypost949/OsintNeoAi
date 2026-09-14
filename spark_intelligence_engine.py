import os
import json
import csv
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ Warning: GEMINI_API_KEY not found in environment.")

def fetch_raw_intelligence_data():
    """
    Mock function to fetch raw intelligence data. 
    In production, this would query BigQuery, RSS feeds, or newly ingested CSVs.
    """
    print("[*] Fetching raw intelligence data for Spark...")
    return {
        "recent_dockets": ["8:2026-cv-00348"],
        "news_events": ["OC Health Officials Waved Off Conflict Warnings"],
        "anomalies": ["$10.4M diverted COVID-19 relief contracts"]
    }

def generate_spark_digest_and_enrichments(raw_data):
    """
    Uses Gemini (Spark) to generate the intelligence digest and lead correlations.
    """
    print("[*] Engaging Gemini (Spark) to generate intelligence digest and lead enrichments...")
    
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY_MISSING", []
        
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are an expert OSINT and Regulatory Intelligence AI. 
    Based on the following raw data, generate an executive digest covering financial compliance, regulatory enforcement, and whistleblower frameworks.
    Raw Data: {json.dumps(raw_data)}
    
    Format your response in TWO parts separated by '---ENRICHMENTS_JSON---':
    1. A professional Markdown intelligence digest (similar to an executive newsletter).
    2. A valid JSON array of new lead correlation enrichments containing keys: 'entity_name', 'correlation_type', 'confidence_score', 'reasoning'.
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        parts = text.split("---ENRICHMENTS_JSON---")
        digest_md = parts[0].strip()
        enrichments = []
        
        if len(parts) > 1:
            try:
                enrichments_text = parts[1].strip()
                # Clean up markdown code blocks if present
                if enrichments_text.startswith("```json"):
                    enrichments_text = enrichments_text[7:-3].strip()
                enrichments = json.loads(enrichments_text)
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse enrichments JSON: {e}")
                
        return digest_md, enrichments
    except Exception as e:
        print(f"⚠️ Gemini API Error: {e}")
        return "ERROR_GENERATING_DIGEST", []

def save_and_hash_digest(digest_md, report_date):
    """
    Saves the digest to the repository and returns the SHA-256 hash.
    """
    out_dir = Path("reports/spark_digests")
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"SPARK_DIGEST_{report_date}.md"
    
    file_path.write_text(digest_md, encoding="utf-8")
    print(f"✅ Spark Digest committed to repository: {file_path}")
    
    hasher = hashlib.sha256()
    hasher.update(file_path.read_bytes())
    return hasher.hexdigest()

def update_master_spark_sheet(enrichments):
    """
    Appends the new lead correlations to a local CSV (acting as the SPARK tab).
    """
    csv_path = Path("master_osint_sheet/SPARK_Correlations.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_exists = csv_path.exists()
    
    with open(csv_path, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Entity Name", "Correlation Type", "Confidence Score", "Reasoning"])
            
        timestamp = datetime.now(timezone.utc).isoformat()
        for e in enrichments:
            writer.writerow([
                timestamp,
                e.get("entity_name", ""),
                e.get("correlation_type", ""),
                e.get("confidence_score", ""),
                e.get("reasoning", "")
            ])
            
    print(f"✅ Master OSINT Sheet (SPARK tab) updated locally at: {csv_path}")

def send_spark_email_alert(report_date, digest_html, enrichments_count, report_hash):
    recipient = os.getenv("ALERT_RECIPIENT_EMAIL", "amd949609@gmail.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", os.getenv("GMAIL_USER", "amd949609@gmail.com"))
    smtp_password = os.getenv("SMTP_PASSWORD", os.getenv("GMAIL_APP_PASSWORD", ""))

    print(f"[*] Preparing Spark Dispatch to: {recipient}...")
    
    if not smtp_password:
        print("ℹ️ Note: SMTP_PASSWORD not configured. Email will not be sent.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 OSINT Spark Intelligence Digest — {report_date}"
        msg["From"] = f"Spark Intelligence Engine <{smtp_user}>"
        msg["To"] = recipient

        # Simple HTML Wrapper for the Markdown/HTML digest
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0b131e; color: #e2e8f0; padding: 25px;">
            <div style="max-width: 800px; margin: auto; background-color: #131d2e; border: 1px solid #1e293b; border-radius: 10px; padding: 25px;">
                <h2 style="color: #ecc94b; margin-top: 0;">⚡ OSINT & Regulatory Intelligence Digest (Spark)</h2>
                <div style="margin-bottom: 20px;">
                    {digest_html.replace(chr(10), '<br>')}
                </div>
                <hr style="border: 0; border-top: 1px solid #2d3748; margin: 20px 0;">
                <p style="color: #68d391; font-weight: bold;">✅ Generated {enrichments_count} new lead correlation enrichments.</p>
                <p style="font-size: 12px; color: #718096;">All structured findings have been logged directly into the SPARK tab of the local Master OSINT Sheet.</p>
                <div style="margin-top: 25px; padding: 12px; background-color: #0b131e; border-radius: 6px; font-size: 12px; color: #718096;">
                    🔒 <strong>NIST SHA-256 Checksum:</strong> <code>{report_hash}</code>
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
        print(f"✅ Spark Dispatch Successfully Delivered to {recipient}!")
        return True
    except Exception as e:
        print(f"⚠️ Email Dispatch Warning: {e}")
        return False

def run_spark_pipeline():
    now = datetime.now(timezone.utc)
    report_date = now.strftime("%Y-%m-%d")
    
    print("=" * 70)
    print(f"⚡ SPARK INTELLIGENCE ENGINE RUN: {report_date}")
    print("=" * 70)
    
    raw_data = fetch_raw_intelligence_data()
    digest_md, enrichments = generate_spark_digest_and_enrichments(raw_data)
    
    if digest_md != "GEMINI_API_KEY_MISSING":
        report_hash = save_and_hash_digest(digest_md, report_date)
        update_master_spark_sheet(enrichments)
        send_spark_email_alert(report_date, digest_md, len(enrichments), report_hash)
    else:
        print("⚠️ Pipeline halted. Please provide a GEMINI_API_KEY in the .env file.")

if __name__ == "__main__":
    run_spark_pipeline()
