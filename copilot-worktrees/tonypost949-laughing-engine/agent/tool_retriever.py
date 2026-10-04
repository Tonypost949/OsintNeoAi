import os
import re
import math

# Path to the agent directory
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_text(text):
    """Tokenizes and cleans text for TF-IDF calculations."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s_]', ' ', text)
    return [w for w in text.split() if len(w) > 2]

class SimpleTFIDF:
    """A lightweight, dependency-free TF-IDF and Cosine Similarity engine."""
    def __init__(self, corpus):
        # corpus is a dict of {doc_id: doc_text}
        self.doc_ids = list(corpus.keys())
        self.doc_terms = {doc_id: clean_text(text) for doc_id, text in corpus.items()}
        
        # Calculate Document Frequencies
        self.dfs = {}
        for terms in self.doc_terms.values():
            unique_terms = set(terms)
            for term in unique_terms:
                self.dfs[term] = self.dfs.get(term, 0) + 1
                
        self.num_docs = len(corpus)
        
        # Calculate IDFs
        self.idfs = {}
        for term, df in self.dfs.items():
            self.idfs[term] = math.log((1 + self.num_docs) / (1 + df)) + 1
            
        # Build Document Vectors
        self.doc_vectors = {}
        for doc_id, terms in self.doc_terms.items():
            tfs = {}
            for t in terms:
                tfs[t] = tfs.get(t, 0) + 1
            
            vec = {}
            for t, tf in tfs.items():
                vec[t] = tf * self.idfs.get(t, 0.0)
            
            # Normalize vector
            length = math.sqrt(sum(val ** 2 for val in vec.values()))
            if length > 0:
                vec = {t: val / length for t, val in vec.items()}
            self.doc_vectors[doc_id] = vec

    def similarity(self, query):
        """Calculates cosine similarity of query against all document vectors."""
        query_terms = clean_text(query)
        q_tfs = {}
        for t in query_terms:
            q_tfs[t] = q_tfs.get(t, 0) + 1
            
        q_vec = {}
        for t, tf in q_tfs.items():
            if t in self.idfs:
                q_vec[t] = tf * self.idfs[t]
                
        # Normalize query vector
        q_length = math.sqrt(sum(val ** 2 for val in q_vec.values()))
        if q_length == 0:
            return {doc_id: 0.0 for doc_id in self.doc_ids}
        q_vec = {t: val / q_length for t, val in q_vec.items()}
        
        scores = {}
        for doc_id, doc_vec in self.doc_vectors.items():
            dot_product = 0.0
            for t, val in q_vec.items():
                if t in doc_vec:
                    dot_product += val * doc_vec[t]
            scores[doc_id] = dot_product
        return scores

def scan_script_catalog():
    """Scans all Python scripts in the agent directory and extracts their docstrings/comments."""
    catalog = {}
    for filename in os.listdir(AGENT_DIR):
        if filename.endswith(".py") and filename != "tool_retriever.py":
            filepath = os.path.join(AGENT_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                # Try parsing the first docstring
                docstring_match = re.match(r'^\s*"""(.*?)"""', content, re.DOTALL)
                if docstring_match:
                    desc = docstring_match.group(1).strip()
                else:
                    # Or get the first few lines of comments
                    lines = content.split("\n")
                    comments = []
                    for line in lines[:15]:
                        if line.strip().startswith("#"):
                            comments.append(line.strip("# ").strip())
                    desc = " ".join(comments).strip()
                
                # Fallback to filename breakdown if no description found
                if not desc:
                    desc = filename.replace("_", " ").replace(".py", "")
                    
                catalog[filename] = f"Filename: {filename}. Description: {desc}"
            except Exception:
                catalog[filename] = f"Filename: {filename}."
    return catalog

class ToolSelector:
    """Implements the Retriever-with-Fallback logic for script selection."""
    def __init__(self, confidence_threshold=0.25):
        self.threshold = confidence_threshold
        self.catalog = scan_script_catalog()
        self.tfidf = SimpleTFIDF(self.catalog)

    def retrieve(self, query):
        scores = self.tfidf.similarity(query)
        sorted_matches = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_matches

    def retrieve_with_fallback(self, query, gemini_client=None):
        matches = self.retrieve(query)
        top_script, score = matches[0] if matches else (None, 0.0)

        # Tier 1: High Confidence Resolution
        if score >= self.threshold:
            return {
                "status": "resolved",
                "script": top_script,
                "confidence": score,
                "attempts": 1,
                "matches": matches[:3]
            }

        # Tier 2: Reformulation using Gemini LLM if available, otherwise simple normalization
        print(f"[*] Confidence low ({score:.3f}). Attempting reformulation...")
        reformulated = query
        if gemini_client:
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=(
                        f"The user query is: '{query}'\n"
                        f"We need to find a matching python file from our local script repository. "
                        f"Rewrite this query focusing strictly on core operational verbs, data targets, and technical keywords. "
                        f"Provide ONLY the rewritten query text, with no headers, explanations, or quotes."
                    )
                )
                reformulated = response.text.strip()
                print(f"[*] Reformulated query: '{reformulated}'")
            except Exception as e:
                print(f"[!] Gemini reformulation failed: {e}")
                # Simple fallback reformulation
                reformulated = query.replace("can you", "").replace("please", "").replace("?", "").strip()
        else:
            reformulated = query.replace("can you", "").replace("please", "").replace("?", "").strip()

        matches2 = self.retrieve(reformulated)
        top_script2, score2 = matches2[0] if matches2 else (None, 0.0)

        if score2 >= self.threshold:
            return {
                "status": "resolved",
                "script": top_script2,
                "confidence": score2,
                "attempts": 2,
                "matches": matches2[:3]
            }

        # Tier 3: Escalate to Clarification
        clarification_options = [f"{m[0]} (confidence: {m[1]:.2f})" for m in matches2[:3] if m[1] > 0.05]
        options_str = "\n- ".join(clarification_options) if clarification_options else "None detected"
        
        clarification_msg = (
            f"I'm not confident which analysis script matches your request '{query}'.\n"
            f"Here are the closest matches:\n- {options_str}\n\n"
            f"Could you please specify which script or data source you would like to analyze?"
        )
        
        return {
            "status": "escalated",
            "script": None,
            "confidence": max(score, score2),
            "attempts": 2,
            "clarification_request": clarification_msg
        }

if __name__ == "__main__":
    selector = ToolSelector()
    
    # Test queries
    test_queries = [
        "Let's sync all the local backups",
        "cross reference Mercy House address logs",
        "xyzzy non-existent command request"
    ]
    
    print("Testing Tool Selector Pipeline:")
    print("="*60)
    for q in test_queries:
        res = selector.retrieve_with_fallback(q)
        print(f"Query: '{q}'")
        print(f"  Status: {res['status']}")
        if res["status"] == "resolved":
            print(f"  Selected Script: {res['script']} (confidence: {res['confidence']:.3f})")
        else:
            print(f"  Clarification:\n{res['clarification_request']}")
        print("-"*60)
