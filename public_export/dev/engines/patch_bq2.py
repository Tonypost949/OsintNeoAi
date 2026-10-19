import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_bq to handle GOOGLE_CREDENTIALS_JSON
bq_logic = '''def get_bq():
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from google.auth.exceptions import DefaultCredentialsError
    import json
    import os
    
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    try:
        if creds_json:
            info = json.loads(creds_json)
            creds = service_account.Credentials.from_service_account_info(info)
            return bigquery.Client(project=GCP_PROJECT, credentials=creds)
        else:
            return bigquery.Client(project=GCP_PROJECT)
    except Exception as e:
        class MockClient:
            def query(self, *args, **kwargs):
                class MockJob:
                    def result(self):
                        return [{"_error": "BigQuery credentials not configured. Please set GOOGLE_CREDENTIALS_JSON in Railway variables."}]
                return MockJob()
            def list_datasets(self):
                return []
        return MockClient()'''

content = re.sub(r'def get_bq\(\).*?return MockClient\(\)', bq_logic, content, flags=re.DOTALL)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
