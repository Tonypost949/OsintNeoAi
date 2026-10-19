import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

repo_logic = '''
          conn = get_db()
          c = conn.cursor()
          c.execute("SELECT repo_url FROM user_repos WHERE user_id = ?", (request.user_id,))
          repos = [r['repo_url'] for r in c.fetchall()]
          conn.close()
          
          repo_text = ""
          if repos:
              repo_text = "\\n\\n[USER GITHUB REPOS]\\nThe user has linked the following GitHub repositories to their account:\\n" + "\\n".join(repos) + "\\n\\nYou can use these custom OSINT tools by writing a bash block that git clones them to /tmp and runs them. E.g., git clone [url] /tmp/repo && /tmp/repo/script.sh"
'''

# Standard replace
content = re.sub(r'(context = build_rag_context\(\))', repo_logic + '\\n          \\1', content)
content = re.sub(r'prompt = f"\{SYSTEM_PROMPT\.format\(project=GCP_PROJECT\)\}\\n\\nCurrent context:\\n\{context\}', 'prompt = f"{SYSTEM_PROMPT.format(project=GCP_PROJECT)}\\n\\nCurrent context:\\n{context}{repo_text}', content)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
