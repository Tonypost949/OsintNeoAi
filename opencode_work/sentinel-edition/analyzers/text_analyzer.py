"""
Text analysis tools for OSINT investigations.
Keyword extraction, sentiment, entity clustering, risk patterns.
"""

import re
from collections import Counter
from typing import Any


class TextAnalyzer:
    """Core text analysis for OSINT documents."""

    RISK_KEYWORDS = {
        "high": ["fraud", "embezzlement", "money laundering", "kickback", "bribery",
                  "shell company", "offshore", "concealment", "fake invoice",
                  "illegal", "criminal", "indictment", "conviction", "felony",
                  "racketeering", "rico", "conspiracy", "obstruction"],
        "medium": ["suspicious", "unusual", "anomaly", "discrepancy", "unexplained",
                    "inconsistent", "questionable", "irregular", "deviation",
                    "overdue", "delinquent", "default", "violation"],
        "low": ["review", "audit", "investigation", "compliance", "monitor",
                "assessment", "evaluation", "examination", "inquiry"],
    }

    PATTERN_INDICATORS = {
        "layering": ["transfer", "wire", "moved", "reallocated", "redirected"],
        "shell_indicators": ["registered agent", "virtual office", "mail forwarding",
                             "p.o. box", "ups store", "registered agent inc"],
        "temporal_anomaly": ["weekend", "holiday", "after hours", "midnight", "2am", "3am"],
        "geographic_mismatch": ["offshore", "foreign", "cayman", "bermuda", "panama",
                                "british virgin", "seychelles", "bahamas"],
    }

    def __init__(self):
        self.stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "dare", "ought",
            "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above", "below",
            "between", "out", "off", "over", "under", "again", "further", "then",
            "once", "here", "there", "when", "where", "why", "how", "all", "each",
            "every", "both", "few", "more", "most", "other", "some", "such", "no",
            "nor", "not", "only", "own", "same", "so", "than", "too", "very",
            "just", "because", "but", "and", "or", "if", "while", "about", "up",
            "it", "its", "this", "that", "these", "those", "i", "me", "my",
        }

    def extract_keywords(self, text: str, top_n: int = 20) -> list[tuple[str, int]]:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in self.stop_words]
        return Counter(filtered).most_common(top_n)

    def risk_assessment(self, text: str) -> dict:
        text_lower = text.lower()
        findings = {"high": [], "medium": [], "low": [], "pattern_matches": []}

        for level, keywords in self.RISK_KEYWORDS.items():
            for kw in keywords:
                count = text_lower.count(kw)
                if count > 0:
                    findings[level].append({"keyword": kw, "count": count})

        for pattern_name, indicators in self.PATTERN_INDICATORS.items():
            matches = [ind for ind in indicators if ind in text_lower]
            if matches:
                findings["pattern_matches"].append({"pattern": pattern_name, "indicators": matches})

        high_score = len(findings["high"]) * 10
        medium_score = len(findings["medium"]) * 5
        low_score = len(findings["low"]) * 1
        pattern_score = len(findings["pattern_matches"]) * 7
        total_score = high_score + medium_score + low_score + pattern_score

        return {
            "risk_score": min(total_score / 10, 10.0),
            "risk_level": "CRITICAL" if total_score > 50 else "HIGH" if total_score > 25 else "MEDIUM" if total_score > 10 else "LOW",
            "findings": findings,
            "total_indicators": total_score,
        }

    def extract_dates(self, text: str) -> list[dict]:
        patterns = [
            (r'\b(\d{4}-\d{2}-\d{2})\b', "ISO"),
            (r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b', "US"),
            (r'\b(\d{1,2}-\d{1,2}-\d{2,4})\b', "Dash"),
            (r'\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b', "Written"),
        ]
        dates = []
        for pattern, fmt in patterns:
            for match in re.finditer(pattern, text):
                dates.append({"date": match.group(1), "format": fmt, "position": match.start()})
        dates.sort(key=lambda x: x["position"])
        return dates

    def extract_financial_figures(self, text: str) -> list[dict]:
        patterns = [
            (r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|thousand|k|m|b))?', "currency"),
            (r'\b(?:USD|EUR|GBP|JPY)\s*[\d,]+(?:\.\d{2})?', "foreign_currency"),
            (r'\b[\d,]+(?:\.\d+)?\s*(?:percent|pct|%)', "percentage"),
            (r'\b\d{2}-\d{7}\b', "ein"),
        ]
        figures = []
        for pattern, ftype in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                figures.append({"value": match.group(), "type": ftype, "position": match.start()})
        return figures

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        if len(sentences) <= max_sentences:
            return ". ".join(sentences) + "."
        word_scores = {}
        for word in re.findall(r'\b\w+\b', text.lower()):
            if word not in self.stop_words:
                word_scores[word] = word_scores.get(word, 0) + 1
        scored = []
        for sent in sentences:
            score = sum(word_scores.get(w.lower(), 0) for w in re.findall(r'\b\w+\b', sent))
            scored.append((score, sent))
        scored.sort(reverse=True)
        top = sorted(scored[:max_sentences], key=lambda x: text.index(x[1]))
        return ". ".join(s for _, s in top) + "."

    def detect_language(self, text: str) -> dict:
        common_words = {
            "en": {"the", "and", "is", "in", "to", "of", "a", "that", "it", "for"},
            "es": {"el", "la", "de", "en", "y", "los", "las", "un", "una", "por"},
            "fr": {"le", "la", "de", "les", "et", "des", "un", "une", "en", "est"},
            "de": {"der", "die", "das", "und", "ist", "in", "den", "von", "zu", "ein"},
            "pt": {"o", "a", "de", "e", "em", "os", "as", "um", "uma", "para"},
        }
        words = set(re.findall(r'\b\w+\b', text.lower()))
        scores = {}
        for lang, vocab in common_words.items():
            scores[lang] = len(words & vocab)
        best = max(scores, key=scores.get)
        return {"language": best, "confidence": scores[best] / len(common_words[best]), "scores": scores}
