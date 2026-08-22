import re

with open('api/main_v2.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix python block 219-235
bad_block = '''        repo_text = ""
        if repos:
            repo_text = "

[USER GITHUB REPOS]
The user has linked the following GitHub repositories to their account:
" + "
".join(repos) + "

You can use these custom OSINT tools by writing a bash block that git clones them to /tmp and runs them. E.g., git clone [url] /tmp/repo && /tmp/repo/script.sh"

          context = build_rag_context()
        prompt = f"{SYSTEM_PROMPT.format(project=GCP_PROJECT)}

Current context:
{context}{repo_text}\\n\\nUser question: {message}\\n\\nReturn your answer. If you need to query BigQuery, include a SQL block with `sql ... ` that I can execute separately."'''

good_block = '''        repo_text = ""
        if repos:
            repo_text = "\\n\\n[USER GITHUB REPOS]\\nThe user has linked the following GitHub repositories to their account:\\n" + "\\n".join(repos) + "\\n\\nYou can use these custom OSINT tools by writing a bash block that git clones them to /tmp and runs them. E.g., git clone [url] /tmp/repo && /tmp/repo/script.sh"

        context = build_rag_context()
        prompt = f"{SYSTEM_PROMPT.format(project=GCP_PROJECT)}\\n\\nCurrent context:\\n{context}{repo_text}\\n\\nUser question: {message}\\n\\nReturn your answer. If you need to query BigQuery, include a SQL block with `sql ... ` that I can execute separately."'''

content = content.replace(bad_block, good_block)

with open('api/main_v2.py', 'w', encoding='utf-8') as f:
    f.write(content)
