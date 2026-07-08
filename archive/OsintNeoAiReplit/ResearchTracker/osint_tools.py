import os
import subprocess
import logging
import pandas as pd
import re
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import streamlit as st
from io import StringIO
import trafilatura

# Setup logging
logger = logging.getLogger("osint_tools")

class OSINTAnalyzer:
    """Class for OSINT analysis of properties and addresses."""
    
    def __init__(self, addresses: List[str], start_year: int = 1900, end_year: int = 2025):
        """Initialize the OSINT analyzer with addresses and time period."""
        self.addresses = addresses
        self.start_year = start_year
        self.end_year = end_year
        self.results = {}
        
        # Create results directory
        os.makedirs("osint_results", exist_ok=True)
    
    def scrape_newspaper_archives(self, address: str) -> List[Dict]:
        """
        Scrape newspaper archives for mentions of the address.
        
        Returns:
            List of dictionary entries with date, headline, and snippet.
        """
        logger.info(f"Scraping newspaper archives for {address}")
        
        # This would normally use real newspaper API or web scraping
        # For demonstration, we'll create realistic sample results
        
        results = []
        
        # Generate some realistic newspaper mentions
        if "17642 Beach" in address:
            results = [
                {
                    "date": "1912-05-15",
                    "source": "Huntington Beach News",
                    "headline": "New Artesian Well Improves Farm Output",
                    "snippet": "The McAllister farm at 17642 Beach Boulevard has reported increased crop yields following the installation of a new artesian well system reaching depths of 120 feet. Local farmers are taking notice of the innovative irrigation method."
                },
                {
                    "date": "1925-08-03",
                    "source": "Orange County Register",
                    "headline": "Produce Market Expansion",
                    "snippet": "The Huntington Produce Market on Beach Boulevard has expanded its operations to include a wider variety of local vegetables. Owner Thomas Henderson attributes success to relationships with local farms including the property at 17642 Beach."
                },
                {
                    "date": "1937-11-20",
                    "source": "Farm Weekly Gazette",
                    "headline": "Modern Irrigation Systems Transform Local Agriculture",
                    "snippet": "Several Huntington Beach farms have adopted electric pump systems for well irrigation. The property at 17642 Beach Blvd was among the first to install such a system in 1929 and has seen consistently higher yields as a result."
                }
            ]
        elif "17631 Cameron" in address:
            results = [
                {
                    "date": "1905-06-10",
                    "source": "Huntington Beach Chronicle",
                    "headline": "Cameron Family Establishes New Farm",
                    "snippet": "The Cameron family has established a new farming operation at 17631 Cameron Lane, focusing on potato and corn production. The family has invested in modern well-drilling equipment to ensure adequate irrigation."
                },
                {
                    "date": "1916-09-22",
                    "source": "Agricultural Times",
                    "headline": "Windmill Technology Improves Farm Output",
                    "snippet": "The Cameron farm on Cameron Lane has reported a 20% increase in crop yields after installing a windmill-powered pump system. Other local farmers are expressing interest in the technology."
                },
                {
                    "date": "1933-03-14",
                    "source": "County Business Journal",
                    "headline": "Local Farms Form Cooperative",
                    "snippet": "Six farms in the Huntington Beach area have joined to form the Huntington Agricultural Cooperative. The Henderson family farm at 17631 Cameron Lane (formerly Cameron Family Farm) is among the founding members."
                }
            ]
        
        return results
    
    def search_property_records(self, address: str) -> Dict:
        """
        Search property records for historical information.
        
        Returns:
            Dictionary of property record information.
        """
        logger.info(f"Searching property records for {address}")
        
        # This would normally connect to county records or databases
        # For demonstration, we'll create realistic sample results
        
        results = {}
        
        # Generate some realistic property records
        if "17642 Beach" in address:
            results = {
                "ownership_history": [
                    {"start_year": 1900, "end_year": 1920, "owner": "McAllister Family", "purchase_price": "$800"},
                    {"start_year": 1920, "end_year": 1935, "owner": "Henderson Agricultural Co.", "purchase_price": "$3,500"},
                    {"start_year": 1935, "end_year": 1950, "owner": "Western Farming Consortium", "purchase_price": "$7,200"}
                ],
                "land_use_changes": [
                    {"year": 1900, "classification": "Agricultural - General Farming"},
                    {"year": 1915, "classification": "Agricultural - Specialized Produce"},
                    {"year": 1930, "classification": "Agricultural/Commercial - Farm with Retail"}
                ],
                "building_permits": [
                    {"year": 1908, "description": "Well house construction", "value": "$120"},
                    {"year": 1917, "description": "Storage barn expansion", "value": "$350"},
                    {"year": 1929, "description": "Pump house and electrical wiring", "value": "$775"},
                    {"year": 1938, "description": "Flood damage repairs", "value": "$280"}
                ]
            }
        elif "17631 Cameron" in address:
            results = {
                "ownership_history": [
                    {"start_year": 1900, "end_year": 1925, "owner": "Cameron Family", "purchase_price": "$650"},
                    {"start_year": 1925, "end_year": 1945, "owner": "Henderson Family", "purchase_price": "$4,200"}
                ],
                "land_use_changes": [
                    {"year": 1900, "classification": "Agricultural - General Farming"},
                    {"year": 1916, "classification": "Agricultural - Farm Stand Added"},
                    {"year": 1933, "classification": "Agricultural Cooperative Member"}
                ],
                "building_permits": [
                    {"year": 1904, "description": "Initial well construction", "value": "$90"},
                    {"year": 1915, "description": "Windmill and pump installation", "value": "$215"},
                    {"year": 1925, "description": "Farm stand construction", "value": "$180"},
                    {"year": 1934, "description": "Storage facility expansion", "value": "$320"}
                ]
            }
        
        return results
    
    def find_historical_satellite_imagery(self, address: str) -> List[Dict]:
        """
        Find historical satellite/aerial imagery information.
        
        Returns:
            List of dictionaries with imagery metadata.
        """
        logger.info(f"Searching historical imagery for {address}")
        
        # This would normally connect to imagery archives or mapping services
        # For demonstration, we'll create realistic sample results
        
        results = []
        
        # Sample imagery metadata - in a real implementation, this might include 
        # actual image URLs or file paths to imagery from various years
        if "17642 Beach" in address or "17631 Cameron" in address:
            # These would be similar for nearby properties
            results = [
                {
                    "year": 1928,
                    "source": "County Surveyor Aerial Survey",
                    "resolution": "Low",
                    "description": "First aerial survey of the area showing agricultural parcels",
                    "notes": "Black and white photograph taken from aircraft"
                },
                {
                    "year": 1938,
                    "source": "USGS Historical Topographic Map",
                    "resolution": "Medium",
                    "description": "Post-flood survey showing affected areas",
                    "notes": "Property boundaries and major structures visible"
                },
                {
                    "year": 1947,
                    "source": "Department of Agriculture Crop Survey",
                    "resolution": "Medium",
                    "description": "Agricultural land use documentation",
                    "notes": "Crop types and irrigation systems visible"
                }
            ]
        
        return results
    
    def analyze_water_rights_history(self, address: str) -> Dict:
        """
        Analyze water rights and well records history.
        
        Returns:
            Dictionary of water rights information.
        """
        logger.info(f"Analyzing water rights for {address}")
        
        # This would normally connect to water district records
        # For demonstration, we'll create realistic sample results
        
        results = {}
        
        if "17642 Beach" in address:
            results = {
                "water_rights": [
                    {
                        "type": "Groundwater Well Permit",
                        "granted_date": "1908-03-20",
                        "description": "Initial well drilling rights",
                        "water_allocation": "15 gallons per minute",
                        "restrictions": "None noted"
                    },
                    {
                        "type": "Expanded Water Rights",
                        "granted_date": "1929-04-15",
                        "description": "Permission for deeper well and electric pump",
                        "water_allocation": "25 gallons per minute",
                        "restrictions": "Not to interfere with neighboring wells"
                    }
                ],
                "well_inspections": [
                    {"date": "1910-05-12", "inspector": "County Water Authority", "status": "Compliant"},
                    {"date": "1922-08-03", "inspector": "State Agricultural Dept", "status": "Compliant"},
                    {"date": "1930-06-18", "inspector": "County Water Authority", "status": "Compliant"},
                    {"date": "1939-09-27", "inspector": "State Water Resources Board", "status": "Compliant"}
                ],
                "historical_notes": "The property was noted for excellent water management practices and an early adopter of electric pumping technology in the county."
            }
        elif "17631 Cameron" in address:
            results = {
                "water_rights": [
                    {
                        "type": "Groundwater Well Permit",
                        "granted_date": "1904-05-10",
                        "description": "Initial well drilling rights",
                        "water_allocation": "12 gallons per minute",
                        "restrictions": "None noted"
                    },
                    {
                        "type": "Secondary Well Permit",
                        "granted_date": "1915-08-28",
                        "description": "Permission for windmill-powered secondary well",
                        "water_allocation": "14 gallons per minute",
                        "restrictions": "None noted"
                    },
                    {
                        "type": "Replacement Well Permit",
                        "granted_date": "1925-03-17",
                        "description": "Permission for deeper replacement well",
                        "water_allocation": "18 gallons per minute",
                        "restrictions": "Required to cap original well"
                    }
                ],
                "well_inspections": [
                    {"date": "1908-04-30", "inspector": "County Water Authority", "status": "Compliant"},
                    {"date": "1916-09-14", "inspector": "State Agricultural Dept", "status": "Compliant"},
                    {"date": "1926-05-22", "inspector": "County Water Authority", "status": "Compliant"},
                    {"date": "1935-07-08", "inspector": "State Water Resources Board", "status": "Minor Concerns", "notes": "Recommended improvements to water conservation practices"}
                ],
                "historical_notes": "The property's water infrastructure evolved from simple hand-pumped wells to windmill technology and finally to more modern systems by the late 1920s."
            }
        
        return results
    
    def search_web_archives(self, address: str) -> List[Dict]:
        """
        Search web archives for historical mentions of the address.
        
        Returns:
            List of dictionary entries with date, URL, and content snippet.
        """
        logger.info(f"Searching web archives for {address}")
        
        # For a real implementation, this would use services like the Wayback Machine API
        # or other web archive services. For now, we'll provide sample data.
        
        results = []
        
        # Simplified sample results to demonstrate the concept
        if "17642 Beach" in address:
            results = [
                {
                    "date": "2001-05-18",
                    "url": "http://orangecountyhistory.org/huntington_farms_1900_1950.html",
                    "title": "Huntington Beach Historical Farms (1900-1950)",
                    "snippet": "...Among the most notable early farms was the property at 17642 Beach Boulevard, which pioneered irrigation techniques that transformed local agriculture..."
                },
                {
                    "date": "2005-11-03",
                    "url": "http://huntingtonbeacharchives.org/historical_wells.html",
                    "title": "Water Resources in Early Huntington Beach Development",
                    "snippet": "...The 1908 artesian well at the Beach Boulevard farm (17642) was among the first in the region to demonstrate the viability of deep-well irrigation for intensive vegetable farming..."
                }
            ]
        elif "17631 Cameron" in address:
            results = [
                {
                    "date": "2003-07-22",
                    "url": "http://orangecountyhistory.org/cameron_family_farms.html",
                    "title": "Cameron Family Agricultural Legacy",
                    "snippet": "...The original Cameron family homestead at 17631 Cameron Lane operated from 1900 until 1925, when ownership transferred to the Henderson family..."
                },
                {
                    "date": "2008-04-15",
                    "url": "http://huntingtonbeacharchives.org/agricultural_coops_1930s.html",
                    "title": "Depression-Era Agricultural Cooperatives in Orange County",
                    "snippet": "...The Henderson farm at the former Cameron property (17631 Cameron Lane) was instrumental in forming one of the most successful local farming cooperatives in 1933..."
                }
            ]
        
        return results
        
    def analyze_address(self, address: str) -> Dict:
        """
        Run all analysis methods for a single address.
        
        Returns:
            Dictionary containing all OSINT findings.
        """
        logger.info(f"Running full OSINT analysis for {address}")
        
        findings = {
            "address": address,
            "newspaper_archives": self.scrape_newspaper_archives(address),
            "property_records": self.search_property_records(address),
            "historical_imagery": self.find_historical_satellite_imagery(address),
            "water_rights_history": self.analyze_water_rights_history(address),
            "web_archives": self.search_web_archives(address),
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Store results for this address
        self.results[address] = findings
        
        return findings
    
    def analyze_all_addresses(self) -> Dict:
        """
        Run OSINT analysis on all addresses.
        
        Returns:
            Dictionary mapping each address to its findings.
        """
        for address in self.addresses:
            self.analyze_address(address)
        
        return self.results
    
    def generate_relationship_analysis(self) -> Dict:
        """
        Analyze potential relationships between different properties.
        
        Returns:
            Dictionary of relationship findings.
        """
        if len(self.addresses) < 2:
            return {"error": "Relationship analysis requires at least 2 addresses"}
        
        # Ensure we have results for all addresses
        for address in self.addresses:
            if address not in self.results:
                self.analyze_address(address)
        
        # Analyze potential connections between properties
        connections = []
        
        # This is a demonstration of the concept - in a real application, this would
        # involve more sophisticated analysis of the gathered data
        
        # Look for common owners
        all_owners = {}
        for address, findings in self.results.items():
            if "property_records" in findings and "ownership_history" in findings["property_records"]:
                for ownership in findings["property_records"]["ownership_history"]:
                    owner = ownership["owner"]
                    if owner not in all_owners:
                        all_owners[owner] = []
                    all_owners[owner].append({
                        "address": address,
                        "period": f"{ownership['start_year']}-{ownership['end_year']}"
                    })
        
        # Find owners with multiple properties
        for owner, properties in all_owners.items():
            if len(properties) > 1:
                connections.append({
                    "type": "Common Owner",
                    "details": owner,
                    "properties": properties
                })
        
        # Look for other types of connections (chronological succession, geographical proximity, etc.)
        # This would be expanded in a real implementation
        
        return {
            "connections": connections,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_web_content(self, url: str) -> str:
        """
        Retrieve and extract main text content from a webpage.
        Uses trafilatura for better text extraction.
        
        Args:
            url: The URL to scrape
            
        Returns:
            Extracted main text content
        """
        try:
            # Download the webpage
            downloaded = trafilatura.fetch_url(url)
            # Extract the main text content
            text = trafilatura.extract(downloaded)
            return text or "No content could be extracted from this page."
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return f"Error retrieving content: {str(e)}"
    
    def export_results(self, format_type: str = "json") -> str:
        """
        Export analysis results to a file.
        
        Args:
            format_type: "json" or "csv"
            
        Returns:
            Path to the exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type.lower() == "json":
            filename = f"osint_results/property_osint_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            return filename
        
        elif format_type.lower() == "csv":
            # For CSV, we'll create multiple files for different data types
            base_filename = f"osint_results/property_osint_{timestamp}"
            files = {}
            
            # Export newspaper archives
            newspaper_data = []
            for address, findings in self.results.items():
                for item in findings.get("newspaper_archives", []):
                    item["address"] = address
                    newspaper_data.append(item)
            
            if newspaper_data:
                df = pd.DataFrame(newspaper_data)
                csv_file = f"{base_filename}_newspapers.csv"
                df.to_csv(csv_file, index=False)
                files["newspapers"] = csv_file
            
            # Similar exports for other data types would be added here
            
            return files