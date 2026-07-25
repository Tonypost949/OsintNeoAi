import requests
import pandas as pd
import io

def check_hud_data():
    url = "https://www.huduser.gov/portal/sites/default/files/xls/2007-2023-PIT-Counts-by-CoC.xlsx"
    print(f"Downloading {url}...")
    try:
        r = requests.get(url)
        if r.status_code == 200:
            df = pd.read_excel(io.BytesIO(r.content), sheet_name='2023')
            ca_df = df[df['CoC Number'].str.startswith('CA')]
            print(f"Found {len(ca_df)} CA CoCs in the HUD file.")
            print(ca_df[['CoC Number', 'CoC Name', 'Overall Homeless, 2023']].head())
        else:
            print("Failed, trying .xlsb or another URL... status:", r.status_code)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    check_hud_data()
