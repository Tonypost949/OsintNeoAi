#!/usr/bin/env python3
"""
arcgis_teams_card_generator.py — Turn GeoJSON targets into Microsoft Teams Adaptive Cards.

Reads arcgis_for_teams_geojson.geojson (or any GeoJSON with TargetID/Name/Severity
properties) and emits:
  * Individual card JSON per target  -> cards/  directory
  * A single combined cards bundle   -> arcgis_teams_cards_all.json
  * A CSV of target -> card mappings -> arcgis_teams_card_index.csv

Posting options:
  1. Power Automate: "HTTP" step posts the card JSON to an Incoming Webhook URL.
  2. Teams Incoming Webhook: POST to https://outlook.office.com/webhook/... with
     {"type":"message","attachments":[{"contentType":"application/vnd.microsoft.card.adaptive","contentUrl":null,"content": CARD}]}

Usage:
    python arcgis_teams_card_generator.py [path/to/targets.geojson] [--severity CRITICAL] [--webhook https://...]

Examples:
    python arcgis_teams_card_generator.py
    python arcgis_teams_card_generator.py --severity CRITICAL
    python arcgis_teams_card_generator.py --webhook https://outlook.office.com/webhook/xxx
"""
import argparse
import csv
import json
import os
import sys
import datetime
import urllib.request

DEFAULT_GEOJSON = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "arcgis_for_teams_geojson.geojson")
OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arcgis_teams_cards")
ARCGIS_MAP_URL = "https://www.arcgis.com/home/webmap/viewer.html"

SEVERITY_COLORS = {
    "CRITICAL": "Attention",
    "HIGH": "Attention",
    "MEDIUM": "Warning",
    "INFO": "Good",
    "Default": "Default",
}


def load_targets(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features", data if isinstance(data, list) else [])
    return features


def make_card(feature):
    p = feature.get("properties", {})
    geom = feature.get("geometry", {})
    if geom.get("type") == "Point" and "coordinates" in geom:
        lon, lat = geom["coordinates"][:2]
    else:
        lat = p.get("Latitude", 0)
        lon = p.get("Longitude", 0)
    sev = (p.get("Severity") or "INFO").upper()
    facts = [
        {"title": "Target ID:", "value": p.get("TargetID") or p.get("OBJECTID") or "N/A"},
        {"title": "Layer:", "value": p.get("Layer", "N/A")},
        {"title": "Severity:", "value": sev},
        {"title": "Coordinates:", "value": f"{lat}, {lon}"},
    ]
    if p.get("AmountUSD"):
        facts.append({"title": "Amount:", "value": f"${p['AmountUSD']:,}"})
    if p.get("Status"):
        facts.append({"title": "Status:", "value": p["Status"]})
    facts.append({"title": "Source:", "value": p.get("Source", "HBNC RICO evidence set")})
    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "fallbackText": f"ArcGIS Spatial Alert: {p.get('Name', 'Target')}",
        "body": [
            {"type": "TextBlock", "text": "ArcGIS Spatial Alert",
             "weight": "Bolder", "size": "Medium",
             "color": SEVERITY_COLORS.get(sev, "Default")},
            {"type": "TextBlock", "text": p.get("Name", "Unnamed target"),
             "weight": "Bolder", "wrap": True},
            {"type": "FactSet", "facts": facts},
            {"type": "TextBlock",
             "text": (p.get("Description") or "").replace("|", " | "),
             "wrap": True, "size": "Small", "isSubtle": True},
        ],
        "actions": [
            {"type": "Action.OpenUrl", "title": "Open in ArcGIS", "url": ARCGIS_MAP_URL},
        ],
        "context": {
            "generator": "arcgis_teams_card_generator.py",
            "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "target_id": p.get("TargetID"),
        },
    }
    return card


def teams_payload(card):
    return {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": None,
            "content": card,
        }],
    }


def write_payloads(cards, targets, outdir, severity_filter=None):
    os.makedirs(outdir, exist_ok=True)
    index = []
    for i, (feat, card) in enumerate(zip(targets, cards)):
        sev = (feat.get("properties", {}).get("Severity") or "INFO").upper()
        if severity_filter and sev != severity_filter.upper():
            continue
        fid = (feat.get("properties", {}).get("TargetID")
               or f"target_{i:03d}").replace("/", "_").replace(" ", "_")
        payload = teams_payload(card)
        with open(os.path.join(outdir, f"{fid}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        index.append({"id": fid, "severity": sev,
                      "file": f"{fid}.json",
                      "name": feat.get("properties", {}).get("Name")})
    combined = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "post_to_teams_as": "application/vnd.microsoft.card.adaptive",
        "cards": [teams_payload(c) for c in cards]
        if not severity_filter else
        [teams_payload(c) for feat, c in zip(targets, cards)
         if (feat.get("properties", {}).get("Severity") or "INFO").upper() == severity_filter.upper()],
    }
    with open(os.path.join(outdir, "arcgis_teams_cards_all.json"), "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)
    with open(os.path.join(outdir, "arcgis_teams_card_index.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target_id", "severity", "name", "card_file"])
        for row in index:
            w.writerow([row["id"], row["severity"], row["name"], row["file"]])
    return index


def post_webhook(webhook_url, payload):
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read().decode("utf-8", errors="replace")


def main():
    ap = argparse.ArgumentParser(description="Generate Teams Adaptive Cards from ArcGIS targets")
    ap.add_argument("geojson", nargs="?", default=DEFAULT_GEOJSON, help="GeoJSON input file")
    ap.add_argument("--severity", default=None, help="Only emit cards for this severity (CRITICAL/HIGH/...)")
    ap.add_argument("--webhook", default=None, help="Teams Incoming Webhook URL; posts all cards")
    ap.add_argument("--outdir", default=OUTDIR, help="Card output directory")
    args = ap.parse_args()

    if not os.path.exists(args.geojson):
        sys.exit(f"GeoJSON not found: {args.geojson}")
    targets = load_targets(args.geojson)
    cards = [make_card(f) for f in targets]
    print(f"Loaded {len(targets)} targets from {os.path.basename(args.geojson)}")

    index = write_payloads(cards, targets, args.outdir, args.severity)
    print(f"Wrote {len(index)} cards to {args.outdir}")

    if args.webhook:
        ok = 0
        for feat, card in zip(targets, cards):
            if args.severity and (feat.get("properties", {}).get("Severity") or "INFO").upper() != args.severity.upper():
                continue
            try:
                status, body = post_webhook(args.webhook, teams_payload(card))
                print(f"  posted {feat.get('properties', {}).get('TargetID')}: HTTP {status}")
                ok += 1
            except Exception as e:
                print(f"  FAILED {feat.get('properties', {}).get('TargetID')}: {e}")
        print(f"Posted {ok} cards")

    sample = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "arcgis_teams_adaptive_card_sample.json")
    with open(sample, "w", encoding="utf-8") as f:
        json.dump(cards[0], f, indent=2, ensure_ascii=False) if cards else None
    print(f"Sample card -> {sample}")


if __name__ == "__main__":
    main()