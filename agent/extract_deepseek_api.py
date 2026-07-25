"""
Chrome Cookie Decryptor for DeepSeek authentication.
Extracts the session token from the local Chrome installation to fetch the chat data.
"""
import os
import json
import base64
import sqlite3
import shutil
import urllib.request
import ssl
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

def get_chrome_key():
    local_state_path = os.path.join(os.environ['USERPROFILE'], 
                                    r'AppData\Local\Google\Chrome\User Data\Local State')
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.loads(f.read())
    
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])
    # Remove DPAPI signature prefix 'DPAPI'
    encrypted_key = encrypted_key[5:]
    decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return decrypted_key

def decrypt_cookie(ciphertext, key):
    try:
        # Check signature prefix
        if ciphertext[:3] == b'v10':
            nonce = ciphertext[3:15]
            payload = ciphertext[15:-16]
            tag = ciphertext[-16:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            decrypted = cipher.decrypt_and_verify(payload, tag)
            return decrypted.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Decryption failed: {e}"
    return ""

def get_deepseek_cookie():
    key = get_chrome_key()
    if not key:
        print("Could not find Chrome encryption key.")
        return None

    # Path to cookies db - scan all profiles dynamically
    user_data = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data')
    cookie_paths = []
    if os.path.exists(user_data):
        for item in os.listdir(user_data):
            if item == 'Default' or item.startswith('Profile '):
                db_path = os.path.join(user_data, item, 'Network', 'Cookies')
                if os.path.exists(db_path):
                    cookie_paths.append(db_path)
    
    cookies = []
    for db_path in cookie_paths:
        if not os.path.exists(db_path):
            continue
        print(f"Reading cookies from {db_path}...")
        # Copy to temp file to avoid locking
        temp_db = "temp_cookies.db"
        try:
            shutil.copyfile(db_path, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query cookies for deepseek
            cursor.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%deepseek%'")
            for host, name, value, enc_val in cursor.fetchall():
                val = value
                if not val and enc_val:
                    val = decrypt_cookie(enc_val, key)
                cookies.append(f"{name}={val}")
            
            conn.close()
            os.remove(temp_db)
        except Exception as e:
            print(f"Error reading path {db_path}: {e}")
            if os.path.exists(temp_db):
                os.remove(temp_db)
                
    return "; ".join(cookies) if cookies else None

def fetch_chat_api(share_id, cookie):
    # Shared chat endpoint on DeepSeek
    # Shared URLs have format: https://chat.deepseek.com/a/chat/s/06e3c77c-3466-4e6c-817d-facd96370cf2
    # The actual API endpoint to fetch the share content is:
    # https://chat.deepseek.com/api/v0/chat/share/detail?share_id=06e3c77c-3466-4e6c-817d-facd96370cf2
    url = f"https://chat.deepseek.com/api/v0/chat/share/detail?share_id={share_id}"
    print(f"Fetching chat details from API for share_id: {share_id}...")
    
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": cookie,
        "Accept": "application/json"
    })
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"API fetch failed: {e}")
        return None

def format_chat(data):
    if not data or 'data' not in data:
        return "No data found."
    
    chat_data = data.get('data', {})
    title = chat_data.get('title', 'Untitled Chat')
    messages = chat_data.get('messages', [])
    
    out = []
    out.append(f"# DeepSeek Chat: {title}\n")
    
    for msg in messages:
        role = msg.get('role', '').upper()
        content = msg.get('content', '')
        out.append(f"{'='*80}\n{role}\n{'='*80}\n{content}\n\n")
        
    return "".join(out)

def main():
    cookie = get_deepseek_cookie()
    if not cookie:
        print("No DeepSeek cookies found in local Chrome profiles.")
        # Try unauthenticated request anyway
        cookie = ""
        
    shares = [
        "06e3c77c-3466-4e6c-817d-facd96370cf2",
        "41317237-4280-4707-8c82-0ac3f6d73c45"
    ]
    
    for i, share_id in enumerate(shares):
        data = fetch_chat_api(share_id, cookie)
        if data:
            formatted = format_chat(data)
            outfile = f"deepseek_session_{i+1}.txt"
            with open(outfile, "w", encoding="utf-8") as f:
                f.write(formatted)
            print(f"Successfully saved formatting to {outfile}")
        else:
            print(f"Could not retrieve details for {share_id}")

if __name__ == "__main__":
    main()
