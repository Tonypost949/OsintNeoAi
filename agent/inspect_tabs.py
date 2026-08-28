"""
inspect_tabs.py — Inspects open tabs via Kimi WebBridge
"""
import requests
import json

DAEMON_URL = "http://127.0.0.1:10086/command"
SESSION_NAME = "inspect-session"

def main():
    r = requests.post(DAEMON_URL, json={"action": "list_tabs", "args": {}, "session": SESSION_NAME})
    print("List tabs:", r.json())

if __name__ == "__main__":
    main()
