# 🗺️ ArcGIS for Teams — Integration & Deployment Guide

**Project:** OSINT Neo AI / Makaveli Protocol  
**Case Reference:** CACD Case 8:2026cv00348  
**ArcGIS Platform:** Esri ArcGIS Online / ArcGIS Enterprise / ArcGIS for Microsoft Teams  

---

## 🚀 Overview

This integration package connects **OSINT Neo AI** spatial intelligence targets, environmental hazard nodes, municipal parcels, and entity relationship vectors directly into your **ArcGIS for Teams** account in Microsoft Teams.

It provides:
1. **Esri Feature Layer Collection (`arcgis_for_teams_feature_collection.json`)**: Pre-built Esri Web Map point & feature layer collection.
2. **GeoJSON Standard Dataset (`arcgis_for_teams_geojson.geojson`)**: Standard GeoJSON FeatureCollection formatted with APN, address, target type, severity, and case references.
3. **Microsoft Teams Adaptive Cards (`arcgis_teams_adaptive_card_sample.json`)**: Interactive alert cards designed to be posted directly into MS Teams channels via ArcGIS for Teams Bot or Webhook.
4. **ArcGIS for Teams Dashboard App (`arcgis_teams_dashboard.html`)**: High-aesthetic Web Application designed to be embedded directly as a Microsoft Teams Tab.

---

## 🛠️ Step 1: Import Spatial Layers into ArcGIS Online / Enterprise

1. Sign in to your **ArcGIS Online / Enterprise** account.
2. Navigate to **Content** → **Add Item** → **From Your Computer**.
3. Select [`arcgis_for_teams_geojson.geojson`](file:///C:/Users/HP/osintneoai/arcgis_for_teams_geojson.geojson) or [`arcgis_for_teams_feature_collection.json`](file:///C:/Users/HP/osintneoai/arcgis_for_teams_feature_collection.json).
4. Choose **Publish this file as a hosted feature layer**.
5. Give the item a title (e.g. `OSINT Neo AI Spatial Targets`) and click **Save & Publish**.
6. Save the newly published Hosted Feature Layer into a Web Map.

---

## 💬 Step 2: Add Map to Microsoft Teams via ArcGIS for Teams

1. Open **Microsoft Teams**.
2. Go to the desired Channel or Chat.
3. Click the **+ (Add a tab)** icon at the top of the channel.
4. Search for and select **ArcGIS**.
5. Select your published `OSINT Neo AI Spatial Targets` Web Map or paste the Web Map URL.
6. Click **Save**. The interactive map is now live for your team inside Microsoft Teams.

---

## 📑 Step 3: Embed the Dedicated Dashboard in Teams

To embed the custom interactive dashboard [`arcgis_teams_dashboard.html`](file:///C:/Users/HP/osintneoai/arcgis_teams_dashboard.html):
1. In Microsoft Teams, click **+ Add a tab**.
2. Select **Website** or **Custom App**.
3. Enter `ArcGIS Spatial Intel Hub` as the tab name.
4. Set the URL to your local server / GitHub Pages hosted [`arcgis_teams_dashboard.html`](file:///C:/Users/HP/osintneoai/arcgis_teams_dashboard.html).

---

## 🔔 Step 4: Send Adaptive Alert Cards to Teams Channels

Use [`arcgis_teams_card_generator.py`](file:///C:/Users/HP/osintneoai/arcgis_teams_card_generator.py) to generate Teams Adaptive Cards:

```bash
python C:\Users\HP\osintneoai\arcgis_teams_card_generator.py
```

Post the output JSON from [`arcgis_teams_adaptive_card_sample.json`](file:///C:/Users/HP/osintneoai/arcgis_teams_adaptive_card_sample.json) via an **Incoming Webhook** or **Power Automate flow** to send real-time target alert cards straight into your Teams channel!

---

*Makaveli Protocol | ArcGIS for Teams Deployment Package | August 2026*
