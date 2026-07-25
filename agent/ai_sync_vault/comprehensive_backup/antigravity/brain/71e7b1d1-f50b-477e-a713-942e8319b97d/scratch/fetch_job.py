import urllib.request
import ssl

def main():
    url = "https://app.emergentagent.com/jobs/3235f8fc-69a8-4a73-b598-97d53e4b5a87"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    try:
        # Create unverified SSL context just in case
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            content = response.read()
            print(f"Success! Response code: {response.status}")
            print(f"Content length: {len(content)} bytes")
            
            # Save first 5000 chars as test
            with open("job_fetch_test.txt", "w", encoding="utf-8") as f:
                f.write(content.decode("utf-8", errors="ignore"))
            print("Saved content to job_fetch_test.txt")
            
    except Exception as e:
        print(f"Error fetching URL: {e}")

if __name__ == "__main__":
    main()
