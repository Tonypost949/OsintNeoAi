#!/usr/bin/env python3
import os
import sys
import requests

TOKEN = os.environ.get("FB_TOKEN", "")

if len(sys.argv) > 1:
    TOKEN = sys.argv[1]

if not TOKEN or TOKEN == "YOUR_FACEBOOK_ACCESS_TOKEN":
    print("Error: Missing Facebook Access Token.")
    print("Usage: python3 fb_check.py <YOUR_FACEBOOK_ACCESS_TOKEN>")
    sys.exit(1)

print("Querying Facebook Graph API for recent posts and comments...")
url = f"https://graph.facebook.com/v19.0/me/posts?fields=message,comments&access_token={TOKEN}"

try:
    response = requests.get(url)
    data = response.json()
    print("Graph API Response:")
    print(data)
    
    with open("fb_posts_comments.json", "w") as f:
        import json
        json.dump(data, f, indent=2)
    print("\nSaved output to fb_posts_comments.json")
except Exception as e:
    print(f"Error fetching data from Facebook Graph API: {e}")
