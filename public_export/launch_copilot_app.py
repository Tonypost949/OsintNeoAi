import os
import sys
import tkinter as tk
from tkinter import ttk
import webbrowser

CLOUDS = [
    {
        "name": "OsintNeoAi Sentinel Agent",
        "url": "https://copilotstudio.microsoft.com/environments/d5b42781-da97-e29a-a5bc-d88f977ebd01/bots/e6781ec6-79e6-4868-90be-60e88d51435b/canvas"
    },
    {
        "name": "OsintNeoAi Master Agent",
        "url": "https://copilotstudio.microsoft.com/environments/d5b42781-da97-e29a-a5bc-d88f977ebd01/bots/3bda9cdd-4646-47bf-8e7a-4d02547f01bf/canvas"
    },
    {
        "name": "Truth & Fact Audit Agent",
        "url": "https://copilotstudio.microsoft.com/environments/d5b42781-da97-e29a-a5bc-d88f977ebd01/bots/af9caeaa-991a-4dbc-9a48-ad2ebb8d60f2/canvas"
    },
    {
        "name": "HUD Housing Verifier Agent",
        "url": "https://copilotstudio.microsoft.com/environments/d5b42781-da97-e29a-a5bc-d88f977ebd01/bots/7450e379-710b-404f-923d-9ac7150384e9/canvas"
    },
    {
        "name": "Osint Neo AI Bot (Personal)",
        "url": "https://copilotstudio.microsoft.com/environments/584c706d-38a2-e52e-b6e3-24a809f10508/bots/fc647254-a398-f111-b8db-00224803c960/canvas"
    },
    {
        "name": "Master Bookmarks & Evidence Hub",
        "url": "file:///C:/OsintNeoAi/Master_Bookmarks_Hub.html"
    }
]

def open_url(url):
    webbrowser.open(url)

root = tk.Tk()
root.title("OsintNeoAi Enterprise Copilot Agent Launcher")
root.geometry("600x450")
root.configure(bg="#0a0e17")

style = ttk.Style()
style.theme_use("clam")

title_label = tk.Label(
    root,
    text="🤖 OsintNeoAi Master Agent Hub",
    font=("Segoe UI", 16, "bold"),
    fg="#00d2ff",
    bg="#0a0e17",
    pady=15
)
title_label.pack()

subtitle_label = tk.Label(
    root,
    text="Bypass Microsoft Store Restrictions - 1-Click Direct Canvas Access",
    font=("Segoe UI", 10),
    fg="#9ca3af",
    bg="#0a0e17",
    pady=5
)
subtitle_label.pack()

btn_frame = tk.Frame(root, bg="#0a0e17", padx=20, pady=15)
btn_frame.pack(fill="both", expand=True)

for item in CLOUDS:
    btn = tk.Button(
        btn_frame,
        text=f"🚀 Launch {item['name']}",
        font=("Segoe UI", 11, "bold"),
        fg="#ffffff",
        bg="#1a233a",
        activebackground="#0078d4",
        activeforeground="#ffffff",
        bd=1,
        relief="solid",
        pady=8,
        command=lambda u=item["url"]: open_url(u)
    )
    btn.pack(fill="x", pady=5)

root.mainloop()
