#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse

def fetch_facebook_comments(post_id, access_token):
    url = f"https://graph.facebook.com/v20.0/{post_id}/comments?access_token={access_token}&fields=id,message,from,created_time"
    req = urllib.request.Request(url, headers={"User-Agent": "OSINTNeoAI/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception as e:
        print(f"Error querying Facebook Graph API: {e}")
        return None

if __name__ == "__main__":
    token = os.environ.get("FB_TOKEN")
    if len(sys.argv) > 1:
        token = sys.argv[1]
    
    post_id = os.environ.get("FB_POST_ID", "100037558611635_pfbid02wxnMqxe5iy7w3zRVF2tqFL5PHx9uDNWdFK467LPrrvqVFCF3Bnc72o3AB4GX7gAdl")
    
    if not token:
        print("Usage: export FB_TOKEN='EAA...' && python3 fb_graph_api.py")
        sys.exit(1)
        
    print(f"Querying Facebook Graph API for Post ID: {post_id}...")
    result = fetch_facebook_comments(post_id, token)
    if result:
        output_file = "/data/data/com.termux/files/home/osintneoai/fb_comments.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"SUCCESS: Saved Facebook Graph API response to {output_file}")
