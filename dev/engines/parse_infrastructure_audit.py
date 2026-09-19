import re
import json

def parse_audit(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Domain / IP
    domain_match = re.search(r'\*\*TARGET:\*\*\s*(.*?)\s*\(`(.*?)`\)', content)
    ip_match = re.search(r'\*\*Resolved IP:\*\*\s*`(.*?)`', content)
    domain = domain_match.group(2) if domain_match else "hbpd.org"
    entity = domain_match.group(1).strip() if domain_match else "Huntington Beach Police Department"
    ip = ip_match.group(1) if ip_match else "162.242.210.88"

    # Extract Table
    records = []
    table_pattern = re.compile(r'\|\s*(\d+(?:,\s*\d+)*)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|')
    
    for match in table_pattern.finditer(content):
        ports_str, service, status, risk = match.groups()
        # Handle multiple ports like "135, 139, 445"
        ports = [p.strip() for p in ports_str.split(',')]
        for port in ports:
            records.append({
                "entity": entity,
                "domain": domain,
                "ip": ip,
                "port": int(port),
                "service": service.strip(),
                "status": status.strip(),
                "risk": risk.strip()
            })
            
    return records

if __name__ == "__main__":
    records = parse_audit("HBPD_PORT_SCAN_REPORT.md")
    with open("infrastructure_audit_parsed.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Parsed {len(records)} port vulnerability records.")
