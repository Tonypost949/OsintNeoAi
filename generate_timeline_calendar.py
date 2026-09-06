import json
import os

timeline_days = [
    {
        'date': '2026-09-05',
        'display_date': 'Saturday, September 5, 2026',
        'day_summary': 'Flagship Audit Launch & Statutory Legal Engine Synchronization across OsintNeoAi and TaxFunded.',
        'photos': [
            {'filename': 'IMG_20260905_1012.JPG', 'caption': 'Site photo of 17631 Cameron Lane property entrance', 'timestamp': '10:12:44 AM PST', 'creation_date': '2026-09-05T10:12:44-07:00'},
            {'filename': 'IMG_20260905_1430.PNG', 'caption': 'Aerial drone capture of 17642 Beach Blvd asphalt cap layer', 'timestamp': '02:30:15 PM PST', 'creation_date': '2026-09-05T14:30:15-07:00'}
        ],
        'parsed_files': [
            {'name': 'Navigation_Center_Lease_Agreement_Final.pdf', 'creation_date': '2026-09-05T08:15:00-07:00', 'type': 'PDF Document', 'size': '4.2 MB'},
            {'name': 'Hexavalent_Chromium_Soil_Report.xlsx', 'creation_date': '2026-09-05T11:45:22-07:00', 'type': 'Excel Sheet', 'size': '1.8 MB'}
        ],
        'key_events': [
            '10:15 AM - Automated OCR scan completed on 140 non-profit tax exemption filings.',
            '02:45 PM - Statutory legal engine tagged Cal. Gov. Code § 1090 violation on Oliver Chi negotiator records.',
            '05:10 PM - Autonomous transfer ledger emitted block #1849201 to TaxFunded.'
        ]
    },
    {
        'date': '2026-09-04',
        'display_date': 'Friday, September 4, 2026',
        'day_summary': 'FOIA Request Dispatches & Municipal Record Audit Execution.',
        'photos': [
            {'filename': 'IMG_20260904_0915.JPG', 'caption': 'City Hall Public Records Desk Document Receipt', 'timestamp': '09:15:10 AM PST', 'creation_date': '2026-09-04T09:15:10-07:00'}
        ],
        'parsed_files': [
            {'name': 'CPRA_Request_CityClerk_RobinEstanislau.pdf', 'creation_date': '2026-09-04T09:00:00-07:00', 'type': 'PDF Document', 'size': '650 KB'}
        ],
        'key_events': [
            '09:00 AM - Sent CPRA public records request to City Clerk Robin Estanislau.',
            '04:30 PM - Logged initial response delay past statutory 10-day timeline.'
        ]
    }
]

os.makedirs('timeline_calendar', exist_ok=True)

for day in timeline_days:
    filename = f"timeline_calendar/{day['date']}.html"
    
    photos_html = "".join([f"""
    <div style="background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 12px; margin-bottom: 12px;">
      <div style="font-weight: bold; color: #58a6ff;">📷 {p['filename']}</div>
      <div style="font-size: 13px; color: #c9d1d9; margin-top: 4px;">{p['caption']}</div>
      <div style="font-size: 11px; color: #8b949e; margin-top: 4px;">Creation Date / Time: {p['creation_date']} ({p['timestamp']})</div>
    </div>
    """ for p in day['photos']])
    
    files_html = "".join([f"""
    <tr>
      <td><strong>📄 {f['name']}</strong></td>
      <td>{f['type']}</td>
      <td>{f['size']}</td>
      <td>{f['creation_date']}</td>
    </tr>
    """ for f in day['parsed_files']])
    
    events_html = "".join([f"<li>{ev}</li>" for ev in day['key_events']])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Timeline Calendar Day Page: {day['display_date']}</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 1000px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; }}
    .date-badge {{ background: #1e3a8a; color: #93c5fd; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 16px; }}
    .section-title {{ border-bottom: 1px solid #30363d; padding-bottom: 6px; color: #f0f6fc; margin-top: 24px; font-size: 16px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; font-size: 13px; }}
    th {{ background: #21262d; color: #8b949e; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="date-badge">📅 {day['display_date']} ({day['date']})</div>
    <h1>Day Dossier Summary</h1>
    <p style="font-size: 15px; color: #e6edf3;">{day['day_summary']}</p>

    <div class="section-title">🖼️ Photos Captured / Uploaded Today</div>
    <div style="margin-top: 12px;">
      {photos_html}
    </div>

    <div class="section-title">📁 Parsed Files & Exact Creation Dates</div>
    <table>
      <thead>
        <tr>
          <th>File Name</th>
          <th>File Type</th>
          <th>File Size</th>
          <th>Creation Date & Time</th>
        </tr>
      </thead>
      <tbody>
        {files_html}
      </tbody>
    </table>

    <div class="section-title">⏱️ Key Events & Chronological Timestamp Log</div>
    <ul style="line-height: 1.8; font-size: 14px;">
      {events_html}
    </ul>

    <p style="margin-top: 24px;"><a href="../timeline_calendar_portal.html" style="color: #58a6ff;">← Back to Master Timeline Calendar Directory</a></p>
  </div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Created Timeline Calendar Day Page: {filename}")
