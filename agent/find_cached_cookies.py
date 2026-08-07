"""
Scans all unlocked Chrome profiles to find any cached DeepSeek cookies.
"""
import os
import json
import base64
import sqlite3
import shutil
from win32crypt import CryptUnprotectData
from Crypto.Cipher import AES

def get_chrome_key():
    local_state_path = os.path.join(os.environ['USERPROFILE'], 
                                    r'AppData\Local\Google\Chrome\User Data\Local State')
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = json.loads(f.read())
    encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
    return CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_cookie(ciphertext, key):
    try:
        if ciphertext[:3] == b'v10':
            nonce = ciphertext[3:15]
            payload = ciphertext[15:-16]
            tag = ciphertext[-16:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(payload, tag).decode('utf-8', errors='replace')
    except Exception as e:
        return ""
    return ""

def main():
    key = get_chrome_key()
    if not key:
        print("No Chrome key found.")
        return
        
    user_data = os.path.join(os.environ['USERPROFILE'], r'AppData\Local\Google\Chrome\User Data')
    if not os.path.exists(user_data):
        print("Chrome User Data path does not exist.")
        return
        
    for item in os.listdir(user_data):
        if item == 'Default' or item.startswith('Profile '):
            db_path = os.path.join(user_data, item, 'Network', 'Cookies')
            if not os.path.exists(db_path):
                continue
                
            temp_db = f"temp_cookies_{item}.db"
            try:
                # Attempt copy
                shutil.copyfile(db_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT host_key, name, value, encrypted_value FROM cookies WHERE host_key LIKE '%deepseek%'")
                rows = cursor.fetchall()
                if rows:
                    print(f"\n[FOUND] Profile: {item} - {len(rows)} deepseek cookies")
                    cookies = []
                    for host, name, value, enc_val in rows:
                        val = value if value else decrypt_cookie(enc_val, key)
                        print(f"  {host} | {name} = {val[:15]}...")
                        cookies.append(f"{name}={val}")
                    
                    # Try to save to file
                    with open(f"cookies_{item}.txt", "w") as f:
                        f.write("; ".join(cookies))
                conn.close()
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() or "permission" in str(e).lower():
                    print(f"Profile {item} is locked (currently active).")
                else:
                    print(f"Error reading sqlite for {item}: {e}")
            except Exception as e:
                print(f"Failed to copy {item}: {e}")
            finally:
                if os.path.exists(temp_db):
                    try:
                        os.remove(temp_db)
                    except:
                        pass

if __name__ == "__main__":
    main()
