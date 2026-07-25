import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

interface Entity {
  id: number;
  name: string;
  type: string;
  fileCount: number;
  connectionCount: number;
}

interface Relationship {
  id: number;
  entity1Id: number;
  entity2Id: number;
  coOccurrenceCount: number;
  strength: string;
}

interface NetworkVisualizationProps {
  entities: Entity[];
  relationships: Relationship[];
}

export default function NetworkVisualization({
  entities,
  relationships,
}: NetworkVisualizationProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<number | null>(null);

  useEffect(() => {
    if (!svgRef.current || entities.length === 0) return;

    // Prepare data for D3
    const nodes = entities.map((entity) => ({
      id: entity.id,
      name: entity.name,
      type: entity.type,
      fileCount: entity.fileCount,
      connectionCount: entity.connectionCount,
    }));

    const links = relationships.map((rel) => ({
      source: rel.entity1Id,
      target: rel.entity2Id,
      value: rel.coOccurrenceCount,
      strength: parseFloat(rel.strength),
    }));

    // Set dimensions
    const width = svgRef.current.clientWidth || 800;
    const height = 600;

    // Clear previous content
    d3.select(svgRef.current).selectAll("*").remove();

    // Create SVG
    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodes as any)
      .force(
        "link",
        d3
          .forceLink(links as any)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-400))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius((d: any) => d.fileCount * 3 + 10));

    // Create links
    const link = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke", "#cbd5e1")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d: any) => Math.sqrt(d.value) * 2);

    // Create nodes
    const node = svg
      .append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", (d: any) => d.fileCount * 3 + 10)
      .attr("fill", (d: any) => {
        if (d.type === "person") return "#3b82f6";
        if (d.type === "email") return "#8b5cf6";
        if (d.type === "phone") return "#ec4899";
        return "#6b7280";
      })
      .attr("stroke", "#fff")
      .attr("stroke-width", 2)
      .attr("cursor", "pointer")
      .on("click", (event, d: any) => {
        setSelectedNode(d.id);
      })
      .call(
        d3
          .drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended) as any
      );

    // Create labels
    const labels = svg
      .append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .attr("x", 0)
      .attr("y", 0)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "central")
      .attr("font-size", 11)
      .attr("fill", "#fff")
      .attr("pointer-events", "none")
      .text((d: any) => d.name.split(" ")[0]);

    // Add tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .style("position", "absolute")
      .style("background", "rgba(0,0,0,0.9)")
      .style("color", "white")
      .style("padding", "8px")
      .style("border-radius", "4px")
      .style("font-size", "12px")
      .style("pointer-events", "none")
      .style("opacity", 0);

    node.on("mouseover", (event, d: any) => {
      tooltip
        .style("opacity", 1)
        .html(
          `<strong>${d.name}</strong><br/>Type: ${d.type}<br/>Files: ${d.fileCount}<br/>Connections: ${d.connectionCount}`
        )
        .style("left", event.pageX + 10 + "px")
        .style("top", event.pageY - 10 + "px");
    }).on("mouseout", () => {
      tooltip.style("opacity", 0);
    });

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      labels.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      tooltip.remove();
    };
  }, [entities, relationships]);

  if (entities.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-slate-50 rounded-lg border border-slate-200">
        <p className="text-slate-600">No entities to visualize. Upload files to get started.</p>
      </div>
    );
  }

  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 overflow-hidden">
      <svg
        ref={svgRef}
        className="w-full"
        style={{ minHeight: "600px", background: "#fff" }}
      />
      {selectedNode && (
        <div className="p-4 bg-slate-50 border-t border-slate-200">
          <p className="text-sm text-slate-600">
            Selected node ID: {selectedNode}
          </p>
        </div>
      )}
    </div>
  );
}
