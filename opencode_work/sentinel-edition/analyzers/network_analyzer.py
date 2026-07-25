"""
Network analysis algorithms for the Sentinel graph.
All implementations are dependency-free (no networkx required).
"""

import math
from collections import defaultdict, deque
from typing import Any


class GraphAlgorithms:
    """Pure-Python graph algorithms for OSINT network analysis."""

    @staticmethod
    def adjacency_list(edges: list[tuple[str, str, dict]]) -> dict[str, list[tuple[str, dict]]]:
        adj = defaultdict(list)
        for src, tgt, meta in edges:
            adj[src].append((tgt, meta))
            adj[tgt].append((src, meta))
        return dict(adj)

    @staticmethod
    def bfs(adj: dict, start: str, max_depth: int = None) -> dict[str, int]:
        distances = {start: 0}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            d = distances[node]
            if max_depth and d >= max_depth:
                continue
            for neighbor, _ in adj.get(node, []):
                if neighbor not in distances:
                    distances[neighbor] = d + 1
                    queue.append(neighbor)
        return distances

    @staticmethod
    def connected_components(adj: dict) -> list[set[str]]:
        visited = set()
        components = []
        for node in adj:
            if node not in visited:
                component = set()
                queue = deque([node])
                while queue:
                    n = queue.popleft()
                    if n in visited:
                        continue
                    visited.add(n)
                    component.add(n)
                    for neighbor, _ in adj.get(n, []):
                        if neighbor not in visited:
                            queue.append(neighbor)
                components.append(component)
        return components

    @staticmethod
    def degree_centrality(adj: dict) -> dict[str, float]:
        n = len(adj)
        if n <= 1:
            return {node: 0.0 for node in adj}
        degrees = {node: len(neighbors) for node, neighbors in adj.items()}
        max_deg = max(degrees.values()) if degrees else 1
        return {node: d / max_deg for node, d in degrees.items()}

    @staticmethod
    def betweenness_centrality(adj: dict, sample_size: int = None) -> dict[str, float]:
        nodes = list(adj.keys())
        betweenness = {n: 0.0 for n in nodes}

        if sample_size and sample_size < len(nodes):
            import random
            sources = random.sample(nodes, sample_size)
        else:
            sources = nodes

        for source in sources:
            stack = []
            predecessors = {n: [] for n in nodes}
            sigma = {n: 0.0 for n in nodes}
            sigma[source] = 1.0
            distance = {n: -1 for n in nodes}
            distance[source] = 0
            queue = deque([source])

            while queue:
                v = queue.popleft()
                stack.append(v)
                for w, _ in adj.get(v, []):
                    if distance[w] < 0:
                        distance[w] = distance[v] + 1
                        queue.append(w)
                    if distance[w] == distance[v] + 1:
                        sigma[w] += sigma[v]
                        predecessors[w].append(v)

            delta = {n: 0.0 for n in nodes}
            while stack:
                w = stack.pop()
                for v in predecessors[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
                if w != source:
                    betweenness[w] += delta[w]

        n = len(nodes)
        if n > 2:
            norm = 2.0 / ((n - 1) * (n - 2))
            betweenness = {k: v * norm for k, v in betweenness.items()}
        return betweenness

    @staticmethod
    def find_bridges(adj: dict) -> list[tuple[str, str]]:
        nodes = list(adj.keys())
        disc = {}
        low = {}
        parent = {}
        bridges = []
        timer = [0]

        def dfs(u):
            disc[u] = low[u] = timer[0]
            timer[0] += 1
            for v, _ in adj.get(u, []):
                if v not in disc:
                    parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])
                    if low[v] > disc[u]:
                        bridges.append((u, v))
                elif v != parent.get(u):
                    low[u] = min(low[u], disc[v])

        for node in nodes:
            if node not in disc:
                parent[node] = None
                dfs(node)
        return bridges

    @staticmethod
    def shortest_path(adj: dict, start: str, end: str) -> list[str]:
        if start == end:
            return [start]
        visited = {start}
        queue = deque([(start, [start])])
        while queue:
            node, path = queue.popleft()
            for neighbor, _ in adj.get(node, []):
                if neighbor == end:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    @staticmethod
    def pagerank(adj: dict, damping: float = 0.85, iterations: int = 100) -> dict[str, float]:
        nodes = list(adj.keys())
        n = len(nodes)
        if n == 0:
            return {}
        rank = {node: 1.0 / n for node in nodes}
        for _ in range(iterations):
            new_rank = {}
            for node in nodes:
                incoming = 0
                for other, neighbors in adj.items():
                    for neighbor, _ in neighbors:
                        if neighbor == node:
                            out_degree = len(neighbors) if neighbors else 1
                            incoming += rank[other] / out_degree
                new_rank[node] = (1 - damping) / n + damping * incoming
            rank = new_rank
        return rank

    @staticmethod
    def community_detection_greedy(adj: dict) -> dict[str, int]:
        """Greedy modularity community detection."""
        nodes = list(adj.keys())
        community = {n: i for i, n in enumerate(nodes)}
        m = sum(len(neighbors) for neighbors in adj.values()) // 2
        if m == 0:
            return community

        def modularity():
            q = 0.0
            for u in nodes:
                for v, _ in adj.get(u, []):
                    if community[u] == community[v]:
                        deg_u = len(adj.get(u, []))
                        deg_v = len(adj.get(v, []))
                        q += 1 - (deg_u * deg_v) / (2 * m)
            return q / (2 * m)

        best_q = modularity()
        for _ in range(50):
            improved = False
            for node in nodes:
                current_comm = community[node]
                best_comm = current_comm
                neighbor_comms = set(community.get(n, community[node]) for n, _ in adj.get(node, []))
                for comm in neighbor_comms:
                    if comm == current_comm:
                        continue
                    community[node] = comm
                    q = modularity()
                    if q > best_q:
                        best_q = q
                        best_comm = comm
                        improved = True
                community[node] = best_comm
            if not improved:
                break
        return community

    @staticmethod
    def risk_scoring(adj: dict, entity_metadata: dict = None) -> dict[str, float]:
        centrality = GraphAlgorithms.degree_centrality(adj)
        pagerank = GraphAlgorithms.Pagerank(adj) if hasattr(GraphAlgorithms, 'Pagerank') else GraphAlgorithms.pagerank(adj)
        bridges = GraphAlgorithms.find_bridges(adj)
        bridge_nodes = set()
        for u, v in bridges:
            bridge_nodes.add(u)
            bridge_nodes.add(v)

        risk = {}
        for node in adj:
            r = 0.0
            r += centrality.get(node, 0) * 30
            r += pagerank.get(node, 0) * 30
            if node in bridge_nodes:
                r += 15
            n_degree = len(adj.get(node, []))
            if n_degree > 10:
                r += 10
            elif n_degree > 5:
                r += 5
            if entity_metadata and node in entity_metadata:
                meta = entity_metadata[node]
                if meta.get("high_risk_flags"):
                    r += 20
            risk[node] = min(r, 100.0)
        return risk
