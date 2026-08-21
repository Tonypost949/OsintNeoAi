#!/usr/bin/env python3
import json
import sys
import os

def run_fb_scraper(post_id, c_user=None, xs=None):
    try:
        from facebook_scraper import get_posts
    except ImportError:
        print("Installing facebook-scraper engine...")
        os.system("pip install facebook-scraper")
        from facebook_scraper import get_posts

    cookies = {}
    if c_user and xs:
        cookies = {'c_user': c_user, 'xs': xs}
    
    print(f"Scraping Facebook Post ID: {post_id} with cookies...")
    
    comments_found = []
    try:
        for post in get_posts(post_urls=[f"https://www.facebook.com/{post_id}"], cookies=cookies, options={"comments": True}):
            print(f"Post Text: {post.get('post_text', '')[:100]}...")
            comments = post.get("comments_full", []) or post.get("comments", [])
            print(f"Found {len(comments)} comments.")
            comments_found.extend(comments)
            
        output_path = "/data/data/com.termux/files/home/osintneoai/fb_scraped_comments.json"
        with open(output_path, "w") as f:
            json.dump(comments_found, f, indent=2, default=str)
        print(f"SUCCESS: Saved comments to {output_path}")
    except Exception as e:
        print("Scraper Error:", e)

if __name__ == "__main__":
    post_id = sys.argv[1] if len(sys.argv) > 1 else "pfbid02wxnMqxe5iy7w3zRVF2tqFL5PHx9uDNWdFK467LPrrvqVFCF3Bnc72o3AB4GX7gAdl"
    c_user = os.environ.get("FB_C_USER")
    xs = os.environ.get("FB_XS")
    run_fb_scraper(post_id, c_user, xs)
