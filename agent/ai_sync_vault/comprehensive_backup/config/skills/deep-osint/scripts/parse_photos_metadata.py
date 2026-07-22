import os
import sys
import json
import re
import datetime
from dateutil import parser as date_parser

# Add current workspace directory to import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_timeline import prepare_ics_file, append_to_ics_file, seal_calendar_file

def parse_photo_metadata_file(json_file_path, output_ics="master_incident_timeline.ics"):
    """
    Parses a single Google Takeout Google Photos metadata JSON file,
    extracts GPS coordinates, capture time, and appends the photo to the calendar.
    """
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return False

    print(f"Reading photo metadata from {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON file: {e}")
        return False

    # Check if this is a Google Photos Takeout metadata JSON
    if "photoTakenTime" not in data or "geoData" not in data:
        print(f"Skipping: {json_file_path} (does not contain Google Photos metadata keys)")
        return False

    geo = data.get("geoData", {})
    lat = geo.get("latitude", 0.0)
    lng = geo.get("longitude", 0.0)
    
    # If no valid coordinates in geoData, check geoDataExif
    if lat == 0.0 and lng == 0.0:
        geo_exif = data.get("geoDataExif", {})
        lat = geo_exif.get("latitude", 0.0)
        lng = geo_exif.get("longitude", 0.0)

    taken_time_data = data.get("photoTakenTime", {})
    timestamp_val = taken_time_data.get("timestamp")
    formatted_val = taken_time_data.get("formatted")

    start_time = None
    if timestamp_val:
        try:
            # Convert Unix epoch timestamp to ISO-like format
            start_time = datetime.datetime.fromtimestamp(int(timestamp_val), tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass
            
    if not start_time and formatted_val:
        try:
            start_time = date_parser.parse(formatted_val).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

    if not start_time:
        print(f"Warning: Could not parse photo taken time from {json_file_path}")
        return False

    title = data.get("title", "Untitled Photo")
    description = data.get("description", "")
    
    # Format details
    details = f"📸 Photo: {title}\n"
    if description:
        details += f"Description: {description}\n"
    details += f"Coordinates: {lat}, {lng}"

    # Build maps link if coordinates are valid
    maps_url = ""
    if lat != 0.0 or lng != 0.0:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
        details += f"\n\nMap Link: {maps_url}"
    else:
        maps_url = "https://photos.google.com/"

    success = append_to_ics_file(
        filename=output_ics,
        summary=f"Photo: {title}",
        start_time_str=start_time,
        description=details,
        end_time_str=start_time, # Single moment event
        source_url=maps_url
    )
    
    if success:
        print(f" -> Successfully appended photo '{title}' to {output_ics}.")
        return True
    return False

def parse_directory(directory_path, output_ics="master_incident_timeline.ics"):
    """Recursively processes all JSON files in a Google Photos directory."""
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return
        
    count = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Takeout metadata files usually end in .jpg.json, .png.json, etc.
            if file.endswith('.json') and not file.endswith('metadata.json'):
                full_path = os.path.join(root, file)
                if parse_photo_metadata_file(full_path, output_ics):
                    count += 1
    print(f"Processed {count} photo metadata files.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parse_photos_metadata.py <path_to_photo_json_file>")
        print("  python parse_photos_metadata.py <path_to_takeout_photos_directory>")
        sys.exit(1)
        
    path_arg = sys.argv[1]
    output_file = "master_incident_timeline.ics"
    
    prepare_ics_file(output_file)
    if os.path.isdir(path_arg):
        parse_directory(path_arg, output_file)
    else:
        parse_photo_metadata_file(path_arg, output_file)
    seal_calendar_file(output_file)
