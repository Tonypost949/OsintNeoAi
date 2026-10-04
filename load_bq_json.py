from google.cloud import bigquery
from datetime import datetime

bq = bigquery.Client(project='noble-beanbag-497411-m4')
table_id = 'noble-beanbag-497411-m4.ai_sandbox.permit_ocr_results'

records = [
    {
        'file_path': r'C:\EVIDENCE_LOCKER_MASTER\20_ANALYSIS\db66e1e0-b949-11f1-8e00-dbd4e67e7847.pdf',
        'filename': 'HBNC_Precise_Grading_Plan_Set_StormTech_MC3500.pdf',
        'page_count': 8,
        'extracted_text': 'StormTech MC-3500 Chamber System: 10 chambers, 77" W x 45" H x 86" L each. Total chamber linear footage: ~71.7 ft. Chamber storage: 109.9 ft3 each. Min installed storage: 178.9 ft3 each. Top manifold: 12" ADS N-12 HDPE. Isolator row: 24" diameter. Stone embedment: AASHTO M43 No. 57, 95% Proctor. Earthwork: Raw Cut 1,560 CY, Raw Fill 475 CY, Net Export 1,085 CY (HAZWOPER). Hexavalent Chromium 980 ug/kg (49x EPA). Lead 101 mg/kg. Toxaphene 1,600 ug/kg. Building Permit #TBD - NEVER ISSUED. PW# 20-020 / L# 20-128 Final. WDID 8 30W004769 waiver abused. OCHCA #20IC002 fraudulent.',
        'key_value_count': 47,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    },
    {
        'file_path': r'C:\OsintNeoAi\evidence\stormtech_legal_permit_index.json',
        'filename': 'stormtech_legal_permit_index.json',
        'page_count': 1,
        'extracted_text': '226 StormTech permits indexed. HBNC permits: ZERO. Costa Mesa Skate Park (20260632178) and Ontario-Montclair DeAnza (20240481959) only municipal StormTech. HB permits: 1 (Springdale Water Main, 2012) - NOT StormTech. OC permits: 8 corrosion/cathodic. Cr-VI permits: 7 - none for HBNC.',
        'key_value_count': 226,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    },
    {
        'file_path': r'C:\Users\Amd949609\Downloads\Cameron Lane Navigation Center- Contract and Permit Record Review.pdf',
        'filename': 'Cameron_Lane_Navigation_Center_Permit_Review.pdf',
        'page_count': 5,
        'extracted_text': 'Accela PWG2020-020 Final grading 17631 Cameron. PW# 20-020 / L# 20-128 Precise Grading Plan Sheet 3 of 8. B2020004554, B2020-005184 MEP permits. Resolution 2019-22, TTS Engineering contract. Escalation: $670K -> $2.41M (3.6x). Unverified: PWE2020-304, PWE2022-0046 encroachment. Building Permit TBD. StormTech design/as-builts not produced.',
        'key_value_count': 15,
        'ocr_timestamp': datetime.utcnow().isoformat() + 'Z'
    }
]

job = bq.load_table_from_json(records, table_id)
job.result()
print(f'Loaded {job.output_rows} rows')