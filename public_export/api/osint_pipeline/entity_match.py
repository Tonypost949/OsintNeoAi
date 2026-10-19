"""
entity_match.py — Fuzzy entity matching with 5-minute cache.
Matches entities across CA SOS, PPP data, and BigQuery.
"""
import hashlib
import json
import time
from pathlib import Path
try:
    from rapidfuzz import fuzz, process
except ImportError:
    import difflib
    class _FuzzFallback:
        @staticmethod
        def token_sort_ratio(s1: str, s2: str) -> float:
            t1 = " ".join(sorted(s1.split()))
            t2 = " ".join(sorted(s2.split()))
            return difflib.SequenceMatcher(None, t1, t2).ratio() * 100.0
            
    class _ProcessFallback:
        @staticmethod
        def extractOne(query: str, choices: list[str], scorer=None, score_cutoff: float = 0.0):
            best_choice = None
            best_score = -1.0
            if scorer is None:
                scorer = _FuzzFallback.token_sort_ratio
            for c in choices:
                score = scorer(query, c)
                if score >= score_cutoff and score > best_score:
                    best_score = score
                    best_choice = c
            if best_choice is not None:
                return (best_choice, best_score, 0)
            return None

    fuzz = _FuzzFallback()
    process = _ProcessFallback()

import config

# ── In-memory cache (dict + timestamps) ────────────────────────
_cache: dict[str, tuple[float, dict]] = {}


def _cache_key(name: str, entity_type: str = "") -> str:
    normalized = name.upper().strip()
    return hashlib.md5(f"{normalized}:{entity_type}".encode()).hexdigest()


def _is_cached(key: str) -> Optional[dict]:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < config.CACHE_TTL_SECONDS:
            return data
        del _cache[key]
    return None


def _store_cache(key: str, data: dict):
    _cache[key] = (time.time(), data)


def normalize_name(name: str) -> str:
    """Normalize entity name for matching."""
    import re
    name = name.upper().strip()
    # Remove common suffixes
    for suffix in [" LLC", " INC", " CORP", " CORPORATION", " LP", " LTD", " COMPANY", " CO"]:
        name = name.replace(suffix, "")
    # Remove punctuation
    name = re.sub(r"[-.,&/()]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    # Remove trailing commas
    name = name.rstrip(",").strip()
    return name


def match_entity(
    name: str,
    candidates: list[dict],
    entity_type: str = "",
    threshold: int = None,
) -> Optional[dict]:
    """
    Fuzzy match an entity name against a list of candidates.
    candidates: list of dicts with 'entity_name' and 'entity_id' keys.
    Returns best match above threshold, or None.
    """
    if threshold is None:
        threshold = config.FUZZY_THRESHOLD

    key = _cache_key(name, entity_type)
    cached = _is_cached(key)
    if cached:
        return cached

    normalized = normalize_name(name)
    candidate_names = {normalize_name(c["entity_name"]): c for c in candidates}

    if not candidate_names:
        return None

    best_match = process.extractOne(
        normalized,
        list(candidate_names.keys()),
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold,
    )

    if best_match:
        match_name, score, _ = best_match
        result = candidate_names[match_name]
        result["match_score"] = score
        result["match_type"] = "fuzzy"
        _store_cache(key, result)
        return result

    return None


def match_exact(name: str, candidates: list[dict]) -> Optional[dict]:
    """Exact match after normalization."""
    key = _cache_key(name)
    cached = _is_cached(key)
    if cached:
        return cached

    normalized = normalize_name(name)
    for c in candidates:
        if normalize_name(c["entity_name"]) == normalized:
            result = dict(c)
            result["match_score"] = 100.0
            result["match_type"] = "exact"
            _store_cache(key, result)
            return result
    return None


def clear_cache():
    """Clear all cache entries."""
    _cache.clear()


def get_cache_stats() -> dict:
    return {
        "size": len(_cache),
        "ttl_seconds": config.CACHE_TTL_SECONDS,
        "threshold": config.FUZZY_THRESHOLD,
    }
