from google.cloud import bigquery
import pandas as pd

def check_cocs():
    client = bigquery.Client(project='noble-beanbag-497411-m4')
    query = """
    SELECT * FROM `noble-beanbag-497411-m4.forensic_layers.cps_trafficking_layer`
    LIMIT 1
    """
    try:
        df = client.query(query).to_dataframe()
        print("Columns in cps_trafficking_layer:", df.columns.tolist())
    except Exception as e:
        print(e)

if __name__ == '__main__':
    check_cocs()
