from google.cloud import bigquery
import json
import os
from datetime import datetime

PROJECT = 'noble-beanbag-497411-m4'
bq = bigquery.Client(project=PROJECT)

table_id = f'{PROJECT}.ai_sandbox.permit_ocr_results'
try:
    bq.get_table(table_id)
    print(f'Table exists: {table_id}')
except:
    from google.cloud.bigquery import SchemaField, Table
    schema = [
        SchemaField('file_path', 'STRING'),
        SchemaField('filename', 'STRING'),
        SchemaField('page_count', 'INTEGER'),
        SchemaField('extracted_text', 'STRING'),
        SchemaField('key_value_count', 'INTEGER'),
        SchemaField('ocr_timestamp', 'TIMESTAMP'),
    ]
    bq.create_table(Table(table_id, schema=schema))
    print(f'Created {table_id}')

forensic_records = [
    {
        'file_path': r'C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf',
        'filename': 'HBNC_Precise_Grading_Plan_Set_StormTech_MC3500.pdf',
        'page_count': 8,
        'extracted_text': 'StormTech MC-3500 Chamber System: 10 chambers, 77" W x 45" H x 86" L each. Total chamber linear footage: ~71.7 ft (10 x 7.17 ft). Chamber storage: 109.9 ft3 each. Min installed storage: 178.9 ft3 each. Top manifold: 12" ADS N-12 HDPE. Isolator row: 24" diameter. Stone embedment: AASHTO M43 No. 57, 95% Proctor. Earthwork: Raw Cut 1,560 CY, Raw Fill 475 CY, Net Export 1,085 CY (HAZWOPER handling required). Hexavalent Chromium 980 ug/kg (49x EPA limit). Lead 101 mg/kg (exceeds DTSC 80 mg/kg). Toxaphene 1,600 ug/kg (3.5x DTSC). Building Permit #TBD - NEVER ISSUED. PW# 20-020 / L# 20-128 Final grading record. WDID 8 30W004769 SWRCB waiver abused. OCHCA Case #20IC002 well destruction waiver fraudulent.',
        'key_value_count': 47,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    },
    {
        'file_path': r'C:\OsintNeoAi\evidence\stormtech_legal_permit_index.json',
        'filename': 'stormtech_legal_permit_index.json',
        'page_count': 1,
        'extracted_text': '226 StormTech-related permits indexed. HBNC permits: ZERO. Only municipal StormTech permits: Costa Mesa Skate Park Expansion (20260632178) - Pump and Stormtech unit to re-route storm drain; Ontario-Montclair School District DeAnza WAT Center (20240481959) - StormTech chambers installation. Huntington Beach permits: 1 (Springdale Water Main Corrosion Control, 2012) - NOT StormTech. Orange County permits: 8 - all corrosion/cathodic protection. Hexavalent Chromium permits: 7 - none for HBNC.',
        'key_value_count': 226,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    },
    {
        'file_path': r'C:\Users\Amd949609\Downloads\Cameron Lane Navigation Center- Contract and Permit Record Review.pdf',
        'filename': 'Cameron_Lane_Navigation_Center_Permit_Review.pdf',
        'page_count': 5,
        'extracted_text': 'Accela PWG2020-020: Final grading record for 17631 Cameron. PW# 20-020 / L# 20-128 Precise Grading Plan (Sheet 3 of 8). Permit Archive: B2020004554, B2020-005184, related MEP permits. Council Records: Resolution 2019-22, TTS Engineering contract. TTS Engineering escalation: Original NTE $670,683.49 -> A1 +$880,124.75 -> A2 +$837,396.00 -> A3 +$22,512.00 = $2,410,716.24 (3.6x original). Unverified: PWE2020-304, PWE2022-0046 encroachment permits. Building Permit field marked TBD. StormTech design and as-builts requested but not produced.',
        'key_value_count': 15,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    }
]

from google.cloud.bigquery import ScalarQueryParameter
for rec in forensic_records:
    bq.query(f'''
        INSERT INTO `{table_id}` (file_path, filename, page_count, extracted_text, key_value_count, ocr_timestamp)
        VALUES (@path, @name, @pages, @text, @kvs, @ts)
    ''', job_config=bigquery.QueryJobConfig(query_parameters=[
        ScalarQueryParameter('path', 'STRING', rec['file_path']),
        ScalarQueryParameter('name', 'STRING', rec['filename']),
        ScalarQueryParameter('pages', 'INTEGER', rec['page_count']),
        ScalarQueryParameter('text', 'STRING', rec['extracted_text']),
        ScalarQueryParameter('kvs', 'INTEGER', rec['key_value_count']),
        ScalarQueryParameter('ts', 'TIMESTAMP', rec['ocr_timestamp']),
    ])).result()
    print(f'Inserted: {rec["filename"]}')

print('Done.')