import json

leads_path = r"C:\OsintNeoAi\data\leads_feed.json"
with open(leads_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
leads = data.get("leads", [])
print(f"Loaded {len(leads)} leads.")

ppp_leads = [L for L in leads if L.get('vector') == 'PPP_PROPERTY_OVERLAP']
shell_clusters = [L for L in leads if L.get('vector') == 'ADDRESS_SHELL_CLUSTER']
mutual_aid = [L for L in leads if L.get('vector') == 'MUTUAL_AID']

print(f"\n--- TOP PPP LEADS ({len(ppp_leads)}) ---")
for lead in ppp_leads[:5]:
    print(json.dumps(lead, indent=2))

print(f"\n--- TOP SHELL CLUSTERS ({len(shell_clusters)}) ---")
for cluster in shell_clusters[:5]:
    print(json.dumps(cluster, indent=2))
