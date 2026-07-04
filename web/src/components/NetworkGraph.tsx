import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { InvestigationData } from '../data/dossier';

interface NetworkGraphProps {
  data: InvestigationData;
  onNodeClick?: (nodeId: string) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ data, onNodeClick }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = 800;
    const height = 600;

    const svg = d3.select(svgRef.current)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('width', '100%')
      .attr('height', '100%');

    svg.selectAll('*').remove();

    const simulation = d3.forceSimulation(data.entities as any)
      .force('link', d3.forceLink(data.connections).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.append('g')
      .selectAll('line')
      .data(data.connections)
      .enter()
      .append('line')
      .attr('stroke', '#00FF41')
      .attr('stroke-width', 2)
      .attr('stroke-opacity', 0.4);

    const node = svg.append('g')
      .selectAll('g')
      .data(data.entities as any[])
      .enter()
      .append('g')
      .attr('cursor', 'pointer')
      .on('click', (event, d: any) => onNodeClick?.(d.id))
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    node.append('rect')
      .attr('width', 12)
      .attr('height', 12)
      .attr('x', -6)
      .attr('y', -6)
      .attr('fill', (d: any) => {
        switch (d.type) {
          case 'PERSON': return '#00FF41';
          case 'ORGANIZATION': return '#003310';
          case 'LOCATION': return '#ef4444';
          case 'TECHNOLOGY': return '#a855f7';
          default: return '#00FF41';
        }
      })
      .attr('stroke', '#00FF41')
      .attr('stroke-width', 1);

    node.append('text')
      .text((d: any) => d.name)
      .attr('x', 14)
      .attr('y', 4)
      .attr('font-size', '12px')
      .attr('fill', '#00FF41')
      .attr('font-weight', 'bold')
      .attr('font-family', 'ui-monospace, monospace')
      .attr('text-transform', 'uppercase');

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('transform', (d: any) => `translate(${d.x}, ${d.y})`);
    });

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [data, onNodeClick]);

  return (
    <div className="w-full h-full bg-black border-2 border-[#00FF41]/20 overflow-hidden">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
};
