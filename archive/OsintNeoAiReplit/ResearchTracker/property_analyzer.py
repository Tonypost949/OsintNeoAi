import os
import logging
from typing import List, Dict, Any, Optional
import json
import csv
from datetime import datetime

# Base directory for saving results
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PropertySearcher:
    """Class to search property data from various sources."""
    
    def __init__(self, address: str, start_year: int, end_year: int):
        """Initialize with property address and time period."""
        self.address = address
        self.start_year = start_year
        self.end_year = end_year
        self.logger = logging.getLogger("property_searcher")
        
    def search_all_sources(self) -> Dict[str, Any]:
        """Search all available data sources for the property."""
        self.logger.info(f"Searching all sources for {self.address} ({self.start_year}-{self.end_year})")
        
        # In a real application, this would call various APIs and data sources
        # For now, we'll generate synthetic but realistic data based on the address and time period
        
        # Parse the address for location information
        address_parts = self.address.split()
        
        # Extract any available location info for contextual data generation
        city = None
        state = None
        
        for i, part in enumerate(address_parts):
            # Look for potential state abbreviations
            if len(part) == 2 and part.isupper() and i > 0:
                state = part
                # Check if previous part might be city
                if i > 0:
                    city = address_parts[i-1]
        
        # Generate findings based on time period and location
        findings = {
            "address": self.address,
            "search_period": f"{self.start_year}-{self.end_year}",
            "findings": self._generate_historical_data(city, state)
        }
        
        return findings
    
    def _generate_historical_data(self, city: Optional[str], state: Optional[str]) -> Dict[str, Any]:
        """Generate historical data based on address components and time period."""
        # This is a placeholder for actual data retrieval
        # In a production app, this would connect to real historical databases
        
        # Create realistic sample data for demonstration purposes
        data = {
            "agricultural_data": [],
            "commercial_usage": [],
            "historical_events": [],
            "value_history": [],
            "water_wells": []  # Added water wells data structure
        }
        
        # Generate data based on specific addresses for demonstration
        if "17642 Beach" in self.address:
            # Agricultural data
            data["agricultural_data"] = [
                {
                    "time_period": "1900-1915",
                    "crop_type": "Beans, Cabbage",
                    "acreage": 25,
                    "soil_type": "Loamy Sand",
                    "irrigation": "Well-based",
                    "annual_yield": "750 bushels"
                },
                {
                    "time_period": "1916-1925",
                    "crop_type": "Lima Beans, Celery",
                    "acreage": 30,
                    "soil_type": "Loamy Sand",
                    "irrigation": "Well-based",
                    "annual_yield": "900 bushels"
                },
                {
                    "time_period": "1926-1940",
                    "crop_type": "Celery, Cabbage, Strawberries",
                    "acreage": 35,
                    "soil_type": "Loamy Sand",
                    "irrigation": "Well-based with pump system",
                    "annual_yield": "1200 bushels"
                }
            ]
            
            # Commercial usage
            data["commercial_usage"] = [
                {
                    "time_period": "1900-1910",
                    "business_name": "Beach Blvd General Store",
                    "business_type": "General Store",
                    "commercial_activity": "Selling farm supplies and groceries",
                    "employees": 3
                },
                {
                    "time_period": "1911-1925",
                    "business_name": "Huntington Produce Market",
                    "business_type": "Farmers Market",
                    "commercial_activity": "Selling locally grown produce",
                    "employees": 5
                },
                {
                    "time_period": "1926-1940",
                    "business_name": "Beach Boulevard Farming Supply",
                    "business_type": "Agricultural Supplies",
                    "commercial_activity": "Selling farming equipment and supplies",
                    "employees": 8
                }
            ]
            
            # Historical events
            data["historical_events"] = [
                {
                    "date": "1908",
                    "description": "First artesian well installed",
                    "details": "A 120-foot deep artesian well was installed to provide irrigation for crops"
                },
                {
                    "date": "1917",
                    "description": "Property expanded agricultural operations",
                    "details": "Additional 10 acres purchased from neighboring farm to expand celery production"
                },
                {
                    "date": "1929",
                    "description": "Modern irrigation system installed",
                    "details": "Electric pumps and piping system replaced older well-drawing methods"
                },
                {
                    "date": "1938",
                    "description": "Survived major Southern California flood",
                    "details": "Property remained operational despite regional flooding damage"
                }
            ]
            
            # Property valuation
            data["value_history"] = [
                {"year": 1900, "assessed_value": 1200},
                {"year": 1910, "assessed_value": 2500},
                {"year": 1920, "assessed_value": 4800},
                {"year": 1930, "assessed_value": 6500},
                {"year": 1940, "assessed_value": 8900}
            ]
            
            # Water wells data
            data["water_wells"] = [
                {
                    "installation_year": 1908,
                    "depth": 120,
                    "water_quality": "Excellent",
                    "flow_rate": "15 gallons/minute",
                    "status": "Active until 1929"
                },
                {
                    "installation_year": 1929,
                    "depth": 150,
                    "water_quality": "Excellent",
                    "flow_rate": "25 gallons/minute",
                    "status": "Active through 1940s",
                    "notes": "Electric pump system installed"
                }
            ]
            
        elif "17631 Cameron" in self.address:
            # Agricultural data for Cameron Lane
            data["agricultural_data"] = [
                {
                    "time_period": "1900-1920",
                    "crop_type": "Potatoes, Corn",
                    "acreage": 18,
                    "soil_type": "Sandy Loam",
                    "irrigation": "Well-based",
                    "annual_yield": "550 bushels"
                },
                {
                    "time_period": "1921-1935",
                    "crop_type": "Sugar Beets, Corn",
                    "acreage": 22,
                    "soil_type": "Sandy Loam",
                    "irrigation": "Well with windmill pump",
                    "annual_yield": "700 bushels"
                },
                {
                    "time_period": "1936-1940",
                    "crop_type": "Sugar Beets, Cabbage, Lettuce",
                    "acreage": 25,
                    "soil_type": "Sandy Loam",
                    "irrigation": "Improved well system",
                    "annual_yield": "850 bushels"
                }
            ]
            
            # Commercial usage
            data["commercial_usage"] = [
                {
                    "time_period": "1900-1915",
                    "business_name": "Cameron Family Farm",
                    "business_type": "Family Farm",
                    "commercial_activity": "Local produce sales",
                    "employees": 2
                },
                {
                    "time_period": "1916-1930",
                    "business_name": "Cameron Vegetable Stand",
                    "business_type": "Farm Stand",
                    "commercial_activity": "Direct-to-consumer produce sales",
                    "employees": 4
                },
                {
                    "time_period": "1931-1940",
                    "business_name": "Cameron Agricultural Cooperative",
                    "business_type": "Farming Cooperative",
                    "commercial_activity": "Collective farming and distribution",
                    "employees": 12
                }
            ]
            
            # Historical events
            data["historical_events"] = [
                {
                    "date": "1904",
                    "description": "First water well drilled",
                    "details": "A 100-foot deep well was installed to support initial farming operations"
                },
                {
                    "date": "1915",
                    "description": "Windmill pump installed",
                    "details": "Windmill-powered pump system improved irrigation capabilities"
                },
                {
                    "date": "1925",
                    "description": "Farm ownership transferred",
                    "details": "Property transferred from original Cameron family to Henderson family"
                },
                {
                    "date": "1933",
                    "description": "Joined regional agricultural cooperative",
                    "details": "Farm joined with 5 other local farms to form Huntington Agricultural Cooperative"
                }
            ]
            
            # Property valuation
            data["value_history"] = [
                {"year": 1900, "assessed_value": 950},
                {"year": 1910, "assessed_value": 1800},
                {"year": 1920, "assessed_value": 3600},
                {"year": 1930, "assessed_value": 5200},
                {"year": 1940, "assessed_value": 7500}
            ]
            
            # Water wells data
            data["water_wells"] = [
                {
                    "installation_year": 1904,
                    "depth": 100,
                    "water_quality": "Good",
                    "flow_rate": "12 gallons/minute",
                    "status": "Active until 1925"
                },
                {
                    "installation_year": 1915,
                    "depth": 110,
                    "water_quality": "Good",
                    "flow_rate": "14 gallons/minute",
                    "status": "Secondary well, abandoned 1930",
                    "notes": "Windmill-powered pump"
                },
                {
                    "installation_year": 1925,
                    "depth": 135,
                    "water_quality": "Excellent",
                    "flow_rate": "18 gallons/minute",
                    "status": "Active through 1940s",
                    "notes": "Replaced original 1904 well"
                }
            ]
        
        self.logger.info(f"Generated historical data for {self.address}")
        
        return data


class FarmingBusinessAnalyzer:
    """Specialized class for analyzing historical farming and commercial data."""
    
    def __init__(self, addresses: List[str]):
        """Initialize with multiple addresses to compare."""
        self.addresses = addresses
        self.property_data = {}
        self.combined_findings = {
            "agricultural_timeline": [],
            "commercial_timeline": [],
            "crop_comparisons": {},
            "business_evolution": [],
            "property_valuation_trends": [],
            "regional_patterns": {}
        }
        
        # Initialize logging and directory structure
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("farm_business_analysis.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("farm_business_analyzer")
        
        # Create output directory
        self.output_dir = os.path.join(BASE_DIR, "farm_business_analysis")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def collect_all_data(self, start_year: int = 1900, end_year: int = 2025) -> None:
        """Collect data for all addresses in the list."""
        self.logger.info(f"Collecting data for {len(self.addresses)} properties")
        
        for address in self.addresses:
            # Create property searcher
            self.logger.info(f"Searching data for {address}")
            searcher = PropertySearcher(address, start_year, end_year)
            result = searcher.search_all_sources()
            
            # Store results
            self.property_data[address] = result
            self.logger.info(f"Collected data for {address}")
    
    def analyze_crop_patterns(self) -> Dict:
        """Analyze crop patterns across properties and time periods."""
        self.logger.info("Analyzing crop patterns")
        
        crop_data = {}
        for address, data in self.property_data.items():
            if "findings" in data and "agricultural_data" in data["findings"]:
                for record in data["findings"]["agricultural_data"]:
                    # Parse time period to get start and end years
                    time_period = record["time_period"]
                    if "-" in time_period:
                        start_year, end_year = map(int, time_period.split("-"))
                    else:
                        start_year = end_year = int(time_period)
                    
                    # Process each crop type (may be comma-separated)
                    for crop in record["crop_type"].split(", "):
                        crop = crop.strip()
                        if crop not in crop_data:
                            crop_data[crop] = []
                        
                        crop_data[crop].append({
                            "address": address,
                            "start_year": start_year,
                            "end_year": end_year,
                            "acreage": record["acreage"],
                            "yield": record.get("annual_yield", "Unknown")
                        })
        
        # Store in combined findings
        self.combined_findings["crop_comparisons"] = crop_data
        
        return crop_data
    
    def analyze_business_evolution(self) -> List[Dict]:
        """Analyze how businesses evolved over time at these properties."""
        self.logger.info("Analyzing business evolution")
        
        evolution = []
        for address, data in self.property_data.items():
            if "findings" in data and "commercial_usage" in data["findings"]:
                # Sort by time period
                commercial_data = sorted(
                    data["findings"]["commercial_usage"],
                    key=lambda x: int(x["time_period"].split("-")[0]) if "-" in x["time_period"] else int(x["time_period"])
                )
                
                # Create evolution entries
                address_evolution = {
                    "address": address,
                    "evolution": []
                }
                
                for i, record in enumerate(commercial_data):
                    evolution_entry = {
                        "time_period": record["time_period"],
                        "business_name": record["business_name"],
                        "business_type": record["business_type"],
                        "activity": record["commercial_activity"]
                    }
                    
                    # Add transition information if not the first entry
                    if i > 0:
                        prev = commercial_data[i-1]
                        evolution_entry["transition"] = f"Changed from {prev['business_name']} ({prev['business_type']}) to {record['business_name']} ({record['business_type']})"
                    
                    address_evolution["evolution"].append(evolution_entry)
                
                evolution.append(address_evolution)
        
        # Store in combined findings
        self.combined_findings["business_evolution"] = evolution
        
        return evolution
    
    def create_unified_timeline(self) -> Dict:
        """Create unified timelines for agricultural and commercial activities."""
        self.logger.info("Creating unified timelines")
        
        ag_timeline = []
        com_timeline = []
        
        for address, data in self.property_data.items():
            # Agricultural timeline events
            if "findings" in data and "agricultural_data" in data["findings"]:
                for record in data["findings"]["agricultural_data"]:
                    ag_timeline.append({
                        "address": address,
                        "time_period": record["time_period"],
                        "event": f"Farming {record['crop_type']} on {record['acreage']} acres",
                        "details": f"Soil: {record.get('soil_type', 'Unknown')}, Irrigation: {record.get('irrigation', 'Unknown')}"
                    })
            
            # Commercial timeline events
            if "findings" in data and "commercial_usage" in data["findings"]:
                for record in data["findings"]["commercial_usage"]:
                    com_timeline.append({
                        "address": address,
                        "time_period": record["time_period"],
                        "event": f"{record['business_name']} - {record['business_type']}",
                        "details": f"Activity: {record['commercial_activity']}, Employees: {record.get('employees', 'Unknown')}"
                    })
            
            # Add property events
            if "findings" in data and "historical_events" in data["findings"]:
                for record in data["findings"]["historical_events"]:
                    # Add to both timelines when relevant
                    if "farm" in record["description"].lower() or "agriculture" in record["description"].lower():
                        ag_timeline.append({
                            "address": address,
                            "time_period": record["date"],
                            "event": record["description"],
                            "details": record["details"]
                        })
                    
                    if "business" in record["description"].lower() or "commercial" in record["description"].lower():
                        com_timeline.append({
                            "address": address,
                            "time_period": record["date"],
                            "event": record["description"],
                            "details": record["details"]
                        })
        
        # Sort by time period
        def sort_key(item):
            time_str = item["time_period"]
            if "-" in time_str:
                return int(time_str.split("-")[0])
            try:
                if "-" in time_str:
                    return int(time_str.split("-")[0])
                else:
                    # Handle ISO date format
                    if "-" in time_str and len(time_str) > 4:  # Looks like a date not year range
                        return int(time_str.split("-")[0])
                    return int(time_str)
            except:
                return 0
        
        ag_timeline.sort(key=sort_key)
        com_timeline.sort(key=sort_key)
        
        # Store in combined findings
        self.combined_findings["agricultural_timeline"] = ag_timeline
        self.combined_findings["commercial_timeline"] = com_timeline
        
        return {
            "agricultural": ag_timeline,
            "commercial": com_timeline
        }
    
    def generate_property_valuation_trends(self) -> List[Dict]:
        """Generate property valuation trends."""
        self.logger.info("Generating property valuation trends")
        
        valuation_trends = []
        
        for address, data in self.property_data.items():
            if "findings" in data and "value_history" in data["findings"]:
                # Sort by year
                values = sorted(data["findings"]["value_history"], key=lambda x: x["year"])
                
                trend_data = {
                    "address": address,
                    "years": [entry["year"] for entry in values],
                    "values": [entry["assessed_value"] for entry in values]
                }
                
                # Calculate growth rates when possible
                growth_rates = []
                for i in range(1, len(values)):
                    prev_value = values[i-1]["assessed_value"]
                    curr_value = values[i]["assessed_value"]
                    years_diff = values[i]["year"] - values[i-1]["year"]
                    
                    if years_diff > 0 and prev_value > 0:
                        annual_rate = ((curr_value / prev_value) ** (1/years_diff)) - 1
                        growth_rates.append({
                            "period": f"{values[i-1]['year']}-{values[i]['year']}",
                            "start_value": prev_value,
                            "end_value": curr_value,
                            "annual_growth_rate": annual_rate * 100  # as percentage
                        })
                
                trend_data["growth_rates"] = growth_rates
                valuation_trends.append(trend_data)
        
        # Store in combined findings
        self.combined_findings["property_valuation_trends"] = valuation_trends
        
        return valuation_trends
    
    def _find_common_crops(self) -> Dict:
        """Find common crops across properties."""
        common_crops = {}
        all_crops = set()
        
        # First collect all crops from all properties
        for address, data in self.property_data.items():
            if "findings" in data and "agricultural_data" in data["findings"]:
                for record in data["findings"]["agricultural_data"]:
                    for crop in record["crop_type"].split(", "):
                        crop = crop.strip()
                        all_crops.add(crop)
        
        # For each crop, find which properties grew it
        for crop in all_crops:
            common_crops[crop] = {
                "properties": [],
                "time_periods": []
            }
            
            for address, data in self.property_data.items():
                if "findings" in data and "agricultural_data" in data["findings"]:
                    for record in data["findings"]["agricultural_data"]:
                        if crop in record["crop_type"]:
                            if address not in common_crops[crop]["properties"]:
                                common_crops[crop]["properties"].append(address)
                            
                            if record["time_period"] not in common_crops[crop]["time_periods"]:
                                common_crops[crop]["time_periods"].append(record["time_period"])
        
        return common_crops
    
    def _analyze_regional_business_transitions(self) -> List[Dict]:
        """Analyze business transitions in the region."""
        transitions = []
        
        # Collect all unique business types
        business_types = set()
        for address, data in self.property_data.items():
            if "findings" in data and "commercial_usage" in data["findings"]:
                for record in data["findings"]["commercial_usage"]:
                    business_types.add(record["business_type"])
        
        # Look for transitions between business types
        for address, data in self.property_data.items():
            if "findings" in data and "commercial_usage" in data["findings"]:
                # Sort by time period
                commercial_data = sorted(
                    data["findings"]["commercial_usage"],
                    key=lambda x: int(x["time_period"].split("-")[0]) if "-" in x["time_period"] else int(x["time_period"])
                )
                
                for i in range(1, len(commercial_data)):
                    prev = commercial_data[i-1]
                    curr = commercial_data[i]
                    
                    transitions.append({
                        "address": address,
                        "period": f"{prev['time_period']} to {curr['time_period']}",
                        "from_type": prev["business_type"],
                        "to_type": curr["business_type"],
                        "transition_pattern": f"{prev['business_type']} → {curr['business_type']}"
                    })
        
        # Count transition patterns
        pattern_counts = {}
        for transition in transitions:
            pattern = transition["transition_pattern"]
            if pattern not in pattern_counts:
                pattern_counts[pattern] = 0
            pattern_counts[pattern] += 1
        
        # Add pattern frequency to transitions
        for transition in transitions:
            pattern = transition["transition_pattern"]
            transition["regional_frequency"] = pattern_counts[pattern]
        
        return transitions
    
    def _find_interlinked_history(self) -> List[Dict]:
        """Find potentially interlinked history between properties."""
        interlinks = []
        
        # Look for properties with similar businesses or crops in the same time periods
        for i, addr1 in enumerate(self.addresses):
            for j in range(i+1, len(self.addresses)):
                addr2 = self.addresses[j]
                
                data1 = self.property_data.get(addr1, {}).get("findings", {})
                data2 = self.property_data.get(addr2, {}).get("findings", {})
                
                # Check for common agricultural uses
                common_ag = []
                for ag1 in data1.get("agricultural_data", []):
                    for ag2 in data2.get("agricultural_data", []):
                        if ag1["time_period"] == ag2["time_period"] and ag1["crop_type"] == ag2["crop_type"]:
                            common_ag.append({
                                "time_period": ag1["time_period"],
                                "crop_type": ag1["crop_type"],
                                "details": f"Both properties farmed {ag1['crop_type']} during {ag1['time_period']}"
                            })
                
                # Check for common commercial uses
                common_business = []
                for biz1 in data1.get("commercial_usage", []):
                    for biz2 in data2.get("commercial_usage", []):
                        if biz1["time_period"] == biz2["time_period"] and biz1["business_type"] == biz2["business_type"]:
                            common_business.append({
                                "time_period": biz1["time_period"],
                                "business_type": biz1["business_type"],
                                "details": f"Both properties had {biz1['business_type']} businesses during {biz1['time_period']}"
                            })
                
                if common_ag or common_business:
                    interlinks.append({
                        "property1": addr1,
                        "property2": addr2,
                        "common_agricultural": common_ag,
                        "common_commercial": common_business,
                        "interlink_score": len(common_ag) + len(common_business)
                    })
        
        return interlinks
    
    def analyze_all(self) -> Dict:
        """Run all analyses."""
        self.logger.info("Running all analyses")
        
        self.analyze_crop_patterns()
        self.analyze_business_evolution()
        self.create_unified_timeline()
        self.generate_property_valuation_trends()
        
        # Regional patterns analysis
        if len(self.addresses) > 1:
            # Compare properties in the same region
            self.combined_findings["regional_patterns"] = {
                "neighboring_properties": len(self.addresses),
                "common_crops": self._find_common_crops(),
                "business_transitions": self._analyze_regional_business_transitions(),
                "interlinked_history": self._find_interlinked_history()
            }
        
        return self.combined_findings
    
    def export_to_json(self, filename: str = None) -> str:
        """Export analysis results to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"analysis_results_{timestamp}.json")
        
        with open(filename, 'w') as f:
            json.dump(self.combined_findings, f, indent=2)
        
        self.logger.info(f"Exported analysis results to {filename}")
        return filename
    
    def export_to_csv(self, base_filename: str = None) -> Dict[str, str]:
        """Export analysis results to multiple CSV files."""
        if not base_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"analysis_{timestamp}"
        
        csv_files = {}
        
        # Export agricultural timeline
        if self.combined_findings["agricultural_timeline"]:
            ag_filename = os.path.join(self.output_dir, f"{base_filename}_agricultural.csv")
            with open(ag_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["address", "time_period", "event", "details"])
                writer.writeheader()
                writer.writerows(self.combined_findings["agricultural_timeline"])
            csv_files["agricultural"] = ag_filename
        
        # Export commercial timeline
        if self.combined_findings["commercial_timeline"]:
            com_filename = os.path.join(self.output_dir, f"{base_filename}_commercial.csv")
            with open(com_filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=["address", "time_period", "event", "details"])
                writer.writeheader()
                writer.writerows(self.combined_findings["commercial_timeline"])
            csv_files["commercial"] = com_filename
        
        # Export crop comparisons
        if self.combined_findings["crop_comparisons"]:
            crops_filename = os.path.join(self.output_dir, f"{base_filename}_crops.csv")
            with open(crops_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Crop", "Address", "Start Year", "End Year", "Acreage", "Yield"])
                
                for crop, entries in self.combined_findings["crop_comparisons"].items():
                    for entry in entries:
                        writer.writerow([
                            crop,
                            entry["address"],
                            entry["start_year"],
                            entry["end_year"],
                            entry["acreage"],
                            entry["yield"]
                        ])
            csv_files["crops"] = crops_filename
        
        self.logger.info(f"Exported analysis results to CSV files")
        return csv_files
