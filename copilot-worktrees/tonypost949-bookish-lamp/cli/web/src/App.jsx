import { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';
import { Activity, Globe, Mail, Network, Search } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000/api/graph';

export default function App() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const graphRef = useRef();

  useEffect(() => {
    fetchGraph();
    const interval = setInterval(fetchGraph, 5000); // Auto-refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const fetchGraph = async () => {
    try {
      const response = await axios.get(API_URL);
      const data = response.data;
      setEntities(data);
      
      // Transform Pydantic models to graph format
      const nodes = data.map(entity => ({
        id: entity.id,
        name: entity.value,
        type: entity.type,
        val: 10 // Node size
      }));
      
      // For now, no implicit links from backend, so nodes float freely or we mock connections
      // In a real OSINT graph, we'd have edges returned from backend
      const links = [];
      
      setGraphData({ nodes, links });
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch graph data:", error);
      setLoading(false);
    }
  };

  const getIconForType = (type) => {
    switch(type.toLowerCase()) {
      case 'domain': return <Globe size={18} color="#00f0ff" />;
      case 'email': return <Mail size={18} color="#b026ff" />;
      default: return <Activity size={18} color="#e2e8f0" />;
    }
  };

  const getNodeColor = (node) => {
    switch(node.type.toLowerCase()) {
      case 'domain': return '#00f0ff';
      case 'email': return '#b026ff';
      default: return '#e2e8f0';
    }
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    // Pan to node
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 1000);
      graphRef.current.zoom(8, 2000);
    }
  };

  if (loading && entities.length === 0) {
    return (
      <div className="loading-overlay">
        <div className="spinner"></div>
        <p>Loading Intelligence Graph...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <div className="graph-view">
        <ForceGraph2D
          ref={graphRef}
          graphData={graphData}
          nodeLabel="name"
          nodeColor={getNodeColor}
          nodeRelSize={6}
          onNodeClick={handleNodeClick}
          backgroundColor="#0b0f19"
          linkColor={() => 'rgba(255,255,255,0.2)'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name;
            const fontSize = 12/globalScale;
            ctx.font = `${fontSize}px Inter`;
            
            // Draw Node Circle
            ctx.beginPath();
            ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
            ctx.fillStyle = getNodeColor(node);
            ctx.fill();
            
            // Draw Glow
            ctx.shadowBlur = 15;
            ctx.shadowColor = getNodeColor(node);
            ctx.fill();
            ctx.shadowBlur = 0; // reset
            
            // Draw Text
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
            ctx.fillText(label, node.x, node.y + 12);
          }}
        />
      </div>

      <div className="sidebar">
        <div className="sidebar-header">
          <h1 className="sidebar-title">
            <Network size={28} color="#00f0ff" />
            OSINT Graph
          </h1>
        </div>

        <div className="entities-list">
          {entities.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No entities in the graph yet. Run a command in the CLI to add some!</p>
          ) : (
            entities.map((entity) => (
              <div 
                key={entity.id} 
                className="entity-card"
                onClick={() => {
                  const node = graphData.nodes.find(n => n.id === entity.id);
                  if (node) handleNodeClick(node);
                }}
              >
                <div className="entity-type">
                  {getIconForType(entity.type)}
                  <span style={{ marginLeft: '8px' }}>{entity.type}</span>
                </div>
                <div className="entity-value">{entity.value}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
