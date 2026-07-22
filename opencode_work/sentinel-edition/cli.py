#!/usr/bin/env python3
"""
Sentinel OSINT Engine - Command Line Interface
================================================
Standalone CLI for investigation workflows.
Usage: python cli.py <command> [options]

Commands:
  investigate <target>     Start investigation on a target
  ingest <path>            Ingest files/directories/documents
  search <query>           Search the investigation graph
  analyze                  Run network analysis
  report [output]          Generate investigation report
  export [format]          Export graph (json/gexf/geojson/html)
  timeline                 Show investigation timeline
  collect <source> <query> Run a data collector
  sources                  List available data sources
  stats                    Show graph statistics
  help                     Show this help
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import SentinelEngine
from collectors.web_collector import CollectorManager
from collectors.public_records import PublicRecordsAggregator
from analyzers.text_analyzer import TextAnalyzer
from exports.html_report import HTMLReportGenerator
from exports.geojson_export import GeoJSONExporter


def print_json(data):
    print(json.dumps(data, indent=2, default=str))


def cmd_investigate(engine, args):
    if not args:
        print("Usage: sentinel investigate <target>")
        return
    target = " ".join(args)
    result = engine.investigate(target)
    print(f"Investigation started for: {target}")
    print_json(result)


def cmd_ingest(engine, args):
    if not args:
        print("Usage: sentinel ingest <file_or_directory>")
        return
    source = args[0]
    print(f"Ingesting: {source}")
    result = engine.ingest(source)
    print_json(result)


def cmd_search(engine, args):
    if not args:
        print("Usage: sentinel search <query>")
        return
    query = " ".join(args)
    results = engine.search(query)
    print(f"Found {len(results)} matching entities:")
    print_json(results)


def cmd_analyze(engine, args):
    print("Running network analysis...")
    results = engine.analyze()
    print_json(results)


def cmd_report(engine, args):
    output = args[0] if args else None
    path = engine.report(output)
    print(f"Report saved to: {path}")


def cmd_export(engine, args):
    fmt = args[0] if args else "json"
    output = args[1] if len(args) > 1 else None
    path = engine.export_graph(fmt, output)
    print(f"Graph exported to: {path}")


def cmd_timeline(engine, args):
    events = engine.timeline_view()
    print(f"Timeline ({len(events)} events):")
    for e in events[-20:]:
        print(f"  {e.get('date', 'N/A')}: {e.get('entity', e.get('relationship', ''))} [{e.get('type', e.get('event', ''))}]")


def cmd_collect(engine, args):
    if len(args) < 2:
        print("Usage: sentinel collect <source> <query>")
        print("Sources: duckduckgo, wayback, crtsh, rdap, abuseipdb, shodan, nppes, sec_edgar, usaspending")
        return
    source, query = args[0], " ".join(args[1:])
    if source in ("nppes", "sec_edgar", "usaspending"):
        agg = PublicRecordsAggregator()
        collector = agg.collectors.get(source)
        if collector:
            if hasattr(collector, "search"):
                result = collector.search(query)
            else:
                result = collector.search_recipients(query)
        else:
            result = {"error": f"Unknown source: {source}"}
    else:
        mgr = CollectorManager()
        result = mgr.run(source, query)
    print_json(result)


def cmd_sources(engine, args):
    web = CollectorManager()
    public = PublicRecordsAggregator()
    print("=== Web Sources ===")
    for s in web.list_collectors():
        print(f"  {s['name']}: {s['description']}")
    print("\n=== Public Records Sources ===")
    for s in public.list_sources():
        key = " [API KEY]" if s["api_key_required"] else " [FREE]"
        print(f"  {s['name']}: {s['description']}{key}")


def cmd_stats(engine, args):
    stats = engine.graph.get_stats()
    print_json(stats)


def cmd_html_report(engine, args):
    output = args[0] if args else "sentinel_report.html"
    gen = HTMLReportGenerator()
    stats = engine.analyze()
    gen.add_stats(stats.get("graph_stats", {}))
    entities = [e.to_dict() for e in engine.graph.entities.values()]
    gen.add_entity_table(entities)
    relationships = [r.to_dict() for r in engine.graph.relationships.values()]
    entity_map = {e.id: e.value for e in engine.graph.entities.values()}
    gen.add_relationship_table(relationships, entity_map)
    gen.save(output)
    print(f"HTML report saved to: {output}")


def cmd_geojson(engine, args):
    output = args[0] if args else "sentinel_map.geojson"
    exporter = GeoJSONExporter()
    entities = [e.to_dict() for e in engine.graph.entities.values()]
    exporter.from_entities(entities)
    exporter.save(output)
    print(f"GeoJSON saved to: {output}")


COMMANDS = {
    "investigate": cmd_investigate,
    "ingest": cmd_ingest,
    "search": cmd_search,
    "analyze": cmd_analyze,
    "report": cmd_report,
    "export": cmd_export,
    "timeline": cmd_timeline,
    "collect": cmd_collect,
    "sources": cmd_sources,
    "stats": cmd_stats,
    "html": cmd_html_report,
    "geojson": cmd_geojson,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print(__doc__)
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    workspace = os.environ.get("SENTINEL_WORKSPACE", os.path.join(os.getcwd(), "sentinel-workspace"))
    engine = SentinelEngine(workspace)

    if cmd in COMMANDS:
        COMMANDS[cmd](engine, args)
    else:
        print(f"Unknown command: {cmd}")
        print(f"Available commands: {', '.join(COMMANDS.keys())}")


if __name__ == "__main__":
    main()
