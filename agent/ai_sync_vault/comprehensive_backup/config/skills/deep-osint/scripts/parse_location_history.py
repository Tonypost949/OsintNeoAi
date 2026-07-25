import os
import sys
import json
import re
from dateutil import parser as date_parser

# Add current workspace directory to import path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_timeline import prepare_ics_file, append_to_ics_file, seal_calendar_file

def parse_location_history_file(json_file_path, output_ics="master_incident_timeline.ics"):
    """
    Parses a single Google Takeout Semantic Location History JSON file,
    extracts GPS coordinates, builds Google Maps links, and appends them to the calendar.
    """
    if not os.path.exists(json_file_path):
        print(f"Error: File not found at {json_file_path}")
        return False

    print(f"Reading location history from {json_file_path}...")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON file: {e}")
        return False

    timeline_objects = data.get("timelineObjects", [])
    events_added = 0

    for obj in timeline_objects:
        # Scenario A: Place Visits (e.g., Coffee Shop, Office)
        if "placeVisit" in obj:
            visit = obj["placeVisit"]
            location = visit.get("location", {})
            duration = visit.get("duration", {})
            
            name = location.get("name", "Unknown Place")
            address = location.get("address", "").replace('\n', ', ')
            start_time = duration.get("startTimestamp")
            end_time = duration.get("endTimestamp")
            place_id = location.get("placeId", "")
            
            # Extract coordinates
            lat = location.get("latitudeE7", 0) / 10000000.0
            lng = location.get("longitudeE7", 0) / 10000000.0
            
            if not start_time:
                continue

            # Build Google Maps Location Link
            if lat != 0 or lng != 0:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"
                if place_id:
                    maps_url += f"&query_place_id={place_id}"
            elif address:
                encoded_addr = re.sub(r'\s+', '+', address)
                maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_addr}"
            else:
                maps_url = "https://www.google.com/maps"

            summary = f"Visited: {name}"
            details = f"Address: {address}\nPlace ID: {place_id if place_id else 'N/A'}\n\nMap Link: {maps_url}"
            
            success = append_to_ics_file(
                filename=output_ics,
                summary=summary,
                start_time_str=start_time,
                description=details,
                end_time_str=end_time,
                source_url=maps_url
            )
            if success:
                events_added += 1

        # Scenario B: Activity Segments (e.g., WALKING)
        elif "activitySegment" in obj:
            segment = obj["activitySegment"]
            duration = segment.get("duration", {})
            start_time = duration.get("startTimestamp")
            end_time = duration.get("endTimestamp")
            activity_type = segment.get("activityType", "UNKNOWN_ACTIVITY")
            distance = segment.get("distance", 0)  # in meters
            
            # We filter for WALKING activities
            if activity_type == "WALKING" and start_time:
                # Extract starting and ending coordinates
                start_loc = segment.get("startLocation", {})
                end_loc = segment.get("endLocation", {})
                
                start_lat = start_loc.get("latitudeE7", 0) / 10000000.0
                start_lng = start_loc.get("longitudeE7", 0) / 10000000.0
                end_lat = end_loc.get("latitudeE7", 0) / 10000000.0
                end_lng = end_loc.get("longitudeE7", 0) / 10000000.0
                
                # Build Google Maps Walking Directions Link
                if start_lat != 0 and end_lat != 0:
                    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={start_lat},{start_lng}&destination={end_lat},{end_lng}&travelmode=walking"
                else:
                    maps_url = "https://www.google.com/maps"

                summary = f"Walked: {distance}m" if distance > 0 else "Walking Activity"
                details = f"Activity Segment: Walking\nDistance covered: {distance} meters.\n\nMap Route: {maps_url}"
                
                success = append_to_ics_file(
                    filename=output_ics,
                    summary=summary,
                    start_time_str=start_time,
                    description=details,
                    end_time_str=end_time,
                    source_url=maps_url
                )
                if success:
                    events_added += 1

    print(f"Successfully processed {events_added} location objects into {output_ics}.")
    return True

def parse_directory(directory_path, output_ics="master_incident_timeline.ics"):
    """Recursively processes all JSON files in a Google Takeout Location History folder."""
    if not os.path.isdir(directory_path):
        print(f"Error: Directory not found at {directory_path}")
        return
        
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                full_path = os.path.join(root, file)
                parse_location_history_file(full_path, output_ics)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python parse_location_history.py <path_to_json_file>")
        print("  python parse_location_history.py <path_to_takeout_directory>")
        sys.exit(1)
        
    path_arg = sys.argv[1]
    output_file = "master_incident_timeline.ics"
    
    prepare_ics_file(output_file)
    if os.path.isdir(path_arg):
        parse_directory(path_arg, output_file)
    else:
        parse_location_history_file(path_arg, output_file)
    seal_calendar_file(output_file)
