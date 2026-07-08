import os

entities = [
    ("PER-1", "maltego.Person", "Kristy Conway (HBPD Outreach)"),
    ("PER-2", "maltego.Person", "Thomas Conway (Mercy House Board)"),
    ("PER-3", "maltego.Person", "Joe Conway (Mercy House Donor)"),
    ("PER-4", "maltego.Person", "Vickie Conway (Mercy House Donor)"),
    ("ORG-1", "maltego.Organization", "Mercy House Living Centers"),
    ("ORG-2", "maltego.Organization", "HBNC 17642 Beach Blvd HB"),
    ("ORG-3", "maltego.Organization", "OC HMIS CA-602"),
    ("ORG-4", "maltego.Organization", "HUD CA-602 CoC 34.6M FY2024"),
    ("PER-5", "maltego.Person", "Erin DeRycke (HMIS Admin OC United Way)"),
    ("ORG-5", "maltego.Organization", "OCHCA Case 20IC002"),
    ("PER-6", "maltego.Person", "Christine Lane (OCHCA)"),
    ("PER-7", "maltego.Person", "Anabel Garcia (OCHCA AOABH Fraud)"),
    ("PER-8", "maltego.Person", "Bridgette Little (Victim)"),
    ("ORG-6", "maltego.Organization", "City of Huntington Beach"),
    ("ORG-7", "maltego.Organization", "OC Metal Processing OCMP Fullerton"),
    ("PER-9", "maltego.Person", "Andrew Do (OC Supervisor CONVICTED 5yr)"),
    ("PER-10", "maltego.Person", "Peter Pham (VAS Founder FUGITIVE)"),
    ("ORG-8", "maltego.Organization", "Viet America Society VAS 10M+ theft"),
    ("PER-11", "maltego.Person", "Rhiannon Do (Co-conspirator)"),
    ("PER-12", "maltego.Person", "Thanh Nguyen (Hand-to-Hand Relief)"),
    ("EML-1", "maltego.EmailAddress", "hotline@hudoig.gov BLOCKED May2026"),
    ("EML-2", "maltego.EmailAddress", "whistleblower@hudoig.gov BLOCKED May2026"),
    ("PER-13", "maltego.Person", "Anthony DiMarcello III (Relator Series3)"),
    ("PER-14", "maltego.Person", "Dr Ann Verma MD (Co-Relator)"),
    ("PER-15", "maltego.Person", "Jesse Knabb (Plaintiff 8-26-cv-00348)"),
    ("DOC-1", "maltego.Document", "Petition A-2926 State Water Board Nov2025")
]

edges = [
    ("PER-1", "ORG-2", "REFERS_TO Dec2021"),
    ("PER-2", "ORG-1", "BOARD_MEMBER + DONOR"),
    ("PER-3", "ORG-1", "DONOR Golf Tournament 2019"),
    ("PER-4", "ORG-1", "DONOR Golf Tournament 2019"),
    ("PER-1", "PER-2", "POSSIBLE FAMILY LINK unconfirmed PRIORITY"),
    ("ORG-1", "ORG-2", "OPERATES OC contract 5401898"),
    ("ORG-1", "ORG-4", "RECEIVES 11.5M+ FY2024 CoC"),
    ("ORG-2", "ORG-3", "FEEDS INTAKE DATA"),
    ("ORG-3", "ORG-4", "CERTIFIES SPMs justify renewals"),
    ("PER-5", "ORG-3", "ADMINISTERS single data control point"),
    ("PER-6", "ORG-5", "SIGNED fraudulent Case Closed"),
    ("ORG-5", "ORG-2", "ISSUED ultra vires cert 20IC002 Aug2020"),
    ("ORG-6", "ORG-4", "USED false cert unlocked 6.1M LMIHAF"),
    ("PER-7", "PER-8", "HARVESTED CREDENTIALS AOABH forms"),
    ("ORG-5", "ORG-7", "PATTERN OF LENIENCY EN0000977"),
    ("PER-9", "ORG-8", "DIRECTED 10M+ sole-source contracts"),
    ("PER-10", "ORG-8", "FOUNDED 15 federal counts"),
    ("PER-11", "ORG-8", "CO-CONSPIRATOR"),
    ("PER-12", "ORG-8", "HAND-TO-HAND logistics"),
    ("ORG-8", "ORG-3", "ENABLED BY falsified crisis metrics"),
    ("PER-13", "EML-1", "BLOCKED x2 May2026 obstruction"),
    ("PER-13", "EML-2", "BLOCKED x2 May2026 obstruction"),
    ("PER-13", "ORG-6", "RELATOR FCA qui tam"),
    ("PER-14", "ORG-6", "CO-RELATOR FCA"),
    ("PER-15", "ORG-6", "PLAINTIFF 8-26-cv-00348 RCRA"),
    ("PER-15", "DOC-1", "FILED Nov15 2025"),
    ("PER-13", "PER-1", "FIRST REFERRED BY Dec27 2021 ORIGIN")
]

xml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<MaltegoGraph version="1.0">',
    '  <Entities>'
]

for eid, etype, value in entities:
    xml_lines.append(f'    <Entity type="{etype}" id="{eid}">')
    xml_lines.append(f'      <Value>{value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</Value>')
    xml_lines.append(f'      <Notes></Notes>')
    xml_lines.append(f'    </Entity>')

xml_lines.append('  </Entities>')
xml_lines.append('  <Relationships>')

for src, dst, label in edges:
    # Use maltego.link.manual-link to be safer, or just use the label as type.
    # The native exporter in retro_osint_gui.py uses the label directly as type
    label_safe = label.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', '&quot;')
    xml_lines.append(f'    <Relationship type="maltego.link.manual-link" source="{src}" target="{dst}">')
    xml_lines.append(f'      <Evidence>{label_safe}</Evidence>')
    xml_lines.append(f'    </Relationship>')

xml_lines.append('  </Relationships>')
xml_lines.append('</MaltegoGraph>')

os.makedirs(r'c:\Users\HP\Downloads\retroOsint4\Retro_OSINT_v3.0\exports', exist_ok=True)
with open(r'c:\Users\HP\Downloads\retroOsint4\Retro_OSINT_v3.0\exports\OC_RICO_Investigation.mtgl', 'w', encoding='utf-8') as f:
    f.write("\n".join(xml_lines))

print("Generated OC_RICO_Investigation.mtgl")
