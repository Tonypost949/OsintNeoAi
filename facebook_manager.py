#!/usr/bin/env python3
"""
Facebook Account Control & Automation Script for Termux & Kali Linux
Supports:
1. Fetching account posts and comments
2. Publishing automated status updates / case dossier releases
3. Querying profile statistics
"""

import os
import sys
import json
import urllib.request
import urllib.parse

class FacebookController:
    def __init__(self, access_token=None):
        self.access_token = access_token or os.environ.get("FB_ACCESS_TOKEN", "")
        self.api_base = "https://graph.facebook.com/v20.0"

    def is_authenticated(self):
        return bool(self.access_token and self.access_token != "YOUR_FB_TOKEN")

    def get_profile(self):
        """Fetch authenticated user profile details"""
        if not self.is_authenticated():
            print("Error: Missing Facebook Access Token.")
            return None
        
        url = f"{self.api_base}/me?fields=id,name,email&access_token={self.access_token}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Termux-Kali-FBControl/1.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                print(f"Authenticated as: {data.get('name')} (ID: {data.get('id')})")
                return data
        except Exception as e:
            print(f"Profile Query Error: {e}")
            return None

    def post_update(self, message_text):
        """Publish a new post to your Facebook feed"""
        if not self.is_authenticated():
            print("Error: Access Token required to publish posts.")
            return False

        url = f"{self.api_base}/me/feed"
        payload = urllib.parse.urlencode({
            "message": message_text,
            "access_token": self.access_token
        }).encode("utf-8")

        try:
            req = urllib.request.Request(url, data=payload, headers={"User-Agent": "Termux-Kali-FBControl/1.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                print(f"SUCCESS: Post published live to Facebook! Post ID: {data.get('id')}")
                return data
        except Exception as e:
            print(f"Publishing Error: {e}")
            return None

    def get_recent_posts(self):
        """Fetch recent posts and comments"""
        if not self.is_authenticated():
            print("Error: Access Token required to fetch posts.")
            return None

        url = f"{self.api_base}/me/posts?fields=id,message,created_time,comments&access_token={self.access_token}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Termux-Kali-FBControl/1.0"})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                output_file = "/data/data/com.termux/files/home/osintneoai/fb_user_posts.json"
                with open(output_file, "w") as f:
                    json.dump(data, f, indent=2)
                print(f"SUCCESS: Retrieved {len(data.get('data', []))} posts and saved to {output_file}")
                return data
        except Exception as e:
            print(f"Fetch Error: {e}")
            return None

if __name__ == "__main__":
    print("=== Facebook Control Engine (Termux & Kali Linux) ===")
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("FB_ACCESS_TOKEN")
    
    fb = FacebookController(token)
    
    if len(sys.argv) > 2 and sys.argv[2] == "post":
        msg = sys.argv[3] if len(sys.argv) > 3 else "Automated update from Termux OSINT Suite."
        fb.post_update(msg)
    else:
        print("\nUsage Modes:")
        print("1. Query Profile & Posts: python3 facebook_manager.py <FB_TOKEN>")
        print("2. Publish Status Update: python3 facebook_manager.py <FB_TOKEN> post 'Your message here'")
