import subprocess, json, os, sys
from google.cloud import bigquery
from google.oauth2.credentials import Credentials

gcloud = os.path.expanduser(r'~\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd')
token = subprocess.check_output([gcloud, 'auth', 'print-access-token', '--account=txtdjdrop@gmail.com'], shell=True).decode().strip()
creds = Credentials(token=token)
client = bigquery.Client(project='noble-beanbag-497411-m4', credentials=creds)
ds = client.get_dataset('noble-beanbag-497411-m4.national_audits')
ds.default_table_expiration_ms = 30 * 24 * 3600 * 1000
ds = client.update_dataset(ds, ['default_table_expiration_ms'])
print('Dataset expiration set:', ds.default_table_expiration_ms)
