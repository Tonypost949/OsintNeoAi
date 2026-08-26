import json, pathlib, hashlib, datetime
from pathlib import Path

kb_v1 = Path(r"C:\OsintNeoAi\knowledge_base\post_bookmarks_knowledge_v1.json")
kb_v2 = Path(r"C:\OsintNeoAi\knowledge_base\post_bookmarks_knowledge_v2.json")
az_v1 = Path(r"C:\OsintNeoAi\knowledge_base\post_library_az_knowledge_v1.json")
az_v2 = Path(r"C:\OsintNeoAi\knowledge_base\post_library_az_knowledge_v2.json")
rag_v1 = Path(r"C:\OsintNeoAi\knowledge_base\post_bookmarks_knowledge_rag_chunks_v1.jsonl")
rag_v2 = Path(r"C:\OsintNeoAi\knowledge_base\post_bookmarks_knowledge_rag_chunks_v2.jsonl")
instr_v1 = Path(r"C:\OsintNeoAi\knowledge_base\repo_ai_instruction_addendum_v1.md")
instr_v2 = Path(r"C:\OsintNeoAi\knowledge_base\repo_ai_instruction_addendum_v2.md")

data = json.loads(kb_v1.read_text(encoding="utf-8"))

new_link = {
    "title": "Nexis+ AI Search Chat - LexisNexis AI",
    "url": "https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9",
    "domain": "nexis.lexisnexis.com",
    "folder_hierarchy": "Post University Library / Nexis+AI (added 2026-08-25)",
    "folders": ["Post University Library", "Nexis+AI"],
    "category": "Post University Library",
    "add_date": str(int(datetime.datetime.now().timestamp())),
    "icon": "",
    "purpose": "LexisNexis Nexis+ AI conversational search - natural language legal, news, and company research via Post SSO. Use when user wants AI to draft, summarize, or chat over Nexis content.",
    "when_to_use": "AI-assisted queries: 'summarize caselaw on Cal. Pub. Util. Code § 851', 'find news on Ascon', 'draft memo from Nexis results'. Auth via Post proxy https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/...",
    "auth_note": "Requires Post SSO - access via Blackboard Traurig Library -> Nexis Uni -> AI Search, or proxy: https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9",
    "added_v2": True
}

# dedup check
if new_link["url"] not in [l["url"] for l in data["all_links"]]:
    data["all_links"].append(new_link)
    data["total_unique_links"] = len(data["all_links"])
    data["total_raw_links"] += 1
    # update categories
    from collections import Counter
    cat_counts = Counter(l["category"] for l in data["all_links"])
    data["categories"] = dict(cat_counts)
    # update top domains
    dom_counts = Counter(l["domain"] for l in data["all_links"])
    data["top_domains"] = dict(dom_counts.most_common(20))
    data["post_university_core"] = [l for l in data["all_links"] if l["category"]=="Post University Library"]
    data["ingested_at_v2"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["v2_note"] = "Added nexis.lexisnexis.com/aisearch/chat AI endpoint per user request 2026-08-25"

kb_v2.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {kb_v2} with {len(data['all_links'])} links")

# AZ v2
az = json.loads(az_v1.read_text(encoding="utf-8"))
az["featured"].append({
    "name": "Nexis+ AI Search Chat (LexisNexis AI)",
    "url": "https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9",
    "direct_url": "https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9",
    "vendor": "LexisNexis",
    "purpose": "Conversational AI over Nexis legal/news/company content - draft memos, summarize, natural language queries",
    "when_to_use": "When user wants AI to do the research, not just search. Use alongside classic Nexis Uni (advance.lexis.com) for AI-synthesized answers."
})
az["key_bookmark_links"].append("https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9")
az["updated_v2"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
az_v2.write_text(json.dumps(az, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {az_v2}")

# RAG v2 - copy v1 + append new chunks
rag_text = rag_v1.read_text(encoding="utf-8")
new_chunks = []
new_chunks.append(json.dumps({
    "id": hashlib.md5(new_link["url"].encode()).hexdigest()[:12],
    "text": f"Title: {new_link['title']}\nURL: {new_link['url']}\nCategory: {new_link['category']}\nPurpose: {new_link['purpose']}\nWhen to use: {new_link['when_to_use']}\nAuth: {new_link['auth_note']}",
    "metadata": new_link,
    "source": "POST82526favorites_8_25_26.html + user added 2026-08-25"
}, ensure_ascii=False))
# also add proxied version
new_chunks.append(json.dumps({
    "id": hashlib.md5((new_link["url"]+"_proxy").encode()).hexdigest()[:12],
    "text": f"Post Library Featured DB: Nexis+ AI Search Chat - Conversational AI over Nexis. Use proxied URL: https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9 for off-campus. Direct: {new_link['url']}",
    "metadata": {"name": "Nexis+ AI Search Chat", "url": new_link["url"]},
    "source": "https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9"
}, ensure_ascii=False))

rag_v2.write_text(rag_text.rstrip() + "\n" + "\n".join(new_chunks) + "\n", encoding="utf-8")
print(f"Wrote {rag_v2} with {len(rag_text.splitlines())+len(new_chunks)} chunks")

# Instruction v2
instr = instr_v1.read_text(encoding="utf-8")
addition = f"""
## V2 Update 2026-08-25 — Added Nexis+ AI Search

**New endpoint added per user request:**
- `https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9` (and proxied: `https://postu.idm.oclc.org/login?auth=prodbb&url=https://nexis.lexisnexis.com/aisearch/chat/819adcf0-2b9a-4c84-8501-3b789be09ca9`)
- **Title:** Nexis+ AI Search Chat
- **When AI should USE it:** Whenever user wants AI-assisted research (natural language, summarization, drafting) over Nexis content. Classic `advance.lexis.com` = keyword/Boolean search; `nexis.lexisnexis.com/aisearch` = conversational AI. Prefer AI chat for: "summarize", "draft memo", "what does caselaw say about X", "analyze news coverage". Prefer classic for precise Boolean docket pulls.
- **Auth:** Always via Post SSO proxy for off-campus. Direct link requires campus IP or Blackboard session.
- **Files updated:** `post_bookmarks_knowledge_v2.json`, `post_library_az_knowledge_v2.json`, `post_bookmarks_knowledge_rag_chunks_v2.jsonl` (+2 chunks)
- **Total now:** {len(data['all_links'])} unique URLs (was 815)
"""
instr_v2.write_text(instr.rstrip() + "\n" + addition + "\n", encoding="utf-8")
print(f"Wrote {instr_v2}")

# Also update agent copy
Path(r"C:\OsintNeoAi\agent\POST_BOOKMARKS_LEARNED_v2.md").write_text(Path(instr_v2).read_text(encoding="utf-8"), encoding="utf-8")
print("Wrote agent/POST_BOOKMARKS_LEARNED_v2.md")
