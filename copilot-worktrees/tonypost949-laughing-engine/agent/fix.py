with open(r'C:\migrate opencode\OSINTNEOAI\agent\fast_scan.py', 'r') as f:
    content = f.read()

old_str = "r.get('banner', '')[:60]))"
new_str = "r.get('banner', '')[:60])"
content = content.replace(old_str, new_str)

with open(r'C:\migrate opencode\OSINTNEOAI\agent\fast_scan.py', 'w') as f:
    f.write(content)

print('Fixed')
