from google.cloud import bigquery

client = bigquery.Client(project="project-743aab84-f9a5-4ec7-954")

# Search for the parent folders of the 7969270 files and get their names
query = """
WITH file_parents AS (
  SELECT DISTINCT file_name, file_id, parent_id
  FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`,
  UNNEST(parent_folder_ids) AS parent_id
  WHERE REGEXP_CONTAINS(file_name, r'^7969270')
)
SELECT DISTINCT p.file_name AS parent_folder_name, p.file_id AS parent_folder_id, p.web_view_link AS folder_link
FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index` p
JOIN file_parents fp ON p.file_id = fp.parent_id
WHERE p.mime_type = 'application/vnd.google-apps.folder'
"""

try:
    df = client.query(query).to_dataframe()
    if df.empty:
        print("[!] No parent folder names resolved. Listing raw parent IDs instead:")
        query2 = """
        SELECT DISTINCT file_name, parent_folder_ids
        FROM `project-743aab84-f9a5-4ec7-954.national_audits_legacy.drive_file_index`
        WHERE REGEXP_CONTAINS(file_name, r'^7969270')
        LIMIT 5
        """
        df2 = client.query(query2).to_dataframe()
        print(df2.to_string(index=False))
    else:
        print("[+] Parent folders resolved:")
        print(df.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")
