import json
import os
from datetime import datetime

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
            {'time': '08:15:00-07:00', 'display_time': '08:15 AM PST', 'event': 'File Ingestion: Navigation_Center_Lease_Agreement_Final.pdf created.'},
            {'time': '10:12:44-07:00', 'display_time': '10:12 AM PST', 'event': 'Photo Capture: Site photo of 17631 Cameron Lane property entrance.'},
            {'time': '10:15:00-07:00', 'display_time': '10:15 AM PST', 'event': 'OCR Scan: Automated scan completed on 140 non-profit filings.'},
            {'time': '11:45:22-07:00', 'display_time': '11:45 AM PST', 'event': 'Soil Report Ingested: Hexavalent_Chromium_Soil_Report.xlsx added to database.'},
            {'time': '14:30:15-07:00', 'display_time': '02:30 PM PST', 'event': 'Photo Capture: Aerial drone capture of 17642 Beach Blvd asphalt cap layer.'},
            {'time': '14:45:00-07:00', 'display_time': '02:45 PM PST', 'event': 'Statutory Legal Match: Cal. Gov. Code § 1090 tagged on Oliver Chi records.'},
            {'time': '17:10:00-07:00', 'display_time': '05:10 PM PST', 'event': 'Ledger Sync: Autonomous transfer ledger emitted block #1849201 to TaxFunded.'}
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
            {'time': '09:00:00-07:00', 'display_time': '09:00 AM PST', 'event': 'CPRA Dispatch: Sent public records request to City Clerk Robin Estanislau.'},
            {'time': '09:15:10-07:00', 'display_time': '09:15 AM PST', 'event': 'Photo Capture: City Hall Public Records Desk Document Receipt.'},
            {'time': '16:30:00-07:00', 'display_time': '04:30 PM PST', 'event': 'Compliance Logged: Initial response delay logged past statutory timeline.'}
        ]
    }
]

os.makedirs('timeline_calendar', exist_ok=True)

for day in timeline_days:
    filename = f"timeline_calendar/{day['date']}.html"

    # Build master chronological sequence uniting photos, files, and events
    combined_timeline = []

    for p in day['photos']:
        combined_timeline.append({
            'sort_time': p['creation_date'],
            'type': 'PHOTO CAPTURE',
            'badge_class': 'badge-photo',
            'html': f"<strong>📷 Photo Captured:</strong> {p['filename']} — <em>{p['caption']}</em>"
        })

    for f in day['parsed_files']:
        combined_timeline.append({
            'sort_time': f['creation_date'],
            'type': 'FILE CREATED',
            'badge_class': 'badge-file',
            'html': f"<strong>📄 File Creation:</strong> {f['name']} ({f['type']}, {f['size']})"
        })

    for ev in day['key_events']:
        combined_timeline.append({
            'sort_time': f"{day['date']}T{ev['time']}",
            'type': 'AUDIT EVENT',
            'badge_class': 'badge-event',
            'html': f"<strong>⚡ Event:</strong> {ev['event']}"
        })

    # Sort strictly by timestamp string
    combined_timeline.sort(key=lambda x: x['sort_time'])

    seq_rows = "".join([f"""
    <tr>
      <td style="font-family: monospace; color: #58a6ff; font-weight: bold;">{item['sort_time']}</td>
      <td><span class="{item['badge_class']}">{item['type']}</span></td>
      <td>{item['html']}</td>
    </tr>
    """ for item in combined_timeline])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Strict Chronological Dossier: {day['display_date']}</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 24px; }}
    .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 24px; max-width: 1050px; margin: auto; }}
    h1 {{ color: #58a6ff; margin-top: 0; }}
    .date-badge {{ background: #1e3a8a; color: #93c5fd; padding: 6px 14px; border-radius: 20px; font-weight: bold; display: inline-block; margin-bottom: 16px; }}
    .section-title {{ border-bottom: 1px solid #30363d; padding-bottom: 6px; color: #f0f6fc; margin-top: 24px; font-size: 16px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 12px; }}
    th, td {{ border: 1px solid #30363d; padding: 10px; text-align: left; font-size: 13px; }}
    th {{ background: #21262d; color: #8b949e; }}
    .badge-photo {{ background: #7c2d12; color: #fdba74; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; }}
    .badge-file {{ background: #1e3a8a; color: #93c5fd; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; }}
    .badge-event {{ background: #064e3b; color: #6ee7b7; padding: 2px 8px; border-radius: 12px; font-weight: bold; font-size: 11px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="date-badge">📅 {day['display_date']} ({day['date']})</div>
    <h1>Strict Chronological Timeline & Evidence Sequence</h1>
    <p style="font-size: 14px; color: #8b949e;">Every photo capture, file creation date, and audit event is forcibly sorted into strict chronological order.</p>

    <div class="section-title">⏱️ Forced Timestamp Sequence (Photos + Files + Events)</div>
    <table>
      <thead>
        <tr>
          <th>ISO Timestamp</th>
          <th>Evidence Category</th>
          <th>Chronological Evidence Details</th>
        </tr>
      </thead>
      <tbody>
        {seq_rows}
      </tbody>
    </table>

    <p style="margin-top: 24px;"><a href="../timeline_calendar_portal.html" style="color: #58a6ff;">← Back to Master Timeline Directory</a></p>
  </div>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Generated Strict Timestamp Sequence Day Dossier: {filename}")
