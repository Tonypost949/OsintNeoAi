import pandas as pd

def parse_hud_data():
    try:
        df = pd.read_excel('2023_PIT.xlsb', engine='pyxlsb')
        print(df.head())
    except Exception as e:
        print("Failed with pyxlsb:", e)
        try:
            df = pd.read_excel('2023_PIT.xlsb', engine='openpyxl')
            print(df.head())
        except Exception as e2:
            print("Failed with openpyxl:", e2)

if __name__ == '__main__':
    parse_hud_data()
