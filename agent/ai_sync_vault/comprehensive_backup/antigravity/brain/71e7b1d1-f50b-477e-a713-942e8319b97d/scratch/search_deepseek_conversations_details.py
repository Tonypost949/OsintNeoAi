import os
import json
import sys

filepath = r"C:\Users\HP\.gemini\antigravity\brain\71e7b1d1-f50b-477e-a713-942e8319b97d\scratch\deepseek_data_1\conversations.json"

if os.path.exists(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            conv = data[0]
            mapping = conv.get("mapping", {})
            for nid, node in list(mapping.items()):
                msg = node.get("message")
                if msg and msg.get("fragments"):
                    print("Node", nid)
                    print("fragments type:", type(msg.get("fragments")))
                    print("fragments value:", str(msg.get("fragments"))[:500])
                    break
    except Exception as e:
         print(e)
