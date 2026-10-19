import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix get_bq to gracefully handle missing credentials
get_bq_new = '''def get_bq():
    from google.cloud import bigquery
    from google.auth.exceptions import DefaultCredentialsError
    try:
        return bigquery.Client(project=GCP_PROJECT)
    except DefaultCredentialsError:
        class MockClient:
            def query(self, *args, **kwargs):
                class MockJob:
                    def result(self):
                        return [{"_error": "BigQuery credentials not configured. Please set GOOGLE_APPLICATION_CREDENTIALS in your deployment."}]
                return MockJob()
            def list_datasets(self):
                return []
        return MockClient()'''

content = re.sub(r'def get_bq\(\):\n    from google.cloud import bigquery\n    return bigquery.Client\(project=GCP_PROJECT\)', get_bq_new, content)

# Fix build_catalog to not throw 500 if client is mocked
catalog_find = '''        client = get_bq()
        catalog = {}'''
catalog_replace = '''        client = get_bq()
        catalog = {}
        if hasattr(client, 'list_datasets') and len(client.list_datasets()) == 0:
            return {"_error": "BigQuery credentials not configured or no datasets found."}'''

content = content.replace(catalog_find, catalog_replace)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
