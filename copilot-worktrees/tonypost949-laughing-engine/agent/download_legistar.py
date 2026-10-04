import requests
import os
import urllib.parse

def download_attachments(matter_file):
    print(f"Fetching data for Matter: {matter_file}")
    matter_res = requests.get(f"http://webapi.legistar.com/v1/huntingtonbeach/Matters?$filter=MatterFile eq '{matter_file}'")
    matter_data = matter_res.json()
    
    if not matter_data:
        print(f"Matter {matter_file} not found.")
        return
        
    for matter in matter_data:
        if matter['MatterFile'] == matter_file:
            matter_id = matter['MatterId']
            print(f"Found Matter ID: {matter_id}")
            
            attach_res = requests.get(f"http://webapi.legistar.com/v1/huntingtonbeach/Matters/{matter_id}/Attachments")
            attachments = attach_res.json()
            
            save_dir = r"C:\Users\HP\.gemini\antigravity-ide\brain\c370d570-1fbc-427b-a511-94af4ff83ad7"
            
            for att in attachments:
                name = att['MatterAttachmentName']
                link = att['MatterAttachmentHyperlink']
                print(f"Downloading: {name} from {link}")
                
                # Sanitize filename
                safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '.', '-', '_')]).rstrip()
                if not safe_name.lower().endswith('.pdf'):
                    safe_name += '.pdf'
                    
                file_path = os.path.join(save_dir, safe_name)
                
                try:
                    pdf_res = requests.get(link)
                    with open(file_path, 'wb') as f:
                        f.write(pdf_res.content)
                    print(f"Saved to {file_path}")
                except Exception as e:
                    print(f"Failed to download {name}: {e}")

download_attachments("20-1799")
