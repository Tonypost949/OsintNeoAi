import json
import os
import glob

def dynamic_rag_search(query):
    query_words = [w.lower() for w in query.split() if len(w) > 2]
    matched_nodes = []
    matched_docs = []

    # 1. Search GraphDB
    graph_p = os.path.join("cli", "data", "graph.json")
    if os.path.exists(graph_p):
        try:
            with open(graph_p, "r", encoding="utf-8") as f:
                g = json.load(f)
                for n in g.get("nodes", []):
                    val = str(n.get("value", "")).lower()
                    ntype = n.get("type", "ENTITY")
                    if any(qw in val for qw in query_words):
                        matched_nodes.append({"value": n.get("value"), "type": ntype, "id": n.get("id")})
        except Exception as e:
            print("Graph search error:", e)

    # 2. Search Legal Library & Docs
    doc_paths = glob.glob("legal_library/*.md") + glob.glob("docs/*.md")
    for dp in doc_paths:
        try:
            with open(dp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                if any(qw in content.lower() for qw in query_words):
                    matched_docs.append({
                        "filename": os.path.basename(dp),
                        "path": dp,
                        "title": os.path.basename(dp).replace(".md", "").replace("_", " ").title()
                    })
        except Exception as e:
            pass

    return {
        "matched_nodes_count": len(matched_nodes),
        "matched_nodes": matched_nodes[:15],
        "matched_docs_count": len(matched_docs),
        "matched_docs": matched_docs[:10]
    }

if __name__ == "__main__":
    res = dynamic_rag_search("Woodbridge Irvine Company Eviction Plume")
    print(json.dumps(res, indent=2))
