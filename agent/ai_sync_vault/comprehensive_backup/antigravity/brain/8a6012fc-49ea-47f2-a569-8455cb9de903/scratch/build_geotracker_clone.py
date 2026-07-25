import os
import shutil
import glob

# Destination folder
dest_dir = r"C:\Users\HP\OneDrive\Documents\opencode_work\Official_GeoTracker_T10000018579"
os.makedirs(dest_dir, exist_ok=True)

# Sources list mapping
sources = [
    r"C:\Users\HP\OneDrive - Post University,inc\files\*T10000018579*",
    r"C:\Users\HP\OneDrive\Downloads (1)\*T10000018579*",
    r"C:\Users\HP\Downloads\Adobe Downloads\*T10000018579*",
    r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\*T10000018579*",
    r"C:\Users\HP\OneDrive\Imports\txtdjdrop@gmail.com - Google Drive\bids hb\*T10000018579*"
]

# Find and copy matching files to the folder
copied_files = {}
for pattern in sources:
    for filepath in glob.glob(pattern):
        if os.path.isfile(filepath):
            filename = os.path.basename(filepath)
            dest_path = os.path.join(dest_dir, filename)
            if filename not in copied_files:
                try:
                    shutil.copy2(filepath, dest_path)
                    copied_files[filename] = filename
                    print(f"[+] Staged: {filename}")
                except Exception as e:
                    print(f"[ERROR] Failed to copy {filename}: {e}")

# Build the custom GeoTracker clone HTML interface page
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeoTracker Site Documents - T10000018579</title>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border-radius: 4px;
        }}
        .header {{
            border-bottom: 2px solid #005a9c;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #005a9c;
            margin: 0 0 5px 0;
            font-size: 24px;
        }}
        .header h2 {{
            margin: 0;
            font-size: 16px;
            color: #666;
        }}
        .tab-title {{
            background: #005a9c;
            color: white;
            padding: 10px;
            font-weight: bold;
            font-size: 14px;
            margin-top: 20px;
            border-radius: 4px 4px 0 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            background: white;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #e6f2ff;
            color: #003366;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f9f9f9;
        }}
        .file-link {{
            color: #0066cc;
            text-decoration: none;
            font-weight: bold;
        }}
        .file-link:hover {{
            text-decoration: underline;
        }}
        .missing-file {{
            color: #999;
            font-style: italic;
        }}
        .btn {{
            background: #005a9c;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 11px;
            font-weight: bold;
        }}
        .btn:hover {{
            background: #003d6b;
        }}
        .meta-box {{
            background: #fdfdfd;
            border: 1px solid #e2e2e2;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 13px;
            border-left: 5px solid #005a9c;
        }}
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>BEACH BOULEVARD PROJECT (T10000018579)</h1>
        <h2>17642 BEACH BOULEVARD, HUNTINGTON BEACH, CA 92647</h2>
    </div>

    <div class="meta-box">
        <strong>Oversight Agency:</strong> ORANGE COUNTY (LEAD) - CASE #: 20IC002<br>
        <strong>Status:</strong> Completed - Case Closed as of 8/21/2020<br>
        <strong>Notice:</strong> Notify the lead cleanup oversight agency prior to planned residential development and/or change in land use.
    </div>

    <div class="tab-title">Site Documents (Staged & Locked offline)</div>
    <table>
        <thead>
            <tr>
                <th width="5%"><input type="checkbox" checked disabled></th>
                <th width="40%">DOCUMENT TITLE</th>
                <th width="20%">TYPE</th>
                <th width="15%">SUBMITTED BY</th>
                <th width="10%">DOCUMENT DATE</th>
                <th width="10%">SIZE</th>
            </tr>
        </thead>
        <tbody>
            <!-- Rows matching the official GeoTracker page -->
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200625.Site Assessment Report.pdf" target="_blank">HISTORIC FILES - SITE ASSESSMENT REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>LENA SHAW (REGULATOR)</td>
                <td>11/16/2025</td>
                <td>106,439 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200318.Phase I Environmental Site Assessment.pdf" target="_blank">HISTORIC FILES - PHASE I ENVIRONMENTAL SITE ASSESSMENT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>37,458 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200408.Analytical Report.pdf" target="_blank">HISTORIC FILES - ANALYTICAL REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>2,116 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200410.Analytical Report.pdf" target="_blank">HISTORIC FILES - ANALYTICAL REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>1,155 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200414.Analytical Report.pdf" target="_blank">HISTORIC FILES - ANALYTICAL REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>2,315 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200415.Analytical Report.pdf" target="_blank">HISTORIC FILES - ANALYTICAL REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>1,667 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.20200417.Analytical Report.pdf" target="_blank">HISTORIC FILES - ANALYTICAL REPORT</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>2,176 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><a class="file-link" href="T10000018579.BulkFile.pdf" target="_blank">HISTORIC FILES - BULKFILE</a></td>
                <td>HISTORIC FILES</td>
                <td>GENIECE HIGGINS (REGULATOR), TAMARA ESCOBEDO (REGULATOR)</td>
                <td>3/10/2025</td>
                <td>2,502 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">SITE SUMMARY AND RECOMMENDATIONS</span></td>
                <td>STAFF LETTER</td>
                <td>GENIECE HIGGINS (REGULATOR)</td>
                <td>8/21/2020</td>
                <td>363 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">SITE SUMMARY AND RECOMMENDATIONS</span></td>
                <td>STAFF LETTER</td>
                <td>GENIECE HIGGINS (REGULATOR)</td>
                <td>8/21/2020</td>
                <td>1,774 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">SITE ASSESSMENT REPORT - SITE ASSESSMENT REPORT</span></td>
                <td>SITE ASSESSMENT REPORT</td>
                <td>TAMARA ESCOBEDO (REGULATOR)</td>
                <td>8/11/2020</td>
                <td>4,215 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">UPDATED RAS FORM</span></td>
                <td>VOLUNTARY REMEDIAL ACTION AGREEMENT</td>
                <td>TAMARA ESCOBEDO (REGULATOR)</td>
                <td>7/20/2020</td>
                <td>1,171 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">SITE ASSESSMENT REPORT - SITE ASSESSMENT REPORT</span></td>
                <td>SITE ASSESSMENT REPORT</td>
                <td>TAMARA ESCOBEDO (REGULATOR)</td>
                <td>6/25/2020</td>
                <td>10,846 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">RAS LETTER</span></td>
                <td>STAFF LETTER</td>
                <td>GENIECE HIGGINS (REGULATOR)</td>
                <td>5/4/2020</td>
                <td>91 KB</td>
            </tr>
            <tr>
                <td><input type="checkbox" checked disabled></td>
                <td><span class="missing-file">REQUEST FOR REMEDIAL ACTION SUPERVISION</span></td>
                <td>CORRESPONDENCE</td>
                <td>GENIECE HIGGINS (REGULATOR)</td>
                <td>4/29/2020</td>
                <td>1,171 KB</td>
            </tr>
        </tbody>
    </table>
</div>

</body>
</html>
"""

# Save the index.html clone page in the folder
with open(os.path.join(dest_dir, "index.html"), "w") as f:
    f.write(html_content)

print(f"[SUCCESS] GeoTracker clone page created and files locked inside: {dest_dir}")
