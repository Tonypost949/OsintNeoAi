from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

tables = {
    'ppp_rico.ppp_150k_plus': None,
    'ppp_rico.ppp_up_to_150k': None,
    'ppp_rico.hb_llcs': None,
    'hb_church_osint.entities': None,
    'nppes_export.oc_lb_orgs': None,
}

for name in tables:
    t = client.get_table(name)
    print(f"\n=== {name} ({t.num_rows} rows) ===")
    for f in t.schema:
        print(f"  {f.name}: {f.field_type}")
