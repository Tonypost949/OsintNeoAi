import json
import os

def main():
    path = r"C:\Users\HP\Downloads\deepseek_data-2026-07-02\conversations.json"
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        data = json.load(f)
        
    convo = data[0]
    mapping = convo.get("mapping", {})
    for node_id, node in mapping.items():
        msg = node.get("message")
        if msg:
            print(f"\nNode: {node_id}")
            fragments = msg.get("fragments")
            for idx, frag in enumerate(fragments):
                print(f"Fragment {idx}: type={frag.get('type')} keys={list(frag.keys())}")
                if frag.get('type') == 'TEXT':
                    print(f"  Text content: {frag.get('text')[:300]}")
                elif frag.get('type') == 'FILE':
                    print(f"  Files: {frag.get('files')}")
            
            # Let's see how author/sender is determined
            # If there's an author key or a role/sender role in mapping node itself
            print(f"Node keys: {list(node.keys())}")
            break

if __name__ == "__main__":
    main()
