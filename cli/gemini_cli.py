#!/usr/bin/env python3
import sys
import os
import urllib.request
import json

def get_api_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

def query_gemini(prompt):
    api_key = get_api_key()
    if not api_key:
        print("[!] GEMINI_API_KEY environment variable not set. Please set GEMINI_API_KEY.")
        print("[!] Using fallback echo mode...")
        print(f"\n[Gemini AI Response to: '{prompt}']\n")
        print("Ready for queries. Set GEMINI_API_KEY to enable live API inference.")
        return

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            print("\n" + text + "\n")
    except Exception as e:
        print(f"[!] Error calling Gemini API: {e}")

def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        query_gemini(query)
    else:
        print("==================================================")
        print("⚡ GEMINI CLI INTERACTIVE TERMINAL")
        print("Type 'exit' or 'quit' to exit.")
        print("==================================================")
        while True:
            try:
                user_input = input("gemini> ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    break
                if user_input:
                    query_gemini(user_input)
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Gemini CLI.")
                break

if __name__ == "__main__":
    main()
