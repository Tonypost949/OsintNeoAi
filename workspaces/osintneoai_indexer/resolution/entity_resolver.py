"""
OsintNeoAi Indexer: Entity Resolution & Graph Disambiguation Pipeline
Path: C:\\OsintNeoAi\\workspaces\\osintneoai_indexer\\resolution\\entity_resolver.py
Milestone: M3 (Entity Resolution & Vault Storage) — Feature 13

Implements the 4-Stage Entity Resolution Pipeline:
1. Normalization & End-Anchored Corporate Suffix Stripping
2. Phonetic & Deterministic Blocking (Russell Soundex + Double Metaphone + Token Keys)
3. Multi-Score Fuzzy & Contextual Matching (Jaro-Winkler + Token Overlap + Context Scoring)
4. Graph Deduplication & Disjoint-Set Union (DSU) Clustering

Also extracts entities, chronological timeline events, financial transactions, and relational edges
from Ingested / Extracted Records.
"""

from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

from normalizers.date_normalizer import extract_dates
from normalizers.entity_normalizer import (
    CORP_SUFFIX_RE,
    HONORIFIC_PREFIX_RE,
    double_metaphone,
    soundex,
)
from resolution.taxonomy import (
    CANONICAL_TARGETS,
    CanonicalEntity,
    EntityCategory,
    EntityMention,
    EventType,
    FinancialTransaction,
    PaymentMethod,
    Relationship,
    RelationshipType,
    TimelineEvent,
    calculate_confidence,
    get_category_prefix,
)

logger = logging.getLogger("osintneoai.resolution.entity_resolver")

STOP_WORDS: Set[str] = {
    "THE", "OF", "AND", "FOR", "IN", "AT", "TO", "A", "AN", "ON", "WITH",
    "BY", "FROM", "LLC", "INC", "CORP", "CO", "LTD", "LP", "LLP", "PLLC",
    "DEPT", "DEPARTMENT", "DIVISION", "AGENCY", "BUREAU", "OFFICE"
}


# ============================================================================
# 1. DISJOINT-SET UNION (DSU) DATA STRUCTURE
# ============================================================================

class DisjointSetUnion:
    """
    Disjoint-Set Union (Union-Find) with path compression and rank optimization.
    Maintains partition of entity mentions and aliases into connected canonical components.
    """

    def __init__(self, elements: Optional[Iterable[str]] = None) -> None:
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
        if elements:
            for elem in elements:
                self.add(elem)

    def add(self, x: str) -> None:
        """Adds a new element if not already present."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0

    def find(self, x: str) -> str:
        """Finds representative root with path compression."""
        if x not in self.parent:
            self.add(x)
            return x

        path = []
        curr = x
        while self.parent[curr] != curr:
            path.append(curr)
            curr = self.parent[curr]

        # Path compression
        for node in path:
            self.parent[node] = curr
        return curr

    def union(self, x: str, y: str) -> bool:
        """
        Merges sets containing x and y.
        Returns True if elements were in distinct sets, False otherwise.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False

        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
        return True

    def is_connected(self, x: str, y: str) -> bool:
        """Checks if x and y belong to the same cluster."""
        return self.find(x) == self.find(y)

    def get_clusters(self) -> Dict[str, Set[str]]:
        """Returns mapping from root canonical key to set of members."""
        clusters: Dict[str, Set[str]] = defaultdict(set)
        for elem in list(self.parent.keys()):
            root = self.find(elem)
            clusters[root].add(elem)
        return dict(clusters)

    def count_clusters(self) -> int:
        """Returns total number of disjoint sets."""
        return len(self.get_clusters())


# ============================================================================
# 2. STRING MATCHING & SIMILARITY ALGORITHMS
# ============================================================================

def jaro_winkler_similarity(s1: str, s2: str, p: float = 0.1, max_l: int = 4) -> float:
    """
    Computes Jaro-Winkler string similarity distance between two strings in [0.0, 1.0].
    """
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    # Count transpositions
    k = 0
    transpositions = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    t = transpositions / 2.0
    jaro = (matches / len1 + matches / len2 + (matches - t) / matches) / 3.0

    # Common prefix length up to max_l
    prefix_len = 0
    for i in range(min(len1, len2, max_l)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break

    jw = jaro + (prefix_len * p * (1.0 - jaro))
    return round(min(1.0, max(0.0, jw)), 6)


def levenshtein_ratio(s1: str, s2: str) -> float:
    """
    Computes normalized Levenshtein ratio in [0.0, 1.0].
    """
    if s1 == s2:
        return 1.0
    if not s1 or not s2:
        return 0.0

    len1, len2 = len(s1), len(s2)
    dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost
            )

    distance = dp[len1][len2]
    max_len = max(len1, len2)
    return round(1.0 - (distance / max_len), 6)


def token_overlap_score(s1: str, s2: str) -> float:
    """
    Computes token-level Jaccard and containment score.
    """
    toks1 = {t for t in s1.upper().split() if t not in STOP_WORDS and len(t) >= 2}
    toks2 = {t for t in s2.upper().split() if t not in STOP_WORDS and len(t) >= 2}

    if not toks1 or not toks2:
        return 0.0

    intersection = toks1 & toks2
    if not intersection:
        return 0.0

    # Jaccard
    jaccard = len(intersection) / len(toks1 | toks2)
    # Containment
    containment = len(intersection) / min(len(toks1), len(toks2))

    return max(jaccard, containment)


# ============================================================================
# 3. EXTRACTION REGEX PATTERNS & HEURISTICS
# ============================================================================

KNOWN_ENTITY_PATTERNS: List[Tuple[re.Pattern, EntityCategory, str]] = [
    # Individuals
    (re.compile(r"\b(?:(?:Mayor\s+)?Harry\s+(?:Singh\s+)?Sidhu|Mayor\s+Sidhu)\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Harry Sidhu"),
    (re.compile(r"\bTodd\s+(?:Stephen\s+)?Ament\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Todd Ament"),
    (re.compile(r"\bMelahat\s+Rafiei\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Melahat Rafiei"),
    (re.compile(r"\b(?:Jeff|Jeffrey)\s+Flint\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Jeffrey Flint"),
    (re.compile(r"\b(?:(?:Special\s+Agent|SA)\s+)?Brian\s+Adkins\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Brian Adkins"),
    (re.compile(r"\b(?:(?:Special\s+Agent|SA)\s+)?Bradley\s+H\.?\s+Zartman\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Bradley H. Zartman"),
    (re.compile(r"\b(?:(?:Judge|Hon\.?)\s+)?Carmen\s+Luege\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Carmen Luege"),
    (re.compile(r"\bRichard\s+(?:S\.?\s+)?Sontag(?:,\s*Esq\.?)?\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Richard S. Sontag"),
    (re.compile(r"\bAnthony\s+(?:C\.?\s+)?DiMarcello\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Anthony DiMarcello"),
    (re.compile(r"\bArden\s+Hoang\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Arden Hoang"),
    (re.compile(r"\bVichal\s+Nunen\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Vichal Nunen"),
    (re.compile(r"\bAustin\s+Drissen\b", re.IGNORECASE), EntityCategory.INDIVIDUAL, "Austin Drissen"),

    # Municipal Bodies
    (re.compile(r"\b(?:City\s+of\s+)?Anaheim(?:\s+City\s+Council)?\b", re.IGNORECASE), EntityCategory.MUNICIPAL_BODY, "City of Anaheim"),
    (re.compile(r"\bAnaheim\s+Chamber\s+of\s+Commerce\b", re.IGNORECASE), EntityCategory.MUNICIPAL_BODY, "Anaheim Chamber of Commerce"),
    (re.compile(r"\bVisit\s+Anaheim\b", re.IGNORECASE), EntityCategory.MUNICIPAL_BODY, "Visit Anaheim"),
    (re.compile(r"\bCity\s+of\s+Irvine\b", re.IGNORECASE), EntityCategory.MUNICIPAL_BODY, "City of Irvine"),
    (re.compile(r"\bOrange\s+County\s+Board\s+of\s+Supervisors\b", re.IGNORECASE), EntityCategory.MUNICIPAL_BODY, "Orange County Board of Supervisors"),

    # Financial Entities
    (re.compile(r"\bTA\s+Group(?:\s+LLC)?\b", re.IGNORECASE), EntityCategory.FINANCIAL_INSTITUTION, "TA Group LLC"),
    (re.compile(r"\bFPS\s+Strategies(?:\s+LLC)?\b", re.IGNORECASE), EntityCategory.FINANCIAL_INSTITUTION, "FPS Strategies LLC"),
    (re.compile(r"\bSRB\s+Management(?:\s+Escrow|\s+LLC)?\b", re.IGNORECASE), EntityCategory.FINANCIAL_INSTITUTION, "SRB Management Escrow"),
    (re.compile(r"\bProgressive\s+Solutions(?:\s+Consulting)?\b", re.IGNORECASE), EntityCategory.FINANCIAL_INSTITUTION, "Progressive Solutions Consulting"),

    # Property Entities
    (re.compile(r"\bWoodbridge\s+Meadows(?:\s+Apartments)?(?:\s+LLC)?\b", re.IGNORECASE), EntityCategory.PROPERTY_MANAGEMENT, "Woodbridge Meadows Apartments LLC"),
    (re.compile(r"\bMercy\s+House(?:\s+Living\s+Centers)?\b", re.IGNORECASE), EntityCategory.PROPERTY_MANAGEMENT, "Mercy House Living Centers"),
    (re.compile(r"\b1456\s+Cedar\s+Lane\b", re.IGNORECASE), EntityCategory.PROPERTY_MANAGEMENT, "1456 Cedar Lane"),
    (re.compile(r"\bAngel\s+Stadium(?:\s+150-Acre\s+Parcel|\s+Site)?\b", re.IGNORECASE), EntityCategory.PROPERTY_MANAGEMENT, "Angel Stadium 150-Acre Parcel"),

    # Legal Agencies
    (re.compile(r"\b(?:USDC\s+CDCA|Central\s+District\s+of\s+California)\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "USDC CDCA"),
    (re.compile(r"\b(?:USDC\s+D\.?N\.?J\.?|District\s+of\s+New\s+Jersey)\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "USDC D.N.J."),
    (re.compile(r"\b(?:Orange\s+County\s+Superior\s+Court|Central\s+Justice\s+Center|CJC)\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "California Superior Court (Orange County CJC)"),
    (re.compile(r"\b(?:Federal\s+Bureau\s+of\s+Investigation|FBI)\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "Federal Bureau of Investigation"),
    (re.compile(r"\b(?:California\s+HCD|Department\s+of\s+Housing\s+and\s+Community\s+Development)\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "California Department of Housing and Community Development"),
    (re.compile(r"\bHamilton\s+Township\s+Police(?:\s+Division)?\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "Hamilton Township Police Division"),
    (re.compile(r"\bEwing\s+Police(?:\s+Department)?\b", re.IGNORECASE), EntityCategory.LEGAL_AGENCY, "Ewing Police Department"),

    # Commercial Entities
    (re.compile(r"\bWallace,?\s+Richardson,?\s+Sontag\s*&\s*Le(?:\s+LLP)?\b", re.IGNORECASE), EntityCategory.COMMERCIAL_ENTITY, "Wallace, Richardson, Sontag & Le LLP"),
    (re.compile(r"\bJL\s+Group(?:\s+LLC)?|\bJL\s+Investigation\b", re.IGNORECASE), EntityCategory.COMMERCIAL_ENTITY, "JL Group LLC"),
    (re.compile(r"\bQuantum\s+Auto\s+Dismantler(?:s)?\b", re.IGNORECASE), EntityCategory.COMMERCIAL_ENTITY, "Quantum Auto Dismantler"),
    (re.compile(r"\bAlaska\s+Airlines\b", re.IGNORECASE), EntityCategory.COMMERCIAL_ENTITY, "Alaska Airlines"),
]


# ============================================================================
# 4. MASTER ENTITY RESOLVER
# ============================================================================

class EntityResolver:
    """
    Multi-stage entity resolver, clusterer, and timeline intelligence synthesizer.
    """

    def __init__(
        self,
        seed_targets: Optional[List[Dict[str, Any]]] = None,
        similarity_threshold: float = 0.88,
    ) -> None:
        self.similarity_threshold = similarity_threshold
        self.seed_targets = seed_targets if seed_targets is not None else CANONICAL_TARGETS
        self._canonical_lookup: Dict[str, CanonicalEntity] = {}
        self._alias_to_canonical_id: Dict[str, str] = {}
        self._initialize_seed_targets()

    def _initialize_seed_targets(self) -> None:
        """Initializes canonical target catalog from knowledge base."""
        for target in self.seed_targets:
            category = target["entity_category"]
            prefix = get_category_prefix(category)
            raw_hash = hashlib.sha256(target["canonical_name"].encode("utf-8")).hexdigest()[:8].upper()
            entity_id = f"{prefix}-{raw_hash}"

            canonical_ent = CanonicalEntity(
                entity_id=entity_id,
                canonical_name=target["canonical_name"],
                entity_category=category,
                role_or_title=target.get("role_or_title"),
                primary_jurisdiction=target.get("primary_jurisdiction"),
                aliases=list(set([target["canonical_name"]] + target.get("aliases", []))),
                confidence_score=1.0,
                metadata=target.get("metadata", {}),
            )
            self._canonical_lookup[entity_id] = canonical_ent
            for alias in canonical_ent.aliases:
                norm_alias = self.normalize_name(alias)
                self._alias_to_canonical_id[norm_alias] = entity_id

    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Stage 1: Normalization & Corporate Suffix Stripping.
        Uppercases, removes honorifics, strips end-anchored suffixes, standardizes whitespace.
        """
        if not name:
            return ""

        # 1. Unicode normalization & basic cleanup
        norm = unicodedata.normalize("NFKC", name).strip()
        norm = re.sub(r"[^\w\s\-\.\,\&]", "", norm)

        # 2. Strip honorific prefixes
        norm = HONORIFIC_PREFIX_RE.sub("", norm).strip()

        # 3. Strip corporate suffixes from right end
        match = CORP_SUFFIX_RE.search(norm)
        if match:
            norm = norm[:match.start()].rstrip(" ,.")

        # 4. Collapse whitespace
        norm = re.sub(r"\s+", " ", norm).strip().upper()
        return norm

    @staticmethod
    def get_blocking_keys(name: str) -> Set[str]:
        """
        Stage 2: Deterministic & Phonetic Blocking Keys.
        Generates Soundex, Double Metaphone, and token keys for candidate partitioning.
        """
        keys = set()
        clean = EntityResolver.normalize_name(name)
        if not clean:
            return keys

        # Exact core stem key
        keys.add(f"STEM:{clean}")

        # Soundex & Double Metaphone for full string
        sx = soundex(clean)
        if sx and sx != "0000":
            keys.add(f"SX:{sx}")

        dm_p, dm_s = double_metaphone(clean)
        if dm_p:
            keys.add(f"DM:{dm_p}")
        if dm_s:
            keys.add(f"DM:{dm_s}")

        # Prefix key
        if len(clean) >= 3:
            keys.add(f"PRE3:{clean[:3]}")

        # Token-level blocking keys (crucial for multi-word and name variants)
        words = clean.split()
        for w in words:
            if len(w) >= 3 and w not in STOP_WORDS:
                keys.add(f"TOK:{w}")
                w_sx = soundex(w)
                if w_sx and w_sx != "0000":
                    keys.add(f"TOK_SX:{w_sx}")
                w_p, w_s = double_metaphone(w)
                if w_p:
                    keys.add(f"TOK_DM:{w_p}")
                if w_s:
                    keys.add(f"TOK_DM:{w_s}")

        return keys

    def resolve_single_name(
        self,
        name: str,
        category: Optional[EntityCategory] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[CanonicalEntity]:
        """
        Resolves a single entity name against the canonical knowledge base using 4 stages.
        """
        if not name or not name.strip():
            return None

        norm_name = self.normalize_name(name)
        if not norm_name:
            return None

        # Check exact normalized alias match
        if norm_name in self._alias_to_canonical_id:
            ent_id = self._alias_to_canonical_id[norm_name]
            return self._canonical_lookup[ent_id]

        # Stage 2 & 3: Blocking & Multi-score fuzzy match against canonical pool
        best_match: Optional[CanonicalEntity] = None
        best_score = 0.0

        ctx = context or {}
        has_context = bool(ctx.get("shared_docket") or ctx.get("shared_address") or ctx.get("shared_agency"))
        shared_docket = bool(ctx.get("shared_docket"))
        shared_address = bool(ctx.get("shared_address"))
        shared_agency = bool(ctx.get("shared_agency"))

        cand_keys = self.get_blocking_keys(norm_name)

        for ent_id, canonical_ent in self._canonical_lookup.items():
            if category and canonical_ent.entity_category != category and category != EntityCategory.OTHER:
                continue

            for alias in canonical_ent.aliases:
                norm_alias = self.normalize_name(alias)
                if norm_name == norm_alias:
                    return canonical_ent

                alias_keys = self.get_blocking_keys(norm_alias)

                # Blocking filter: must share at least one blocking key
                if not (cand_keys & alias_keys):
                    continue

                jw_score = jaro_winkler_similarity(norm_name, norm_alias)
                tok_score = token_overlap_score(norm_name, norm_alias)
                effective_str_score = max(jw_score, tok_score)

                if has_context:
                    composite = calculate_confidence(
                        string_similarity=effective_str_score,
                        shared_docket=shared_docket,
                        shared_address=shared_address,
                        shared_agency=shared_agency,
                        exact_match=False,
                    )
                else:
                    composite = effective_str_score

                if composite > best_score:
                    best_score = composite
                    best_match = canonical_ent

        if best_score >= self.similarity_threshold and best_match:
            return best_match

        return None

    def cluster_mentions(
        self,
        mentions: List[EntityMention],
        context_docs: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[CanonicalEntity], List[EntityMention]]:
        """
        Stage 4: DSU Graph Deduplication & Clustering across all mentions.
        """
        dsu = DisjointSetUnion()
        mention_map: Dict[str, EntityMention] = {}
        seed_matches: Dict[str, str] = {}
        blocks: Dict[str, Set[str]] = defaultdict(set)

        for m in mentions:
            mention_map[m.mention_id] = m
            dsu.add(m.mention_id)
            norm = self.normalize_name(m.raw_text)

            # Check seed canonical match
            seed_ent = self.resolve_single_name(m.raw_text, category=m.entity_category)
            if seed_ent:
                seed_matches[m.mention_id] = seed_ent.entity_id

            # Assign blocking keys
            for b_key in self.get_blocking_keys(norm):
                blocks[b_key].add(m.mention_id)

        # Merge mentions that resolved to the same seed target
        seed_to_mentions: Dict[str, List[str]] = defaultdict(list)
        for mid, seed_id in seed_matches.items():
            seed_to_mentions[seed_id].append(mid)

        for seed_id, m_ids in seed_to_mentions.items():
            first_id = m_ids[0]
            for other_id in m_ids[1:]:
                dsu.union(first_id, other_id)

        # Pairwise comparison within blocks
        checked_pairs: Set[Tuple[str, str]] = set()
        for b_key, m_ids in blocks.items():
            m_list = list(m_ids)
            n = len(m_list)
            for i in range(n):
                for j in range(i + 1, n):
                    id_a, id_b = m_list[i], m_list[j]
                    pair_key = (min(id_a, id_b), max(id_a, id_b))
                    if pair_key in checked_pairs:
                        continue
                    checked_pairs.add(pair_key)

                    m_a = mention_map[id_a]
                    m_b = mention_map[id_b]

                    # Category constraint
                    if m_a.entity_category != EntityCategory.OTHER and m_b.entity_category != EntityCategory.OTHER:
                        if m_a.entity_category != m_b.entity_category:
                            continue

                    norm_a = self.normalize_name(m_a.raw_text)
                    norm_b = self.normalize_name(m_b.raw_text)

                    if norm_a == norm_b:
                        dsu.union(id_a, id_b)
                        continue

                    jw = jaro_winkler_similarity(norm_a, norm_b)
                    tok = token_overlap_score(norm_a, norm_b)
                    effective = max(jw, tok)

                    if effective >= self.similarity_threshold:
                        dsu.union(id_a, id_b)

        # Extract clusters and assign canonical entities
        clusters = dsu.get_clusters()
        resolved_entities: List[CanonicalEntity] = []
        updated_mentions: List[EntityMention] = []

        for root_id, member_ids in clusters.items():
            member_mentions = [mention_map[mid] for mid in member_ids]
            all_raw_names = [m.raw_text.strip() for m in member_mentions]

            # Try to resolve against seed knowledge base first
            seed_canonical: Optional[CanonicalEntity] = None
            for mid in member_ids:
                if mid in seed_matches:
                    seed_canonical = self._canonical_lookup[seed_matches[mid]]
                    break

            if not seed_canonical:
                for raw_n in all_raw_names:
                    match = self.resolve_single_name(raw_n)
                    if match:
                        seed_canonical = match
                        break

            if seed_canonical:
                canonical_id = seed_canonical.entity_id
                canonical_name = seed_canonical.canonical_name
                category = seed_canonical.entity_category
                role = seed_canonical.role_or_title
                jurisdiction = seed_canonical.primary_jurisdiction
                aliases = list(set(seed_canonical.aliases + all_raw_names))
                metadata = dict(seed_canonical.metadata)
            else:
                # Form new canonical entity
                canonical_name = max(all_raw_names, key=lambda n: (len(n), n))
                cat_counts: Dict[EntityCategory, int] = defaultdict(int)
                for m in member_mentions:
                    if m.entity_category != EntityCategory.OTHER:
                        cat_counts[m.entity_category] += 1
                category = max(cat_counts, key=cat_counts.get) if cat_counts else EntityCategory.OTHER

                prefix = get_category_prefix(category)
                raw_hash = hashlib.sha256(canonical_name.encode("utf-8")).hexdigest()[:8].upper()
                canonical_id = f"{prefix}-{raw_hash}"
                role = None
                jurisdiction = None
                aliases = list(set(all_raw_names))
                metadata = {}

            canonical_entity = CanonicalEntity(
                entity_id=canonical_id,
                canonical_name=canonical_name,
                entity_category=category,
                role_or_title=role,
                primary_jurisdiction=jurisdiction,
                aliases=aliases,
                confidence_score=1.0,
                metadata=metadata,
            )
            resolved_entities.append(canonical_entity)

            # Update mention links
            for m in member_mentions:
                m.entity_id = canonical_id
                m.entity_category = category
                updated_mentions.append(m)

        return resolved_entities, updated_mentions

    def extract_and_resolve(
        self,
        records: Sequence[Any],
    ) -> Tuple[
        List[CanonicalEntity],
        List[EntityMention],
        List[TimelineEvent],
        List[FinancialTransaction],
        List[Relationship],
    ]:
        """
        Full extraction and resolution pass over extracted document records.
        Extracts mentions, timeline events, financial transactions, and relational edges.
        """
        all_mentions: List[EntityMention] = []
        all_events: List[TimelineEvent] = []
        all_transactions: List[FinancialTransaction] = []
        all_relationships: List[Relationship] = []

        seen_mentions_keys: Set[Tuple[str, str, int]] = set()

        for rec in records:
            doc_id = getattr(rec, "record_id", None) or getattr(rec, "artifact_sha256", str(uuid.uuid4()))
            text = getattr(rec, "extracted_text", "") or ""
            doc_date = getattr(rec, "normalized_date", None)
            sender = getattr(rec, "sender", None)
            recipients = getattr(rec, "recipients", []) or []
            financial_amounts = getattr(rec, "financial_amounts", []) or []
            case_numbers = getattr(rec, "case_numbers", []) or []

            # 1. Regex & Pattern-based mention extraction from text
            for pattern, cat, canon_name in KNOWN_ENTITY_PATTERNS:
                for match in pattern.finditer(text):
                    m_text = match.group(0).strip()
                    start_off = match.start()
                    end_off = match.end()
                    key = (doc_id, m_text.lower(), start_off)
                    if key in seen_mentions_keys:
                        continue
                    seen_mentions_keys.add(key)

                    snip_start = max(0, start_off - 50)
                    snip_end = min(len(text), end_off + 50)
                    snippet = text[snip_start:snip_end].replace("\n", " ").strip()

                    mention_id = f"MEN-{uuid.uuid4().hex[:12].upper()}"
                    mention = EntityMention(
                        mention_id=mention_id,
                        document_id=doc_id,
                        raw_text=m_text,
                        entity_category=cat,
                        char_offset_start=start_off,
                        char_offset_end=end_off,
                        context_snippet=snippet,
                        confidence_score=0.95,
                        extraction_method="REGEX",
                    )
                    all_mentions.append(mention)

            # 2. Extract correspondence mentions (Sender / Recipients)
            if sender:
                key = (doc_id, sender.lower(), 0)
                if key not in seen_mentions_keys:
                    seen_mentions_keys.add(key)
                    all_mentions.append(EntityMention(
                        mention_id=f"MEN-{uuid.uuid4().hex[:12].upper()}",
                        document_id=doc_id,
                        raw_text=sender,
                        entity_category=EntityCategory.INDIVIDUAL,
                        context_snippet=f"From: {sender}",
                        confidence_score=0.90,
                        extraction_method="NER",
                    ))

            for r in recipients:
                key = (doc_id, r.lower(), 0)
                if key not in seen_mentions_keys:
                    seen_mentions_keys.add(key)
                    all_mentions.append(EntityMention(
                        mention_id=f"MEN-{uuid.uuid4().hex[:12].upper()}",
                        document_id=doc_id,
                        raw_text=r,
                        entity_category=EntityCategory.INDIVIDUAL,
                        context_snippet=f"To: {r}",
                        confidence_score=0.90,
                        extraction_method="NER",
                    ))

            # 3. Extract Timeline Events
            line_events: List[TimelineEvent] = []
            seen_event_dates: Set[str] = set()

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines:
                line_dates = extract_dates(line)
                if line_dates:
                    l_date = line_dates[0].iso_value
                    if l_date in seen_event_dates:
                        continue
                    seen_event_dates.add(l_date)

                    line_lower = line.lower()
                    event_type = EventType.OTHER
                    if any(kw in line_lower for kw in ["indictment", "plea", "plea agreement", "felony", "complaint", "docket", "summons", "warrant", "unlawful detainer", "writ", "judgment", "challenge", "stay order"]):
                        event_type = EventType.JUDICIAL_FILING
                    elif any(kw in line_lower for kw in ["resolution", "council", "ordinance", "city council", "disclosure"]):
                        event_type = EventType.LEGISLATIVE_ACTION
                    elif any(kw in line_lower for kw in ["notice of violation", "regulatory", "hcd", "surplus land act", "report", "violation"]):
                        event_type = EventType.REGULATORY_NOTICE
                    elif any(kw in line_lower for kw in ["incident", "police", "arrest", "search warrant", "chain of custody", "affidavit"]):
                        event_type = EventType.INCIDENT_LOG

                    parts = l_date.split("T")[0].split("-")
                    yr = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 2022
                    mo = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                    dy = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

                    event_id = f"EVT-{l_date.replace('-', '').replace(':', '')[:8]}-{uuid.uuid4().hex[:6].upper()}"
                    clean_line = re.sub(r"<[^>]+>", " ", line).strip()
                    title = f"{event_type.value}: {clean_line[:120].strip()}"
                    description = clean_line

                    line_events.append(TimelineEvent(
                        event_id=event_id,
                        document_id=doc_id,
                        event_date_iso=l_date,
                        event_year=yr,
                        event_month=mo,
                        event_day=dy,
                        event_type=event_type,
                        title=title,
                        description=description,
                        raw_snippet=clean_line[:300].strip(),
                        confidence_score=1.0,
                    ))

            if len(line_events) > 1:
                all_events.extend(line_events)
            elif doc_date and len(text.strip()) > 0:
                first_line = text.strip().split("\n")[0][:120].strip()
                event_type = EventType.OTHER
                text_lower = text.lower()

                if any(kw in text_lower for kw in ["indictment", "plea", "plea agreement", "felony", "complaint", "docket", "summons", "warrant", "unlawful detainer"]):
                    event_type = EventType.JUDICIAL_FILING
                elif any(kw in text_lower for kw in ["resolution", "council", "ordinance", "city council"]):
                    event_type = EventType.LEGISLATIVE_ACTION
                elif any(kw in text_lower for kw in ["notice of violation", "regulatory", "hcd", "surplus land act"]):
                    event_type = EventType.REGULATORY_NOTICE
                elif any(kw in text_lower for kw in ["incident", "police", "arrest", "search warrant", "chain of custody"]):
                    event_type = EventType.INCIDENT_LOG
                elif financial_amounts:
                    event_type = EventType.FINANCIAL_TRANSACTION

                parts = doc_date.split("T")[0].split("-")
                yr = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 2022
                mo = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                dy = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None

                event_id = f"EVT-{doc_date.replace('-', '').replace(':', '')[:8]}-{uuid.uuid4().hex[:6].upper()}"
                title = f"{event_type.value}: {first_line or 'Official Record'}"
                description = text[:1000].strip()

                evt = TimelineEvent(
                    event_id=event_id,
                    document_id=doc_id,
                    event_date_iso=doc_date,
                    event_year=yr,
                    event_month=mo,
                    event_day=dy,
                    event_type=event_type,
                    title=title,
                    description=description,
                    raw_snippet=text[:300].strip(),
                    confidence_score=1.0,
                )
                all_events.append(evt)
            elif line_events:
                all_events.extend(line_events)

            # 4. Extract Financial Transactions
            for idx, fin in enumerate(financial_amounts):
                amt_float = fin.get("amount_float", 0.0)
                if amt_float > 0:
                    raw_str = fin.get("raw", "")
                    trx_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
                    trx_date = doc_date or "2022-01-01"

                    pay_method = PaymentMethod.UNKNOWN
                    t_lower = text.lower()
                    if "wire" in t_lower:
                        pay_method = PaymentMethod.WIRE
                    elif "escrow" in t_lower:
                        pay_method = PaymentMethod.ESCROW
                    elif "grant" in t_lower:
                        pay_method = PaymentMethod.GRANT
                    elif "check" in t_lower:
                        pay_method = PaymentMethod.CHECK
                    elif "invoice" in t_lower:
                        pay_method = PaymentMethod.INVOICE

                    is_pred = bool(any(p in t_lower for p in ["bribe", "conspiracy", "slush", "kickback", "conduit", "unlawful", "fraud"]))

                    trx = FinancialTransaction(
                        transaction_id=trx_id,
                        document_id=doc_id,
                        transaction_date_iso=trx_date,
                        amount=float(amt_float),
                        currency=fin.get("currency", "USD"),
                        sender_raw_text=sender,
                        recipient_raw_text=recipients[0] if recipients else None,
                        payment_method=pay_method,
                        transaction_purpose=f"Financial transaction recorded in document: {raw_str}",
                        is_predicate_act=is_pred,
                        raw_snippet=text[:300].strip(),
                    )
                    all_transactions.append(trx)

        # 5. Cluster & resolve all collected mentions
        resolved_entities, updated_mentions = self.cluster_mentions(all_mentions)
        resolved_map = {e.entity_id: e for e in resolved_entities}

        # Associate primary entities to events and financial transactions
        for evt in all_events:
            doc_mentions = [m for m in updated_mentions if m.document_id == evt.document_id and m.entity_id]
            if doc_mentions:
                evt.primary_entity_id = doc_mentions[0].entity_id

        for trx in all_transactions:
            doc_mentions = [m for m in updated_mentions if m.document_id == trx.document_id and m.entity_id]
            if doc_mentions:
                if len(doc_mentions) >= 2:
                    trx.sender_entity_id = doc_mentions[0].entity_id
                    trx.recipient_entity_id = doc_mentions[1].entity_id
                else:
                    trx.recipient_entity_id = doc_mentions[0].entity_id

        # 6. Infer Relational Graph Edges
        doc_to_entities: Dict[str, Set[str]] = defaultdict(set)
        for m in updated_mentions:
            if m.entity_id:
                doc_to_entities[m.document_id].add(m.entity_id)

        seen_rels: Set[Tuple[str, str, str]] = set()
        for doc_id, ent_ids in doc_to_entities.items():
            ent_list = list(ent_ids)
            for i in range(len(ent_list)):
                for j in range(i + 1, len(ent_list)):
                    src, tgt = ent_list[i], ent_list[j]
                    if src == tgt:
                        continue

                    if src > tgt:
                        src, tgt = tgt, src

                    rel_type = RelationshipType.CONNECTED_TO
                    src_ent = resolved_map.get(src)
                    tgt_ent = resolved_map.get(tgt)

                    if src_ent and tgt_ent:
                        if src_ent.entity_category == EntityCategory.INDIVIDUAL and tgt_ent.entity_category == EntityCategory.MUNICIPAL_BODY:
                            rel_type = RelationshipType.OFFICER_OF
                        elif src_ent.entity_category == EntityCategory.INDIVIDUAL and tgt_ent.entity_category == EntityCategory.FINANCIAL_INSTITUTION:
                            rel_type = RelationshipType.CONTROLLED_BY
                        elif src_ent.entity_category == EntityCategory.COMMERCIAL_ENTITY and tgt_ent.entity_category == EntityCategory.PROPERTY_MANAGEMENT:
                            rel_type = RelationshipType.REPRESENTED_BY

                    rel_key = (src, tgt, rel_type.value)
                    if rel_key not in seen_rels:
                        seen_rels.add(rel_key)
                        all_relationships.append(Relationship(
                            relationship_id=f"REL-{uuid.uuid4().hex[:8].upper()}",
                            source_entity_id=src,
                            target_entity_id=tgt,
                            relationship_type=rel_type,
                            direction="DIRECTED",
                            confidence=0.90,
                            source_document_id=doc_id,
                            evidence_summary=f"Co-occurring entities detected in document {doc_id}",
                        ))

        # Sort timeline events chronologically and assign ranks
        all_events.sort(key=lambda e: e.event_date_iso)
        for rank, evt in enumerate(all_events, start=1):
            evt.chronological_rank = rank

        return resolved_entities, updated_mentions, all_events, all_transactions, all_relationships
