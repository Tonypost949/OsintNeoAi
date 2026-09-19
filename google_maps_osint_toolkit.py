"""
Google Maps Platform OSINT Intelligence Toolkit for OsintNeoAi
Source: Google Maps Platform Code Assist
"""

import os
import requests
import json

class GoogleMapsOsintToolkit:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")
        self.attribution_id = "gmp_git_agentskills_v1"

    def geocode_address(self, address):
        """Converts an address or landmark into latitude/longitude coordinates."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()

    def reverse_geocode(self, lat, lng):
        """Converts latitude/longitude coordinates into address information."""
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "latlng": f"{lat},{lng}",
            "key": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()

    def search_place_text(self, query_text):
        """Uses Places API (New) Text Search endpoint via server-side REST proxy."""
        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.rating,places.nationalPhoneNumber"
        }
        payload = {
            "textQuery": query_text
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

    def compute_route_matrix(self, origins, destinations):
        """Uses Routes API Distance Matrix REST endpoint."""
        url = "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "originIndex,destinationIndex,duration,distanceMeters,status"
        }
        payload = {
            "origins": [{"waypoint": {"location": {"latLng": {"latitude": o["lat"], "longitude": o["lng"]}}}} for o in origins],
            "destinations": [{"waypoint": {"location": {"latLng": {"latitude": d["lat"], "longitude": d["lng"]}}}} for d in destinations],
            "travelMode": "DRIVE"
        }
        response = requests.post(url, headers=headers, json=payload)
        return response.json()

if __name__ == "__main__":
    print("Google Maps OSINT Toolkit initialized successfully for OsintNeoAi.")
