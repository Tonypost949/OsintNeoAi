import re
import html

html_path = r"C:\Users\HP\.gemini\antigravity\brain\2dfef4c3-8925-4be4-a79e-c8d4755f7c55\.system_generated\steps\675\content.md"
output_path = r"C:\Users\HP\.gemini\antigravity\brain\2dfef4c3-8925-4be4-a79e-c8d4755f7c55\opencode_share_clean.md"

with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
    raw = f.read()

print("=== CLEANING HTML FROM OPENCODE SHARE ===")

# Locate the hydration data object in the script tag
# The hydration data starts with $R[7]={sessionID: ...}
data_match = re.search(r'\$R\[7\]\s*=\s*(\{[\s\S]+?\});', raw)
if not data_match:
    # Try backup search for sessionID
    data_match = re.search(r'sessionID\s*:\s*"ses_[^"]+"[\s\S]*', raw)

cleaned_text = ""

# Let's extract all the code blocks and text segments in the script
# E.g., strings inside $R assignments or standard text segments
text_segments = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', raw)
print(f"Extracted {len(text_segments)} raw text segments.")

code_blocks = []
for segment in text_segments:
    # Clean up double slashes, unicode escapes, newlines
    decoded = segment.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
    
    # Unescape unicode sequences (e.g. \u003c to <)
    try:
        decoded = decoded.encode('utf-8').decode('unicode_escape')
    except:
        pass
        
    if "bash" in decoded or "gcloud" in decoded or "PROJECT_ID=" in decoded or "rclone" in decoded or "import " in decoded:
        if len(decoded.strip()) > 30:
            code_blocks.append(decoded)

# Sort and filter unique code blocks to avoid duplicate assignments
unique_blocks = []
for block in code_blocks:
    if block not in unique_blocks:
        unique_blocks.append(block)

print(f"Located {len(unique_blocks)} unique code/migration blocks.")

cleaned_text += "# OpenCode Shared Session Migration Details\n\n"
cleaned_text += "Here are the extracted migration scripts and commands from the shared session:\n\n"

for i, block in enumerate(unique_blocks):
    cleaned_text += f"## Script Block {i+1}\n"
    if "python" in block.lower() or "import " in block.lower():
        lang = "python"
    elif "bash" in block.lower() or "mkdir" in block.lower() or "gcloud" in block.lower():
        lang = "bash"
    else:
        lang = "text"
        
    cleaned_text += f"```{lang}\n{block.strip()}\n```\n\n"

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(cleaned_text)

print(f"Successfully wrote cleaned markdown to {output_path}")
