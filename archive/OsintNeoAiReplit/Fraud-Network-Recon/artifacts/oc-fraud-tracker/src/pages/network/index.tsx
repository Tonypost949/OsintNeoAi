import { useEffect, useRef, useState, useMemo, useCallback } from "react";
import ForceGraph2D from "react-force-graph-2d";
import { ACTORS, ENTITIES, MONEY_FLOWS, Actor, Entity } from "@/data/caseData";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, Printer, Filter } from "lucide-react";
import { useTheme } from "next-themes";

const NODE_COLORS: Record<string, string> = {
  person: "#3b82f6", // blue
  nonprofit: "#22c55e", // green
  shell_company: "#ef4444", // red
  government: "#a855f7", // purple
  church: "#f59e0b", // amber
  restaurant: "#f97316", // orange
  real_estate: "#14b8a6", // teal
  other: "#6b7280", // gray
};

type GraphNode = {
  id: string;
  name: string;
  group: string;
  role?: string;
  val: number;
  data: any;
};

type GraphLink = {
  source: string;
  target: string;
  label?: string;
  amount?: string;
  type: "connection" | "money";
};

export default function NetworkPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [filter, setFilter] = useState<"all" | "persons" | "organizations">("all");

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };
    window.addEventListener("resize", updateDimensions);
    updateDimensions();
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const graphData = useMemo(() => {
    const nodesMap = new Map<string, GraphNode>();
    const links: GraphLink[] = [];

    ACTORS.forEach((a) => {
      nodesMap.set(a.id, {
        id: a.id,
        name: a.name,
        group: "person",
        role: a.role,
        val: 1,
        data: a,
      });
    });

    ENTITIES.forEach((e) => {
      nodesMap.set(e.id, {
        id: e.id,
        name: e.name,
        group: e.type,
        role: e.role,
        val: 1,
        data: e,
      });
    });

    ACTORS.forEach((a) => {
      a.connections?.forEach((targetId) => {
        if (nodesMap.has(targetId)) {
          links.push({
            source: a.id,
            target: targetId,
            type: "connection",
          });
        }
      });
    });

    MONEY_FLOWS.forEach((m) => {
      const fromId = m.from.toLowerCase().replace(/\s+/g, "-");
      const toId = m.to.toLowerCase().replace(/\s+/g, "-");
      
      let sourceId = nodesMap.has(m.from) ? m.from : (nodesMap.has(fromId) ? fromId : null);
      let targetId = nodesMap.has(m.to) ? m.to : (nodesMap.has(toId) ? toId : null);

      if (!sourceId && m.from) {
        sourceId = fromId;
        nodesMap.set(sourceId, {
          id: sourceId,
          name: m.from,
          group: "other",
          val: 1,
          data: { name: m.from, type: "other" },
        });
      }

      if (!targetId && m.to) {
        targetId = toId;
        nodesMap.set(targetId, {
          id: targetId,
          name: m.to,
          group: "other",
          val: 1,
          data: { name: m.to, type: "other" },
        });
      }

      if (sourceId && targetId) {
        links.push({
          source: sourceId,
          target: targetId,
          amount: m.amount,
          label: m.description,
          type: "money",
        });
      }
    });

    links.forEach((link) => {
      const sourceNode = nodesMap.get(link.source as string);
      const targetNode = nodesMap.get(link.target as string);
      if (sourceNode) sourceNode.val += 1;
      if (targetNode) targetNode.val += 1;
    });

    let filteredNodes = Array.from(nodesMap.values());
    if (filter === "persons") {
      filteredNodes = filteredNodes.filter((n) => n.group === "person");
    } else if (filter === "organizations") {
      filteredNodes = filteredNodes.filter((n) => n.group !== "person");
    }

    const filteredNodeIds = new Set(filteredNodes.map((n) => n.id));
    const filteredLinks = links.filter(
      (l) => filteredNodeIds.has(l.source as string) && filteredNodeIds.has(l.target as string)
    );

    return {
      nodes: filteredNodes,
      links: filteredLinks,
    };
  }, [filter]);

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node);
  }, []);

  const handleExport = () => {
    window.print();
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      <div className="p-4 flex items-center justify-between border-b border-slate-800 bg-slate-900/50 backdrop-blur z-10 text-white">
        <div>
          <h1 className="text-2xl font-serif font-bold">Entity Network</h1>
          <p className="text-sm text-slate-400">
            {graphData.nodes.length} nodes, {graphData.links.length} relationships
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 bg-slate-800 rounded-md p-1 border border-slate-700">
            <Filter size={16} className="text-slate-400 ml-2" />
            <select
              className="bg-transparent text-sm text-white focus:outline-none py-1 pr-2"
              value={filter}
              onChange={(e) => setFilter(e.target.value as any)}
            >
              <option value="all">All Entities</option>
              <option value="persons">Persons Only</option>
              <option value="organizations">Organizations Only</option>
            </select>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport} className="text-white border-slate-700 hover:bg-slate-800 hover:text-white">
            <Printer size={16} className="mr-2" />
            Export
          </Button>
        </div>
      </div>

      <div className="flex-1 relative flex" ref={containerRef}>
        <ForceGraph2D
          width={dimensions.width}
          height={dimensions.height}
          graphData={graphData}
          nodeLabel={(node: any) => `${node.name} ${node.role ? `\n${node.role}` : ''}`}
          nodeColor={(node: any) => NODE_COLORS[node.group] || NODE_COLORS.other}
          nodeRelSize={4}
          linkDirectionalArrowLength={3.5}
          linkDirectionalArrowRelPos={1}
          linkColor={(link: any) => (link.type === "money" ? "rgba(34, 197, 94, 0.4)" : "rgba(148, 163, 184, 0.2)")}
          linkWidth={(link: any) => (link.type === "money" ? 2 : 1)}
          onNodeClick={handleNodeClick}
          backgroundColor="#0f172a"
        />

        {/* Detail Panel */}
        {selectedNode && (
          <Card className="absolute top-4 right-4 w-80 max-h-[calc(100%-2rem)] overflow-y-auto shadow-2xl border-slate-700 bg-slate-800/95 backdrop-blur text-white">
            <CardHeader className="relative pb-2 border-b border-slate-700">
              <button
                onClick={() => setSelectedNode(null)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white"
              >
                <X size={20} />
              </button>
              <Badge
                style={{ backgroundColor: NODE_COLORS[selectedNode.group] || NODE_COLORS.other }}
                className="w-max mb-2 uppercase text-[10px] tracking-wider text-white border-transparent"
              >
                {selectedNode.group.replace("_", " ")}
              </Badge>
              <CardTitle className="text-xl font-serif text-white">{selectedNode.name}</CardTitle>
              {selectedNode.role && <p className="text-sm text-slate-300 mt-1">{selectedNode.role}</p>}
            </CardHeader>
            <CardContent className="pt-4 space-y-4 text-sm">
              {selectedNode.data.status && (
                <div>
                  <h4 className="font-semibold text-slate-400 uppercase text-xs mb-1">Legal Status</h4>
                  <p className="text-slate-200">{selectedNode.data.statusDetail}</p>
                </div>
              )}
              {selectedNode.data.crimes && selectedNode.data.crimes.length > 0 && (
                <div>
                  <h4 className="font-semibold text-slate-400 uppercase text-xs mb-1">Allegations / Crimes</h4>
                  <ul className="list-disc pl-4 text-slate-200 space-y-1">
                    {selectedNode.data.crimes.map((crime: string, idx: number) => (
                      <li key={idx}>{crime}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedNode.data.fundsReceived && (
                <div>
                  <h4 className="font-semibold text-slate-400 uppercase text-xs mb-1">Funds Received</h4>
                  <p className="text-green-400 font-mono font-medium">{selectedNode.data.fundsReceived}</p>
                </div>
              )}
              {selectedNode.data.notes && (
                <div>
                  <h4 className="font-semibold text-slate-400 uppercase text-xs mb-1">Notes</h4>
                  <p className="text-slate-200">{selectedNode.data.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-slate-800/90 backdrop-blur border border-slate-700 p-4 rounded-lg shadow-lg">
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Node Types</h4>
          <div className="grid grid-cols-2 gap-x-4 gap-y-2">
            {Object.entries(NODE_COLORS).map(([type, color]) => (
              <div key={type} className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs text-slate-300 capitalize">{type.replace("_", " ")}</span>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-700">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Edge Types</h4>
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <div className="w-4 h-0.5 bg-slate-400/50" />
                <span className="text-xs text-slate-300">Connection</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 bg-green-500/50" />
                <span className="text-xs text-slate-300">Money Flow</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
