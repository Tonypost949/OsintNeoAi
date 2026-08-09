"""
arcgis_teams_card_generator.py — Adaptive Card Generator for ArcGIS for Teams
Generates Microsoft Teams Adaptive Cards for sharing spatial intelligence target alerts
directly inside Microsoft Teams channels, chats, and ArcGIS for Teams apps.
"""

import json
import os

def create_teams_adaptive_card(target_id, name, category, severity, address, apn, description, lat, lng, case_ref):
    """Creates a Microsoft Teams Adaptive Card v1.4 JSON object."""
    
    # Severity color badge
    color_map = {
        "CRITICAL": "Attention",
        "HIGH": "Warning",
        "MEDIUM": "Accent",
        "INFO": "Good"
    }
    card_color = color_map.get(severity.upper(), "Default")

    arcgis_online_map_url = f"https://www.arcgis.com/home/webmap/viewer.html?center={lng},{lat}&level=17"
    local_recon_map_url = "https://github.com/Tonypost949/OsintNeoAi/blob/main/hbnc_rico_gis.html"

    card = {
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "type": "AdaptiveCard",
        "version": "1.4",
        "body": [
            {
                "type": "Container",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"🗺️ ArcGIS Spatial Intel Alert — {name}",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": card_color
                    },
                    {
                        "type": "TextBlock",
                        "text": f"OSINT Neo AI / Makaveli Spatial Target | Case Ref: {case_ref}",
                        "isSubtle": True,
                        "spacing": "None"
                    }
                ]
            },
            {
                "type": "FactSet",
                "facts": [
                    {"title": "Target ID:", "value": target_id},
                    {"title": "Category:", "value": category},
                    {"title": "Severity:", "value": severity},
                    {"title": "APN:", "value": apn},
                    {"title": "Address:", "value": address},
                    {"title": "Coordinates:", "value": f"{lat:.4f}, {lng:.4f}"}
                ]
            },
            {
                "type": "TextBlock",
                "text": description,
                "wrap": True,
                "spacing": "Small"
            }
        ],
        "actions": [
            {
                "type": "Action.OpenUrl",
                "title": "🌐 Open in ArcGIS Web Map",
                "url": arcgis_online_map_url
            },
            {
                "type": "Action.OpenUrl",
                "title": "📍 View Interactive Recon GIS Map",
                "url": local_recon_map_url
            }
        ]
    }
    return card

def generate_sample_cards_package(output_path):
    """Generates sample Adaptive Cards for the top spatial targets."""
    sample_targets = [
        {
            "target_id": "TOX-001",
            "name": "HBNC Toxic Site",
            "category": "Toxic Contaminated Plume",
            "severity": "CRITICAL",
            "address": "17642 Beach Blvd / 17631 Cameron Ln, Huntington Beach, CA",
            "apn": "102-451-09",
            "description": "Hexavalent Chromium (Cr-VI) 980 µg/kg (49x RSL). Asphalt cap failing over 2,247 cu ft HDPE Stormtech chambers. $155M COC liability.",
            "lat": 33.6775,
            "lng": -118.0012,
            "case_ref": "8:26-cv-00348"
        },
        {
            "target_id": "TOX-003",
            "name": "7561 Center Ave Vaults",
            "category": "Underground Vault / Shell Routing",
            "severity": "CRITICAL",
            "address": "7561 Center Ave, Units D1-E1-G3-J1, Huntington Beach, CA",
            "apn": "107-120-14",
            "description": "Underground concrete coffins (1960s-70s). 4 shell LLCs. Chen-Yamada pipeline routing $1.47M PPP funds.",
            "lat": 33.6927,
            "lng": -117.9974,
            "case_ref": "8:26-cv-00348"
        }
    ]

    cards_output = []
    for t in sample_targets:
        card = create_teams_adaptive_card(**t)
        cards_output.append(card)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cards_output, f, indent=2)

    print(f"[+] Successfully generated Microsoft Teams Adaptive Cards package: {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(base_dir, "arcgis_teams_adaptive_card_sample.json")
    generate_sample_cards_package(out_file)
