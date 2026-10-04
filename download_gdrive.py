import requests
import sys
import os

def download_file_from_google_drive(id, destination):
    print(f"Downloading {id} to {destination}...")
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)
    print(f"Finished downloading {id}. Size: {os.path.getsize(destination)} bytes.")

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

if __name__ == "__main__":
    download_file_from_google_drive('1AmQLbItaSDPL9qxUqK9LYddOLBX8Qw9E', 'C:\\EVIDENCE_LOCKER_MASTER\\01_ESA\\1AmQLbItaSDPL9qxUqK9LYddOLBX8Qw9E.pdf')
    download_file_from_google_drive('1H9a7_cIOpsTz5wtDQusx90Qf9TGlKXWX', 'C:\\EVIDENCE_LOCKER_MASTER\\01_ESA\\1H9a7_cIOpsTz5wtDQusx90Qf9TGlKXWX.pdf')
