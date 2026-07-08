from google.cloud import bigquery
client = bigquery.Client(project='noble-beanbag-497411-m4')

# Find LLCs that own multiple HB properties with out-of-state mailing addresses
print("=== Multi-property LLCs with out-of-state mail addresses ===")
query = """
SELECT 
    p.owner_name,
    COUNT(DISTINCT p.apn) as property_count,
    ARRAY_AGG(STRUCT(p.address as address, p.apn as apn, p.last_sale_value as last_sale_value, p.mail_address as mail_address, p.mail_city as mail_city) ORDER BY p.last_sale_value DESC) as properties
FROM `noble-beanbag-497411-m4.hb_church_osint.properties` p
WHERE p.mail_city NOT IN ('HUNTINGTON BEACH', 'FOUNTAIN VALLEY', 'COSTA MESA', 'NEWPORT BEACH', 'WESTMINSTER', 'GARDEN GROVE', 'ANAHEIM', 'ORANGE', 'IRVINE', 'BREA', 'YORBA LINDA', 'LONG BEACH', 'LOS ANGELES', 'SAN DIEGO', 'SAN FRANCISCO', 'SANTA ANA', 'TUSTIN', 'MISSION VIEJO', 'LAKE FOREST', 'LAGUNA BEACH', 'DANA POINT', 'SEAL BEACH', 'CYPRESS', 'BUENA PARK', 'FULLERTON', 'HUNTINGTN BCH', 'HUNTINGTONBCH', 'CORONA DEL MAR', 'NEWPORT COAST', 'SUNSET BEACH', 'LOS ALAMITOS', 'PASADENA', 'SANTA FE SPRINGS', 'BEVERLY HILLS', 'DOWNEY', 'CERRITOS', 'WALNUT', 'PLACENTIA', 'CORONA', 'GLENDALE', 'LA MIRADA', 'LAGUNA NIGUEL', 'ALHAMBRA', 'SAN JOSE', 'STANTON', 'WILDOMAR', 'LAGUNA HILLS', 'BAKERSFIELD', 'TORRANCE', 'VILLA PARK', 'PALOS VERDES ESTATES', 'SURFSIDE', 'SAN CLEMENTE')
GROUP BY p.owner_name
HAVING COUNT(DISTINCT p.apn) >= 2
ORDER BY COUNT(DISTINCT p.apn) DESC, SUM(p.last_sale_value) DESC
LIMIT 50
"""
rows = client.query(query).result()
for row in rows:
    print(f"\n{row.owner_name} ({row.property_count} properties)")
    for prop in row.properties:
        print(f"  - {prop['address']} | APN {prop['apn']} | ${prop['last_sale_value']} | Mail: {prop['mail_address']}, {prop['mail_city']}")

# Find properties in clusters with churches by address similarity
print("\n=== Properties near church-matched addresses (MAIN ST, DELAWARE, etc.) ===")
query2 = """
SELECT owner_name, address, apn, mail_address, mail_city, last_sale_value
FROM `noble-beanbag-497411-m4.hb_church_osint.properties`
WHERE UPPER(address) LIKE '%MAIN ST%' 
   OR UPPER(address) LIKE '%DELAWARE ST%'
   OR UPPER(address) LIKE '%3RD ST%'
   OR UPPER(address) LIKE '%8TH ST%'
   OR UPPER(address) LIKE '%9TH ST%'
   OR UPPER(address) LIKE '%2ND ST%'
ORDER BY last_sale_value DESC
LIMIT 50
"""
rows2 = client.query(query2).result()
for row in rows2:
    print(f"{row.owner_name} | {row.address} | APN {row.apn} | {row.mail_address}, {row.mail_city} | ${row.last_sale_value}")
