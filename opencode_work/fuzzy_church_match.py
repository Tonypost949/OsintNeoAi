import csv
import re
from difflib import SequenceMatcher
from collections import defaultdict

def normalize_address(addr):
    if not addr:
        return ""
    addr = addr.upper()
    addr = re.sub(r'\b(STREET|ST\b|AVE|AVENUE|BLVD|BOULEVARD|DR|DRIVE|LN|LANE|CIR|CIRCLE|CT|COURT|PL|PLACE|WAY|PKWY|PKY)\b', '', addr)
    addr = re.sub(r'[^A-Z0-9]', ' ', addr)
    addr = re.sub(r'\s+', ' ', addr).strip()
    return addr

def token_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Load properties
props = []
with open(r"C:\Users\HP\OneDrive\Documents\opencode_work\hb_church_osint_properties.csv", 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        row['_norm'] = normalize_address(row['address'])
        row['_tokens'] = set(row['_norm'].split())
        props.append(row)

# Load entities (churches/nonprofits)
entities = []
with open(r"C:\Users\HP\OneDrive\Documents\opencode_work\hb_church_osint_entities.csv", 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['type'].strip().lower() in ('church', 'nonprofit'):
            row['_norm'] = normalize_address(row['address'])
            row['_tokens'] = set(row['_norm'].split())
            entities.append(row)

print(f"Loaded {len(props)} properties and {len(entities)} church/nonprofit entities")

# Match by address similarity
matches = []
for e in entities:
    if not e['_norm'] or len(e['_tokens']) < 2:
        continue
    best = None
    best_score = 0
    for p in props:
        if not p['_norm'] or len(p['_tokens']) < 2:
            continue
        # Street number must match exactly
        e_num = re.match(r'(\d+)', e['address'])
        p_num = re.match(r'(\d+)', p['address'])
        if not e_num or not p_num:
            continue
        if e_num.group(1) != p_num.group(1):
            continue
        score = token_similarity(e['_norm'], p['_norm'])
        if score > best_score and score >= 0.6:
            best_score = score
            best = p
    if best:
        matches.append({
            'entity_name': e['name'],
            'entity_type': e['type'],
            'entity_address': e['address'],
            'entity_city': e['city'],
            'entity_state': e['state'],
            'entity_ein': e['ein'],
            'property_owner': best['owner_name'],
            'property_address': best['address'],
            'property_apn': best['apn'],
            'property_last_sale_value': best['last_sale_value'],
            'property_last_sale_date': best['last_sale_date'],
            'property_mail_address': best['mail_address'],
            'property_mail_city': best['mail_city'],
            'match_score': round(best_score, 3)
        })

# Deduplicate by property APN + entity name
seen = set()
unique = []
for m in matches:
    key = (m['property_apn'], m['entity_name'])
    if key not in seen:
        seen.add(key)
        unique.append(m)

unique.sort(key=lambda x: (float(x['property_last_sale_value'] or 0), x['match_score']), reverse=True)

out_path = r"C:\Users\HP\OneDrive\Documents\opencode_work\church_property_fuzzy_network.csv"
with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=unique[0].keys())
    writer.writeheader()
    writer.writerows(unique)

print(f"Saved {out_path} with {len(unique)} fuzzy matches")

# Summary by property owner
owner_counts = defaultdict(int)
for m in unique:
    owner_counts[m['property_owner']] += 1

print("\nTop multi-church property owners:")
for owner, cnt in sorted(owner_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {owner}: {cnt} church/nonprofit matches")
