#!/usr/bin/env python3
"""
OSINT Network Visualization Engine
===================================
Advanced Maltego-style network visualization, graph analysis, and relationship mapping.
Supports interactive visualizations, community detection, centrality analysis, and exports.

Features:
  - Interactive network graphs (Plotly, NetworkX)
  - Maltego-style node/edge visualization
  - Community detection & clustering
  - Centrality analysis (betweenness, closeness, eigenvector)
  - Temporal network analysis
  - Graph statistics & metrics
  - Multiple export formats (JSON, HTML, SVG, PNG)
"""

import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import datetime
from collections import defaultdict
import math

try:
    import networkx as nx
    from networkx.algorithms import community
    from networkx.readwrite import json_graph
except ImportError:
    os.system("pip install networkx")
    import networkx as nx
    from networkx.algorithms import community
    from networkx.readwrite import json_graph

try:
    import plotly.graph_objects as go
    import plotly.express as px
except ImportError:
    os.system("pip install plotly")
    import plotly.graph_objects as go
    import plotly.express as px

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    os.system("pip install pillow")
    from PIL import Image, ImageDraw, ImageFont

# ── Network Analysis Engine ──────────────────────────────────────────────────
class NetworkAnalysisEngine:
    """Advanced network analysis with multiple algorithms."""
    
    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.metrics = {}
        self.centralities = {}
        self.communities = {}
    
    def calculate_all_metrics(self) -> Dict:
        """Calculate comprehensive network metrics."""
        if self.graph.number_of_nodes() == 0:
            return {}
        
        metrics = {
            'basic': self._calculate_basic_metrics(),
            'centrality': self._calculate_centralities(),
            'communities': self._detect_communities(),
            'clustering': self._calculate_clustering(),
            'paths': self._calculate_path_metrics()
        }
        
        self.metrics = metrics
        return metrics
    
    def _calculate_basic_metrics(self) -> Dict:
        """Basic network statistics."""
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            'connected_components': nx.number_connected_components(self.graph),
            'is_connected': nx.is_connected(self.graph),
            'diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) else None,
            'avg_clustering_coefficient': nx.average_clustering(self.graph)
        }
    
    def _calculate_centralities(self) -> Dict:
        """Calculate various centrality measures."""
        centralities = {}
        
        # Degree centrality
        centralities['degree'] = nx.degree_centrality(self.graph)
        
        # Betweenness centrality
        centralities['betweenness'] = nx.betweenness_centrality(self.graph)
        
        # Closeness centrality
        centralities['closeness'] = nx.closeness_centrality(self.graph)
        
        # Eigenvector centrality
        try:
            centralities['eigenvector'] = nx.eigenvector_centrality(self.graph, max_iter=1000)
        except:
            centralities['eigenvector'] = {}
        
        # PageRank
        centralities['pagerank'] = nx.pagerank(self.graph)
        
        self.centralities = centralities
        return centralities
    
    def _detect_communities(self) -> Dict:
        """Detect communities using multiple algorithms."""
        if self.graph.number_of_nodes() == 0:
            return {}
        
        communities_data = {}
        
        try:
            # Greedy modularity optimization
            greedy_comms = community.greedy_modularity_communities(self.graph)
            communities_data['greedy_modularity'] = [list(comm) for comm in greedy_comms]
        except:
            pass
        
        try:
            # Louvain method
            louvain_comms = community.louvain_communities(self.graph)
            communities_data['louvain'] = [list(comm) for comm in louvain_comms]
        except:
            pass
        
        self.communities = communities_data
        return communities_data
    
    def _calculate_clustering(self) -> Dict:
        """Calculate clustering coefficients."""
        return {
            'node_clustering': nx.clustering(self.graph),
            'transitivity': nx.transitivity(self.graph),
            'avg_clustering': nx.average_clustering(self.graph)
        }
    
    def _calculate_path_metrics(self) -> Dict:
        """Calculate path-based metrics."""
        if not nx.is_connected(self.graph):
            return {'is_connected': False}
        
        try:
            avg_shortest_path = nx.average_shortest_path_length(self.graph)
        except:
            avg_shortest_path = None
        
        return {
            'is_connected': True,
            'avg_shortest_path_length': avg_shortest_path,
            'diameter': nx.diameter(self.graph)
        }
    
    def get_top_influencers(self, metric: str = 'betweenness', top_n: int = 10) -> List[Tuple]:
        """Get top influencers by centrality metric."""
        if metric not in self.centralities:
            return []
        
        centrality = self.centralities[metric]
        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:top_n]
    
    def get_bridge_nodes(self) -> List:
        """Find bridge nodes (connectors between communities)."""
        bridges = []
        for node in self.graph.nodes():
            neighbors = set(self.graph.neighbors(node))
            if len(neighbors) > 1:
                neighbor_edges = 0
                for n1 in neighbors:
                    for n2 in neighbors:
                        if n1 < n2 and self.graph.has_edge(n1, n2):
                            neighbor_edges += 1
                
                total_possible = len(neighbors) * (len(neighbors) - 1) / 2
                if neighbor_edges < total_possible * 0.3:  # Sparse connections
                    bridges.append(node)
        
        return bridges

# ── Visualization Generators ─────────────────────────────────────────────────
class MaltegoStyleVisualizer:
    """Generate Maltego-style network visualizations."""
    
    def __init__(self, graph: nx.Graph, people_map: Dict = None):
        self.graph = graph
        self.people_map = people_map or {}
        self.pos = None
        self.node_colors = {}
        self.node_sizes = {}
    
    def generate_interactive_html(self, output_path: str, title: str = "OSINT Network"):
        """Generate interactive Plotly visualization."""
        
        # Layout
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50, seed=42)
        self.pos = pos
        
        # Prepare edges
        edge_x = []
        edge_y = []
        edge_text = []
        edge_colors = []
        
        for edge in self.graph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            strength = edge[2].get('strength', 0.5)
            edge_text.append(f"Type: {edge[2].get('connection_type', 'contact')}<br>Strength: {strength:.1%}<br>Evidence: {edge[2].get('evidence', 'N/A')}")
            
            # Color by strength
            if strength > 0.7:
                edge_colors.append('rgba(50, 200, 50, 0.6)')  # Green
            elif strength > 0.5:
                edge_colors.append('rgba(255, 180, 0, 0.6)')  # Orange
            else:
                edge_colors.append('rgba(200, 50, 50, 0.6)')  # Red
        
        # Create edge trace
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            hoverinfo='text',
            hovertext=edge_text,
            line=dict(width=0.5, color='#888'),
            showlegend=False
        )
        
        # Prepare nodes
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        node_size = []
        
        for node in self.graph.nodes(data=True):
            x, y = pos[node[0]]
            node_x.append(x)
            node_y.append(y)
            
            person = self.people_map.get(node[0], {})
            person_name = person.get('name', node[0]) if isinstance(person, dict) else getattr(person, 'name', node[0])
            
            hover_text = f"<b>{person_name}</b><br>"
            
            if isinstance(person, dict):
                for key, value in person.items():
                    if value and key not in ['id', 'name']:
                        hover_text += f"{key}: {value}<br>"
            else:
                for attr in ['email', 'phone', 'business', 'city', 'state']:
                    value = getattr(person, attr, None)
                    if value:
                        hover_text += f"{attr}: {value}<br>"
            
            node_text.append(hover_text)
            
            # Size by degree
            degree = self.graph.degree(node[0])
            node_size.append(max(10, 10 + degree * 5))
            
            # Color by community (if available)
            node_color.append('rgba(100, 150, 255, 0.8)')
        
        # Create node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[self.people_map.get(node, {}).get('name', node) if isinstance(self.people_map.get(node, {}), dict) else getattr(self.people_map.get(node), 'name', node) for node in self.graph.nodes()],
            textposition='top center',
            hoverinfo='text',
            hovertext=node_text,
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='#222'),
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title={
                               'text': title,
                               'x': 0.5,
                               'xanchor': 'center',
                               'font': {'size': 20, 'color': '#1F4E78'}
                           },
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='#f8f9fa',
                           paper_bgcolor='white',
                           height=800,
                           width=1200
                       ))
        
        fig.write_html(output_path)
        print(f"✅ Interactive visualization saved: {output_path}")
    
    def generate_community_view(self, output_path: str, communities: List[List]):
        """Generate community-colored network visualization."""
        
        if not self.pos:
            self.pos = nx.spring_layout(self.graph, k=0.5, iterations=50, seed=42)
        
        # Assign colors to communities
        community_colors = {}
        color_palette = [
            'rgba(50, 150, 255, 0.8)',
            'rgba(255, 100, 50, 0.8)',
            'rgba(100, 255, 50, 0.8)',
            'rgba(255, 200, 50, 0.8)',
            'rgba(200, 50, 255, 0.8)',
            'rgba(50, 255, 200, 0.8)',
        ]
        
        for idx, comm in enumerate(communities):
            color = color_palette[idx % len(color_palette)]
            for node in comm:
                community_colors[node] = color
        
        # Build visualization
        edge_x = []
        edge_y = []
        
        for edge in self.graph.edges():
            x0, y0 = self.pos[edge[0]]
            x1, y1 = self.pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=1, color='#888'),
            showlegend=False
        )
        
        # Nodes
        node_x = []
        node_y = []
        node_color = []
        node_text = []
        
        for node in self.graph.nodes():
            x, y = self.pos[node]
            node_x.append(x)
            node_y.append(y)
            node_color.append(community_colors.get(node, 'rgba(100, 100, 100, 0.8)'))
            
            person = self.people_map.get(node, {})
            person_name = person.get('name', node) if isinstance(person, dict) else getattr(person, 'name', node)
            node_text.append(person_name)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            textposition='top center',
            marker=dict(size=15, color=node_color, line=dict(width=2)),
            showlegend=False
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Community-Based Network View',
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=0, l=0, r=0, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='#f8f9fa',
                           height=800,
                           width=1200
                       ))
        
        fig.write_html(output_path)
        print(f"✅ Community view saved: {output_path}")

# ── Advanced Export Formats ──────────────────────────────────────────────────
class NetworkExporter:
    """Export network in various formats."""
    
    def __init__(self, graph: nx.Graph, people_map: Dict = None):
        self.graph = graph
        self.people_map = people_map or {}
    
    def export_json(self, output_path: str) -> str:
        """Export to JSON format."""
        data = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'nodes_count': self.graph.number_of_nodes(),
                'edges_count': self.graph.number_of_edges(),
                'generated': datetime.datetime.now().isoformat()
            }
        }
        
        for node in self.graph.nodes(data=True):
            node_data = {
                'id': node[0],
                'label': self.people_map.get(node[0], {}).get('name', node[0]) if isinstance(self.people_map.get(node[0], {}), dict) else getattr(self.people_map.get(node[0]), 'name', node[0]),
                'attributes': node[1]
            }
            data['nodes'].append(node_data)
        
        for edge in self.graph.edges(data=True):
            edge_data = {
                'source': edge[0],
                'target': edge[1],
                'attributes': edge[2]
            }
            data['edges'].append(edge_data)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ JSON export: {output_path}")
        return output_path
    
    def export_gexf(self, output_path: str) -> str:
        """Export to GEXF (Gephi) format."""
        nx.write_gexf(self.graph, output_path)
        print(f"✅ GEXF export (Gephi compatible): {output_path}")
        return output_path
    
    def export_graphml(self, output_path: str) -> str:
        """Export to GraphML format."""
        nx.write_graphml(self.graph, output_path)
        print(f"✅ GraphML export: {output_path}")
        return output_path
    
    def export_csv(self, output_path: str) -> str:
        """Export edges to CSV."""
        import csv
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source', 'Target', 'Type', 'Strength', 'Evidence'])
            
            for edge in self.graph.edges(data=True):
                writer.writerow([
                    edge[0],
                    edge[1],
                    edge[2].get('connection_type', 'contact'),
                    f"{edge[2].get('strength', 0):.2f}",
                    edge[2].get('evidence', '')
                ])
        
        print(f"✅ CSV export: {output_path}")
        return output_path

# ── Temporal Network Analysis ────────────────────────────────────────────────
class TemporalNetworkAnalyzer:
    """Analyze network evolution over time."""
    
    def __init__(self):
        self.snapshots = {}
        self.events = []
    
    def add_snapshot(self, timestamp: str, graph: nx.Graph):
        """Add network snapshot at specific timestamp."""
        self.snapshots[timestamp] = graph
    
    def calculate_evolution(self) -> Dict:
        """Calculate how network evolved over time."""
        evolution = {
            'nodes_over_time': [],
            'edges_over_time': [],
            'density_over_time': [],
            'clustering_over_time': []
        }
        
        for timestamp in sorted(self.snapshots.keys()):
            graph = self.snapshots[timestamp]
            evolution['nodes_over_time'].append((timestamp, graph.number_of_nodes()))
            evolution['edges_over_time'].append((timestamp, graph.number_of_edges()))
            evolution['density_over_time'].append((timestamp, nx.density(graph)))
            evolution['clustering_over_time'].append((timestamp, nx.average_clustering(graph)))
        
        return evolution
    
    def detect_node_emergence(self) -> List:
        """Detect when new nodes appeared."""
        if len(self.snapshots) < 2:
            return []
        
        timestamps = sorted(self.snapshots.keys())
        emergent_nodes = []
        
        for i in range(len(timestamps) - 1):
            t1_nodes = set(self.snapshots[timestamps[i]].nodes())
            t2_nodes = set(self.snapshots[timestamps[i+1]].nodes())
            
            new_nodes = t2_nodes - t1_nodes
            if new_nodes:
                emergent_nodes.append({
                    'timestamp': timestamps[i+1],
                    'new_nodes': list(new_nodes)
                })
        
        return emergent_nodes

# ── Risk Assessment Engine ───────────────────────────────────────────────────
class RiskAssessmentEngine:
    """Assess risk factors and anomalies in network."""
    
    def __init__(self, graph: nx.Graph, people_map: Dict = None):
        self.graph = graph
        self.people_map = people_map or {}
        self.risk_scores = {}
    
    def calculate_risk_scores(self) -> Dict:
        """Calculate risk scores for each node."""
        
        risk_factors = {
            'isolated_nodes': self._identify_isolated(),
            'high_connectivity': self._identify_hubs(),
            'bridge_nodes': self._identify_bridges(),
            'suspicious_patterns': self._identify_suspicious_patterns()
        }
        
        return risk_factors
    
    def _identify_isolated(self) -> List:
        """Identify isolated or low-connectivity nodes."""
        isolated = []
        avg_degree = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0
        
        for node in self.graph.nodes():
            degree = self.graph.degree(node)
            if degree < avg_degree * 0.3:
                isolated.append({
                    'node': node,
                    'degree': degree,
                    'risk': 'low_connectivity',
                    'severity': 'medium'
                })
        
        return isolated
    
    def _identify_hubs(self) -> List:
        """Identify highly connected hub nodes."""
        hubs = []
        avg_degree = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0
        
        for node in self.graph.nodes():
            degree = self.graph.degree(node)
            if degree > avg_degree * 2.5:
                hubs.append({
                    'node': node,
                    'degree': degree,
                    'risk': 'high_connectivity_hub',
                    'severity': 'high'
                })
        
        return hubs
    
    def _identify_bridges(self) -> List:
        """Identify bridge nodes connecting communities."""
        bridges = []
        
        try:
            comms = list(nx.algorithms.community.greedy_modularity_communities(self.graph))
            node_to_comm = {}
            for idx, comm in enumerate(comms):
                for node in comm:
                    node_to_comm[node] = idx
            
            for node in self.graph.nodes():
                neighbors = list(self.graph.neighbors(node))
                if len(neighbors) > 0:
                    neighbor_comms = set(node_to_comm.get(n, -1) for n in neighbors)
                    if len(neighbor_comms) > 1:
                        bridges.append({
                            'node': node,
                            'communities_bridged': len(neighbor_comms),
                            'risk': 'bridge_node',
                            'severity': 'medium'
                        })
        except:
            pass
        
        return bridges
    
    def _identify_suspicious_patterns(self) -> List:
        """Identify suspicious connection patterns."""
        suspicious = []
        
        for node in self.graph.nodes():
            neighbors = list(self.graph.neighbors(node))
            
            # Check if neighbors are not connected to each other (star pattern)
            connected_neighbors = 0
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i+1:]:
                    if self.graph.has_edge(n1, n2):
                        connected_neighbors += 1
            
            total_possible = len(neighbors) * (len(neighbors) - 1) / 2
            if total_possible > 0:
                cluster_coeff = connected_neighbors / total_possible
                if cluster_coeff < 0.1 and len(neighbors) > 3:
                    suspicious.append({
                        'node': node,
                        'pattern': 'star_topology',
                        'risk': 'unusual_connection_pattern',
                        'severity': 'medium',
                        'cluster_coefficient': cluster_coeff
                    })
        
        return suspicious
    
    def generate_risk_report(self) -> Dict:
        """Generate comprehensive risk assessment report."""
        risk_data = self.calculate_risk_scores()
        
        report = {
            'generated': datetime.datetime.now().isoformat(),
            'total_nodes': self.graph.number_of_nodes(),
            'risk_summary': {
                'isolated_nodes': len(risk_data['isolated_nodes']),
                'hub_nodes': len(risk_data['high_connectivity']),
                'bridge_nodes': len(risk_data['bridge_nodes']),
                'suspicious_patterns': len(risk_data['suspicious_patterns'])
            },
            'detailed_findings': risk_data,
            'recommendations': self._generate_recommendations(risk_data)
        }
        
        return report
    
    def _generate_recommendations(self, risk_data: Dict) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        if len(risk_data['isolated_nodes']) > 0:
            recommendations.append("⚠️ Multiple isolated nodes detected - investigate why these people have minimal connections")
        
        if len(risk_data['high_connectivity']) > 0:
            recommendations.append("🔴 High-connectivity hubs identified - these are key influencers or critical connectors")
        
        if len(risk_data['bridge_nodes']) > 0:
            recommendations.append("🟡 Bridge nodes detected - these connect separate communities and may be gatekeepers")
        
        if len(risk_data['suspicious_patterns']) > 0:
            recommendations.append("⚠️ Suspicious star-topology patterns found - indicates potential coordinator nodes")
        
        return recommendations

if __name__ == "__main__":
    print("✅ Network Visualization Engine loaded")
