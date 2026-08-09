#!/usr/bin/env python3
"""
City IP Geolocation Lookup System
Maps IP addresses to geographic city locations for OSINT investigations.

Supports:
- MaxMind GeoIP2 database (high accuracy)
- IP2Location database
- Batch IP processing and BigQuery storage
- Spatial mapping and clustering
"""

import os
import json
import requests
import geoip2.database
import pandas as pd
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BigQuery client
BQ_CLIENT = bigquery.Client()
PROJECT_ID = "project-743aab84-f9a5-4ec7-954"
DATASET_ID = "national_audits"
TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.ip_geolocation_index"

# Free IP geolocation APIs (no key required)
IP_APIS = {
    "ipstack": "http://api.ipstack.com/{ip}?access_key=",
    "ip2geo": "https://api.ip2geo.io/{ip}",
    "geolite": "https://geoip.nekudo.com/api/",
}

# MaxMind GeoLite2 database paths
GEOIP_DB_CITY = os.path.expanduser("~/.geoip/GeoLite2-City.mmdb")
GEOIP_DB_ASN = os.path.expanduser("~/.geoip/GeoLite2-ASN.mmdb")


class CityIPGeolocation:
    """IP to city geolocation lookup with batch processing."""

    def __init__(self):
        self.reader = None
        self.asn_reader = None
        self.initialize_geoip()

    def initialize_geoip(self):
        """Load MaxMind GeoLite2 database if available."""
        if os.path.exists(GEOIP_DB_CITY):
            try:
                self.reader = geoip2.database.Reader(GEOIP_DB_CITY)
                logger.info("✓ Loaded GeoLite2-City database")
            except Exception as e:
                logger.warning(f"Could not load GeoLite2 City DB: {e}")

        if os.path.exists(GEOIP_DB_ASN):
            try:
                self.asn_reader = geoip2.database.Reader(GEOIP_DB_ASN)
                logger.info("✓ Loaded GeoLite2-ASN database")
            except Exception as e:
                logger.warning(f"Could not load GeoLite2 ASN DB: {e}")

    def download_geolite2(self):
        """Download MaxMind GeoLite2 databases (requires free account)."""
        os.makedirs(os.path.dirname(GEOIP_DB_CITY), exist_ok=True)
        logger.info("To use MaxMind databases, download from:")
        logger.info("https://www.maxmind.com/en/geolite2/signup")
        logger.info(f"Extract to: {os.path.dirname(GEOIP_DB_CITY)}")

    def lookup_ip(self, ip_address: str) -> Dict:
        """
        Lookup single IP address using available methods.
        
        Returns geolocation data with fallback to free APIs.
        """
        # Try MaxMind first (most accurate)
        if self.reader:
            try:
                response = self.reader.city(ip_address)
                return {
                    "ip": ip_address,
                    "city": response.city.name,
                    "region": response.subdivisions[0].name if response.subdivisions else None,
                    "country": response.country.iso_code,
                    "latitude": response.location.latitude,
                    "longitude": response.location.longitude,
                    "timezone": response.location.time_zone,
                    "accuracy_radius": response.location.accuracy_radius,
                    "asn": None,
                    "source": "maxmind_geolite2",
                }
            except Exception as e:
                logger.debug(f"MaxMind lookup failed for {ip_address}: {e}")

        # Try ASN lookup
        asn_data = None
        if self.asn_reader:
            try:
                asn_response = self.asn_reader.asn(ip_address)
                asn_data = asn_response.autonomous_system_number
            except Exception:
                pass

        # Fallback to free API (IP2Geo)
        try:
            resp = requests.get(f"https://api.ip2geo.io/{ip_address}", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "ip": ip_address,
                    "city": data.get("city", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "country": data.get("country_code", "Unknown"),
                    "latitude": data.get("latitude", None),
                    "longitude": data.get("longitude", None),
                    "timezone": data.get("timezone", None),
                    "accuracy_radius": None,
                    "asn": asn_data,
                    "source": "ip2geo_api",
                }
        except Exception as e:
            logger.debug(f"IP2Geo API failed: {e}")

        return {
            "ip": ip_address,
            "city": "Unknown",
            "region": "Unknown",
            "country": "Unknown",
            "latitude": None,
            "longitude": None,
            "timezone": None,
            "accuracy_radius": None,
            "asn": asn_data,
            "source": "error",
        }

    def batch_lookup(self, ip_addresses: List[str], max_workers: int = 10) -> List[Dict]:
        """Batch lookup multiple IPs with concurrent requests."""
        logger.info(f"Starting batch lookup for {len(ip_addresses)} IPs...")
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.lookup_ip, ip): ip for ip in ip_addresses
            }

            for i, future in enumerate(as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                    if (i + 1) % 50 == 0:
                        logger.info(f"  Processed {i + 1}/{len(ip_addresses)} IPs")
                except Exception as e:
                    logger.error(f"Error processing IP: {e}")

        return results

    def upload_to_bigquery(self, results: List[Dict]):
        """Upload geolocation results to BigQuery."""
        if not results:
            logger.warning("No results to upload")
            return

        df = pd.DataFrame(results)
        logger.info(f"Uploading {len(df)} IP geolocation records to BigQuery...")

        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",
            schema_update_options=[bigquery.SchemaUpdateOptions.ALLOW_FIELD_ADDITION],
        )

        try:
            job = BQ_CLIENT.load_table_from_dataframe(df, TABLE_ID, job_config=job_config)
            job.result()
            logger.info(f"✓ Upload complete! Table: {TABLE_ID}")
        except Exception as e:
            logger.error(f"BigQuery upload failed: {e}")
            # Save locally as fallback
            output_file = "ip_geolocation_results.jsonl"
            with open(output_file, "w") as f:
                for record in results:
                    f.write(json.dumps(record) + "\n")
            logger.info(f"Saved to local file: {output_file}")

    def spatial_clustering(self, results: List[Dict]) -> Dict:
        """Cluster IPs by geographic proximity."""
        df = pd.DataFrame(results)
        df = df[(df["latitude"].notna()) & (df["longitude"].notna())]

        if df.empty:
            logger.warning("No geographic data available for clustering")
            return {}

        # Group by city
        clusters = df.groupby("city").agg({
            "ip": "count",
            "latitude": "mean",
            "longitude": "mean",
            "country": lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
        }).rename(columns={"ip": "count"}).reset_index()

        clusters = clusters.sort_values("count", ascending=False)
        logger.info(f"\nTop Cities by IP Count:")
        for idx, row in clusters.head(10).iterrows():
            logger.info(
                f"  {row['city']}, {row['country']}: {row['count']} IPs "
                f"({row['latitude']:.2f}, {row['longitude']:.2f})"
            )

        return clusters.to_dict("records")

    def export_geojson(self, results: List[Dict], output_file: str = "ip_geolocations.geojson"):
        """Export geolocation data as GeoJSON for mapping."""
        features = []
        
        for record in results:
            if record["latitude"] and record["longitude"]:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [record["longitude"], record["latitude"]],
                    },
                    "properties": {
                        "ip": record["ip"],
                        "city": record["city"],
                        "region": record["region"],
                        "country": record["country"],
                        "timezone": record["timezone"],
                        "asn": record["asn"],
                    },
                })

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }

        with open(output_file, "w") as f:
            json.dump(geojson, f, indent=2)

        logger.info(f"✓ GeoJSON exported: {output_file}")
        return output_file

    def query_city_ips(self, city_name: str, country_code: Optional[str] = None) -> List[Dict]:
        """Query IPs located in a specific city from BigQuery."""
        query = f"""
        SELECT ip, city, region, country, latitude, longitude, timezone, source
        FROM `{TABLE_ID}`
        WHERE LOWER(city) LIKE LOWER('%{city_name}%')
        """

        if country_code:
            query += f" AND country = '{country_code}'"

        query += " ORDER BY ip DESC LIMIT 1000"

        try:
            results = BQ_CLIENT.query(query).to_dataframe()
            logger.info(f"Found {len(results)} IPs in {city_name}")
            return results.to_dict("records")
        except Exception as e:
            logger.error(f"BigQuery query failed: {e}")
            return []


def main():
    """Example usage of City IP Geolocation system."""
    import argparse

    parser = argparse.ArgumentParser(description="City IP Geolocation Lookup")
    parser.add_argument("--ips", nargs="+", help="IP addresses to lookup")
    parser.add_argument("--file", help="File with IPs (one per line)")
    parser.add_argument("--city", help="Query IPs in specific city")
    parser.add_argument("--country", help="Filter by country code")
    parser.add_argument("--export-geojson", action="store_true", help="Export as GeoJSON")
    parser.add_argument("--cluster", action="store_true", help="Show geographic clusters")

    args = parser.parse_args()
    geo = CityIPGeolocation()

    # Load IPs
    ips = args.ips or []
    if args.file:
        with open(args.file) as f:
            ips.extend(line.strip() for line in f if line.strip())

    if ips:
        # Batch lookup
        results = geo.batch_lookup(ips)

        # Display results
        for result in results[:5]:
            logger.info(
                f"{result['ip']}: {result['city']}, {result['country']} "
                f"({result['latitude']}, {result['longitude']})"
            )

        # Upload to BigQuery
        geo.upload_to_bigquery(results)

        # Export GeoJSON
        if args.export_geojson:
            geo.export_geojson(results)

        # Show clusters
        if args.cluster:
            geo.spatial_clustering(results)

    # Query by city
    if args.city:
        city_results = geo.query_city_ips(args.city, args.country)
        logger.info(f"\n{len(city_results)} IPs found in {args.city}:")
        for record in city_results[:5]:
            logger.info(f"  {record}")


if __name__ == "__main__":
    main()
