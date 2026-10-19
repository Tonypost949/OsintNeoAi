import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(len(lines)):
    if lines[i].startswith('          conn = get_db()'):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          c = conn.cursor()'):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          c.execute('):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          repos = '):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          conn.close()'):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          repo_text = '):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('          if repos:'):
        lines[i] = lines[i].replace('          ', '        ')
    elif lines[i].startswith('              repo_text = '):
        lines[i] = lines[i].replace('              ', '            ')

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
