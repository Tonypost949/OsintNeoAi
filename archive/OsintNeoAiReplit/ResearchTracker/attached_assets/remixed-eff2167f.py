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
                            common_crops[crop]["time_periods"].append(record["time_period"])
        class PropertySearcher:
    """Handles searching for property information across multiple sources with focus on farming and commercial data."""
    
    def __init__(self, address: str, start_year: int = 1900, end_year: int = 2025):
        """Initialize with search parameters."""
        self.address = address
        self.start_year = start_year
        self.end_year = end_year
        self.results = {
            "query": {
                "address": address,
                "time_period": f"{start_year}-{end_year}",
                "timestamp": datetime.datetime.now().isoformat()
            },
            "sources": {},
            "findings": {
                "ownership": [],
                "property_details": {},
                "historical_events": [],
                "value_history": [],
                "agricultural_data": [],
                "commercial_usage": [],
                "crop_history": [],
                "business_licenses": []
            }
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.join(PROPERTY_RECORDS_DIR, "raw_data"), exist_ok=True)
        
        # Record of all API calls for auditing
        self.api_calls = []
    
    def search_all_sources(self) -> Dict:
        """Search all available property databases with focus on agricultural and commercial data."""
        logger.info(f"Starting comprehensive search for: {self.address}")
        
        # County Assessor's Office (historical records)
        self._search_county_assessor()
        
        # Real estate databases (current data)
        self._search_real_estate_dbs()
        
        # Historical archives
        self._search_historical_archives()
        
        # Agricultural records
        self._search_agricultural_records()
        
        # Commercial and business records
        self._search_commercial_records()
        
        # Parse and consolidate findings
        self._consolidate_findings()
        
        logger.info(f"Completed search across {len(self.api_calls)} sources")
        return self.results
    
    def _search_agricultural_records(self) -> None:
        """Search agricultural records databases for farming history."""
        logger.info("Searching agricultural records...")
        
        try:
            # Record API call attempt
            call_record = {
                "api": "agricultural_records",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "startYear": self.start_year,
                    "endYear": self.end_year
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for demonstration - Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["agricultural_records"] = {
                    "status": "success",
                    "records_found": 3,
                    "data": [
                        {
                            "year": "1940-1942",
                            "crop_type": "Strawberries",
                            "acreage": 2.5,
                            "annual_yield": "~12,000 lbs",
                            "soil_type": "Sandy loam",
                            "irrigation": "Well water"
                        },
                        {
                            "year": "1945-1950",
                            "crop_type": "Strawberries, Tomatoes",
                            "acreage": 2.3,
                            "annual_yield": "Mixed crops: ~15,000 lbs total",
                            "soil_type": "Sandy loam with amendments",
                            "irrigation": "Well water + county water access"
                        },
                        {
                            "year": "1950-1955",
                            "crop_type": "Mixed vegetables",
                            "acreage": 2.1,
                            "annual_yield": "Data not available",
                            "soil_type": "Sandy loam with amendments",
                            "irrigation": "County water system"
                        }
                    ]
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["agricultural_records"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "year": "1935-1942",
                            "crop_type": "Mixed vegetables (cabbage, onions, lettuce)",
                            "acreage": 1.8,
                            "annual_yield": "Data not available",
                            "soil_type": "Sandy loam",
                            "irrigation": "Well water"
                        },
                        {
                            "year": "1947-1960",
                            "crop_type": "Peppers, Cucumber",
                            "acreage": 1.5,
                            "annual_yield": "~8,000 lbs yearly average",
                            "soil_type": "Sandy loam with amendments",
                            "irrigation": "County water system"
                        }
                    ]
                }
            else:
                self.results["sources"]["agricultural_records"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error accessing agricultural records: {e}")
            self.results["sources"]["agricultural_records"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _search_commercial_records(self) -> None:
        """Search commercial and business license records."""
        logger.info("Searching commercial records...")
        
        try:
            # Record API call attempt
            call_record = {
                "api": "business_records",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "startYear": self.start_year,
                    "endYear": self.end_year
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for demonstration - Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["commercial_records"] = {
                    "status": "success",
                    "records_found": 3,
                    "data": [
                        {
                            "year": "1946-1952",
                            "business_name": "Tanaka Family Farm",
                            "business_type": "Agricultural - Farm Stand",
                            "license_number": "HB-AG-1946-083",
                            "employees": "Family operated, 2-3 seasonal workers",
                            "commercial_activity": "Direct sale of produce at roadside stand"
                        },
                        {
                            "year": "1953-1960",
                            "business_name": "Tanaka Produce",
                            "business_type": "Agricultural - Distribution",
                            "license_number": "HB-AG-1953-021",
                            "employees": "5-7 workers",
                            "commercial_activity": "Farm stand plus wholesale distribution to local markets"
                        },
                        {
                            "year": "1963-1970",
                            "business_name": "Beach Blvd Nursery",
                            "business_type": "Commercial - Nursery/Garden Center",
                            "license_number": "HB-COM-1963-142",
                            "employees": "8-12 workers",
                            "commercial_activity": "Retail nursery, garden supplies"
                        }
                    ]
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["commercial_records"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "year": "1947-1955",
                            "business_name": "Nakamura Family Farm",
                            "business_type": "Agricultural - Wholesale",
                            "license_number": "HB-AG-1947-056",
                            "employees": "Family operated plus 3-4 workers",
                            "commercial_activity": "Wholesale vegetable supplier to markets"
                        },
                        {
                            "year": "1958-1972",
                            "business_name": "Cameron Gardens",
                            "business_type": "Agricultural/Commercial - Mixed",
                            "license_number": "HB-COM-1958-079",
                            "employees": "6-10 workers",
                            "commercial_activity": "Garden center with wholesale nursery operations"
                        }
                    ]
                }
            else:
                self.results["sources"]["commercial_records"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error accessing commercial records: {e}")
            self.results["sources"]["commercial_records"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _search_real_estate_dbs(self) -> None:
        """Search current real estate databases."""
        logger.info("Searching real estate databases...")
        
        try:
            # Record API call attempt
            call_record = {
                "api": "real_estate_db",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for demonstration - Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["real_estate"] = {
                    "status": "success",
                    "records_found": 1,
                    "data": {
                        "current_owner": "REDACTED",
                        "last_sale_date": "2015-06-15",
                        "last_sale_price": 780000,
                        "current_value": 1250000,
                        "year_built": 1955,
                        "lot_size": 0.25,
                        "building_size": 1850
                    }
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["real_estate"] = {
                    "status": "success",
                    "records_found": 1,
                    "data": {
                        "current_owner": "REDACTED",
                        "last_sale_date": "2020-03-22",
                        "last_sale_price": 895000,
                        "current_value": 1350000,
                        "year_built": 1960,
                        "lot_size": 0.2,
                        "building_size": 1650
                    }
                }
            else:
                self.results["sources"]["real_estate"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": {}
                }
            
        except Exception as e:
            logger.error(f"Error accessing real estate databases: {e}")
            self.results["sources"]["real_estate"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _search_historical_archives(self) -> None:
        """Search historical property archives."""
        logger.info("Searching historical archives...")
        
        try:
            # Record API call attempt
            call_record = {
                "api": "historical_archives",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "startYear": self.start_year,
                    "endYear": self.end_year
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["historical_archives"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "type": "deed",
                            "date": "1940-04-15",
                            "description": "Transfer to Tanaka family",
                            "details": "Purchase of agricultural land for strawberry farming"
                        },
                        {
                            "type": "government_action",
                            "date": "1942-05-06",
                            "description": "Property seized under EO 9066",
                            "details": "Japanese internment period"
                        }
                    ]
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["historical_archives"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "type": "deed",
                            "date": "1935-09-22",
                            "description": "Transfer to Yamamoto family",
                            "details": "Purchase of agricultural land for vegetable farming"
                        },
                        {
                            "type": "government_action",
                            "date": "1942-05-03",
                            "description": "Property seized under EO 9066",
                            "details": "Japanese internment period"
                        }
                    ]
                }
            else:
                self.results["sources"]["historical_archives"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error accessing historical archives: {e}")
            self.results["sources"]["historical_archives"] = {
                "status": "error",
                "message": str(e)
            }
    
    def _consolidate_findings(self) -> None:
        """Consolidate findings from all sources into a unified timeline."""
        logger.info("Consolidating findings from all sources...")
        
        # Process county assessor data
        if "county_assessor" in self.results["sources"] and self.results["sources"]["county_assessor"]["status"] == "success":
            for record in self.results["sources"]["county_assessor"]["data"]:
                # Add to ownership records
                self.results["findings"]["ownership"].append({
                    "year": record["year"],
                    "owner": record["owner"],
                    "source": "county_assessor"
                })
                
                # Add to value history
                self.results["findings"]["value_history"].append({
                    "year": record["year"],
                    "assessed_value": record["assessed_value"],
                    "source": "county_assessor"
                })
        
        # Process historical archives
        if "historical_archives" in self.results["sources"] and self.results["sources"]["historical_archives"]["status"] == "success":
            for record in self.results["sources"]["historical_archives"]["data"]:
                # Add to historical events
                self.results["findings"]["historical_events"].append({
                    "date": record["date"],
                    "event_type": record["type"],
                    "description": record["description"],
                    "details": record["details"],
                    "source": "historical_archives"
                })
        
        # Process agricultural records
        if "agricultural_records" in self.results["sources"] and self.results["sources"]["agricultural_records"]["status"] == "success":
            for record in self.results["sources"]["agricultural_records"]["data"]:
                # Add to agricultural data
                self.results["findings"]["agricultural_data"].append({
                    "time_period": record["year"],
                    "crop_type": record["crop_type"],
                    "acreage": record["acreage"],
                    "annual_yield": record.get("annual_yield", "Unknown"),
                    "soil_type": record.get("soil_type", "Unknown"),
                    "irrigation": record.get("irrigation", "Unknown"),
                    "source": "agricultural_records"
                })
                
                # Add to crop history for timeline
                self.results["findings"]["crop_history"].append({
                    "time_period": record["year"],
                    "crop_type": record["crop_type"],
                    "source": "agricultural_records"
                })
        
        # Process commercial records
        if "commercial_records" in self.results["sources"] and self.results["sources"]["commercial_records"]["status"] == "success":
            for record in self.results["sources"]["commercial_records"]["data"]:
                # Add to commercial usage
                self.results["findings"]["commercial_usage"].append({
                    "time_period": record["year"],
                    "business_name": record["business_name"],
                    "business_type": record["business_type"],
                    "commercial_activity": record["commercial_activity"],
                    "employees": record.get("employees", "Unknown"),
                    "source": "commercial_records"
                })
                
                # Add to business licenses
                self.results["findings"]["business_licenses"].append({
                    "time_period": record["year"],
                    "business_name": record["business_name"],
                    "license_number": record["license_number"],
                    "source": "commercial_records"
                })
        
        # Add current property details if available
        if "real_estate" in self.results["sources"] and self.results["sources"]["real_estate"]["status"] == "success":
            self.results["findings"]["property_details"] = self.results["sources"]["real_estate"]["data"]
    
    def save_results(self, format_type: str = "json") -> str:
        """Save results to a file and return the filename."""
        output_dir = os.path.join(PROPERTY_RECORDS_DIR, "raw_data")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on address and timestamp
        address_slug = re.sub(r'[^\w\s]', '', self.address).replace(' ', '_').lower()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/property_search_{address_slug}_{timestamp}.json"
        
        # Save file
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")
        
        # Also save API call log for audit purposes
        audit_filename = f"{output_dir}/api_call_log_{address_slug}_{timestamp}.json"
        with open(audit_filename, 'w') as f:
            json.dump(self.api_calls, f, indent=2)
        
        logger.info(f"API call log saved to {audit_filename}")
        
        return filename


class MediaArchiveSearcher:
    """Handles searching for information in media archives."""
    
    def __init__(self, address: str, start_year: int = 1900, end_year: int = 2025):
        """Initialize with search parameters."""
        self.address = address
        # Extract components from address for more targeted searches
        self.address_components = self._parse_address(address)
        self.start_year = start_year
        self.end_year = end_year
        self.results = {
            "query": {
                "address": address,
                "address_components": self.address_components,
                "time_period": f"{start_year}-{end_year}",
                "timestamp": datetime.datetime.now().isoformat()
            },
            "sources": {},
            "findings": {
                "newspaper_articles": [],
                "archived_webpages": [],
                "library_records": [],
                "related_mentions": []
            }
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.join(MEDIA_ARCHIVES_DIR, "raw_data"), exist_ok=True)
        
        # Record of all API calls for auditing
        self.api_calls = []
    
    def _parse_address(self, address: str) -> Dict[str, str]:
        """Parse address into components for more targeted searches."""
        # Simple regex parsing - in production would use a proper address parser
        components = {"full_address": address}
        
        # Extract street number and name
        street_match = re.search(r'(\d+)\s+([A-Za-z\s]+)(?:,|\s+)([A-Za-z\s]+)(?:,|\s+)([A-Za-z]{2})(?:\s+(\d+))?', address)
        if street_match:
            components["street_number"] = street_match.group(1)
            components["street_name"] = street_match.group(2).strip()
            components["city"] = street_match.group(3).strip()
            components["state"] = street_match.group(4).strip()
            if len(street_match.groups()) > 4 and street_match.group(5):
                components["zip"] = street_match.group(5)
        
        return components

    def search_newspapers(self) -> None:
        """Search historical newspapers."""
        logger.info(f"Searching newspapers for: {self.address}")
        
        try:
            # Record API call
            call_record = {
                "api": "newspaper_archives",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "startYear": self.start_year,
                    "endYear": self.end_year
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["newspapers"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "publication": "Huntington Beach News",
                            "date": "1941-06-12",
                            "title": "Local Farms Report Successful Harvest",
                            "excerpt": "...several local strawberry farms including the Tanaka property on Beach Boulevard reported exceptional yields this season...",
                            "page": 4
                        },
                        {
                            "publication": "Orange County Register",
                            "date": "1942-05-15",
                            "title": "Local Japanese Families Relocated",
                            "excerpt": "...among those affected by the government order were the Tanaka family who operated a successful strawberry farm on Beach Boulevard...",
                            "page": 1
                        }
                    ]
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["newspapers"] = {
                    "status": "success",
                    "records_found": 1,
                    "data": [
                        {
                            "publication": "Huntington Beach Independent",
                            "date": "1940-08-23",
                            "title": "Local Produce Featured at County Fair",
                            "excerpt": "...vegetables from the Yamamoto farm on Cameron Lane won several ribbons at the annual county agricultural exhibition...",
                            "page": 6
                        }
                    ]
                }
            else:
                self.results["sources"]["newspapers"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error searching newspapers: {e}")
            self.results["sources"]["newspapers"] = {
                "status": "error",
                "message": str(e)
            }

    def search_web_archives(self) -> None:
        """Search web archives for historical mentions."""
        logger.info(f"Searching web archives for: {self.address}")
        
        try:
            # Record API call
            call_record = {
                "api": "web_archives",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "url": f"https://maps.google.com/?q={self.address.replace(' ', '+')}"
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for demonstration
            self.results["sources"]["web_archives"] = {
                "status": "success",
                "records_found": 0,
                "data": []
            }
            
        except Exception as e:
            logger.error(f"Error searching web archives: {e}")
            self.results["sources"]["web_archives"] = {
                "status": "error",
                "message": str(e)
            }

    def search_library_collections(self) -> None:
        """Search library and institutional digital collections."""
        logger.info(f"Searching library collections for: {self.address}")
        
        try:
            # Record API call
            call_record = {
                "api": "library_collections",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "address": self.address,
                    "startYear": self.start_year,
                    "endYear": self.end_year
                }
            }
            self.api_calls.append(call_record)
            
            # Mock data for Beach Blvd
            if "17642 Beach" in self.address:
                self.results["sources"]["library_collections"] = {
                    "status": "success",
                    "records_found": 2,
                    "data": [
                        {
                            "collection": "OC Agricultural Archives",
                            "item_type": "Photograph",
                            "date": "1941",
                            "title": "Strawberry Harvest at Tanaka Farm",
                            "description": "Black and white photograph showing strawberry harvest at the Tanaka farm on Beach Boulevard",
                            "archive_id": "OCAA-1941-0623"
                        },
                        {
                            "collection": "Japanese American Relocation Records",
                            "item_type": "Document",
                            "date": "1942-05",
                            "title": "Property Inventory - Tanaka",
                            "description": "Inventory of property and assets at the time of relocation",
                            "archive_id": "JARR-1942-0113"
                        }
                    ]
                }
            # Mock data for Cameron Lane
            elif "17631 Cameron" in self.address:
                self.results["sources"]["library_collections"] = {
                    "status": "success",
                    "records_found": 1,
                    "data": [
                        {
                            "collection": "Japanese American Relocation Records",
                            "item_type": "Document",
                            "date": "1942-05",
                            "title": "Property Inventory - Yamamoto",
                            "description": "Inventory of property and assets at the time of relocation",
                            "archive_id": "JARR-1942-0098"
                        }
                    ]
                }
            else:
                self.results["sources"]["library_collections"] = {
                    "status": "success",
                    "records_found": 0,
                    "data": []
                }
            
        except Exception as e:
            logger.error(f"Error searching library collections: {e}")
            self.results["sources"]["library_collections"] = {
                "status": "error",
                "message": str(e)
            }

    def search_all_sources(self) -> Dict:
        """Search all available media archives."""
        self.search_newspapers()
        self.search_web_archives()
        self.search_library_collections()
        self._consolidate_findings()
        
        logger.info(f"Completed media archive search across {len(self.results['sources'])} sources")
        return self.results

    def _consolidate_findings(self) -> None:
        """Consolidate findings from all sources into categorized results."""
        # Process newspaper data
        if "newspapers" in self.results["sources"] and self.results["sources"]["newspapers"]["status"] == "success":
            for record in self.results["sources"]["newspapers"]["data"]:
                self.results["findings"]["newspaper_articles"].append({
                    "date": record["date"],
                    "publication": record["publication"],
                    "title": record["title"],
                    "excerpt": record["excerpt"],
                    "page": record["page"],
                    "source": "newspaper_archives"
                })
        
        # Process web archive data
        if "web_archives" in self.results["sources"] and self.results["sources"]["web_archives"]["status"] == "success":
            for record in self.results["sources"]["web_archives"]["data"]:
                self.results["findings"]["archived_webpages"].append({
                    "date": record.get("date", ""),
                    "url": record.get("url", ""),
                    "title": record.get("title", ""),
                    "source": "web_archives"
                })
        
        # Process library collection data
        if "library_collections" in self.results["sources"] and self.results["sources"]["library_collections"]["status"] == "success":
            for record in self.results["sources"]["library_collections"]["data"]:
                self.results["findings"]["library_records"].append({
                    "date": record["date"],
                    "collection": record["collection"],
                    "item_type": record["item_type"],
                    "title": record["title"],
                    "description": record["description"],
                    "archive_id": record["archive_id"],
                    "source": "library_collections"
                })

    def save_results(self, format_type: str = "json") -> str:
        """Save results to a file and return the filename."""
        output_dir = os.path.join(MEDIA_ARCHIVES_DIR, "raw_data")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename based on address and timestamp
        address_slug = re.sub(r'[^\w\s]', '', self.address).replace(' ', '_').lower()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/media_search_{address_slug}_{timestamp}.json"
        
        # Save file
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")
        
        # Also save API call log for audit purposes
        audit_filename = f"{output_dir}/api_call_log_{address_slug}_{timestamp}.json"
        with open(audit_filename, 'w') as f:
            json.dump(self.api_calls, f, indent=2)
        
        logger.info(f"API call log saved to {audit_filename}")
        
        return filename


class TimelineGenerator:
    """Creates visual timelines from research data."""
    
    def __init__(self, address: str, start_year: int = 1900, end_year: int = 2025):
        """Initialize with timeline parameters."""
        self.address = address
        self.start_year = start_year
        self.end_year = end_year
        
        # Create output directory if it doesn't exist
        os.makedirs(TIMELINES_DIR, exist_ok=True)
    
    def create_ownership_timeline(self, ownership_data: List[Dict]) -> str:
        """Create a timeline visualization of property ownership."""
        
        # Prepare data
        years = []
        owners = []
        for record in ownership_data:
            years.append(int(record["year"]))
            owners.append(record["owner"])
        
        # Convert to DataFrame for easier plotting
        df = pd.DataFrame({'year': years, 'owner': owners})
        df = df.sort_values('year')
        
        # Create plot
        plt.figure(figsize=(12, 6))
        
        # Plot each owner as a horizontal line
        unique_owners = df['owner'].unique()
        colors = plt.cm.tab10(range(len(unique_owners)))
        color_map = dict(zip(unique_owners, colors))
        
        current_owner = None
        start_year = None
        
        # Plot segments for each ownership period
        for i, row in df.iterrows():
            if current_owner != row['owner']:
                if current_owner is not None:
                    plt.plot([start_year, row['year']], [1, 1], 
                             linewidth=10, solid_capstyle='butt',
                             color=color_map[current_owner], 
                             label=current_owner if current_owner not in plt.gca().get_legend_handles_labels()[1] else "")
                current_owner = row['owner']
                start_year = row['year']
        
        # Add the last segment
        if current_owner is not None:
            plt.plot([start_year, self.end_year], [1, 1], 
                     linewidth=10, solid_capstyle='butt',
                     color=color_map[current_owner], 
                     label=current_owner if current_owner not in plt.gca().#!/usr/bin/env python3
"""
Multi-Target OSINT Research Suite
---------------------------------
This program integrates property search, media archive search, and timeline generation
for historical property research in Huntington Beach, CA.

Primary targets:
- 17642 Beach Blvd, Huntington Beach, CA (1900-1950) 
- 17631 Cameron Lane, Huntington Beach, CA (1900-1940)
"""

import os
import json
import datetime
import webbrowser
import csv
import re
import logging
import argparse
import sys
import requests
import time
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("osint_research.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("osint_research")

# Directory structure
BASE_DIR = "17642_beach_research"
PROPERTY_RECORDS_DIR = os.path.join(BASE_DIR, "1_property_records")
BUSINESS_RECORDS_DIR = os.path.join(BASE_DIR, "2_business_records")
MEDIA_ARCHIVES_DIR = os.path.join(BASE_DIR, "3_media_archives")
CENSUS_DATA_DIR = os.path.join(BASE_DIR, "4_census_data")
MAPS_IMAGERY_DIR = os.path.join(BASE_DIR, "5_maps_imagery")
SOCIAL_MEDIA_DIR = os.path.join(BASE_DIR, "6_social_media")
CACHED_DATA_DIR = os.path.join(BASE_DIR, "7_cached_data")
REPORTS_DIR = os.path.join(BASE_DIR, "8_reports")
TIMELINES_DIR = os.path.join(BASE_DIR, "timelines")

# API endpoints and settings
APIS = {
    "assessor": "https://api.ocassessor.org/property/search",
    "redfin": "https://www.redfin.com/stingray/api/gis",
    "property_shark": "https://www.propertyshark.com/mason/Lookup/",
    "zillow": "https://www.zillow.com/homes/",
    "newspaper_archive": "https://newspaperarchive.com/api/v2/search",
    "historical_maps": "https://historicalmaps.arcgis.com/arcgis/rest/services/",
}

# Archive sources
SOURCES = {
    "newspapers": {
        "cdnc": "https://cdnc.ucr.edu",  # California Digital Newspaper Collection
        "chronicling_america": "https://chroniclingamerica.loc.gov/search/pages/results/",
        "newspaper_archive": "https://newspaperarchive.com/api/v2/search"
    },
    "web_archives": {
        "wayback_machine": "https://archive.org/wayback/available",
        "archive_today": "https://archive.today" 
    },
    "library_digital": {
        "huntington_library": "https://catalog.huntington.org/",
        "orange_county_archives": "https://ocarchives.com/digital-collections/"
    }
}
    def __init__(self, target_address: str, time_period: str):
        self.target_address = target_address
        self.time_period = time_period
        self.data_dir = "17642_beach_research"
        self.results_file = os.path.join(self.data_dir, "research_results.json")
        self.log_file = os.path.join(self.data_dir, "research_log.txt")
        self.categories = {
            "property_records": {
                "status": "in_progress",
                "items": {
                    "historical_ownership": {"completed": True, "data": {"Tanaka Family": "1940-1942, 1945-1950"}},
                    "current_property_status": {"completed": False, "data": {}},
                    "building_permits": {"completed": False, "data": {}},
                    "zoning_changes": {"completed": False, "data": {}},
                    "tax_assessment": {"completed": False, "data": {}}
                }
            },
            "business_records": {
                "status": "not_started",
                "items": {
                    "agricultural_permits": {"completed": False, "data": {}},
                    "business_licenses": {"completed": False, "data": {}},
                    "commercial_registrations": {"completed": False, "data": {}},
                    "operational_history": {"completed": False, "data": {}}
                }
            },
            "media_archives": {
                "status": "not_started",
                "items": {
                    "local_newspapers": {"completed": False, "data": {}},
                    "community_publications": {"completed": False, "data": {}},
                    "historical_photographs": {"completed": False, "data": {}},
                    "business_directories": {"completed": False, "data": {}}
                }
            },
            "census_data": {
                "status": "partial",
                "items": {
                    "household_1940": {"completed": True, "data": {"size": 7, "value": "$3,200"}},
                    "agricultural_census": {"completed": False, "data": {}},
                    "postwar_records": {"completed": False, "data": {}},
                    "modern_demographics": {"completed": False, "data": {}}
                }
            },
            "maps_imagery": {
                "status": "not_started",
                "items": {
                    "historical_maps": {"completed": False, "data": {}},
                    "aerial_photographs": {"completed": False, "data": {}},
                    "land_surveys": {"completed": False, "data": {}},
                    "modern_gis": {"completed": False, "data": {}}
                }
            },
            "social_media": {
                "status": "not_started",
                "items": {
                    "location_mentions": {"completed": False, "data": {}},
                    "historical_references": {"completed": False, "data": {}},
                    "community_discussions": {"completed": False, "data": {}},
                    "related_hashtags": {"completed": False, "data": {}}
                }
            },
            "cached_data": {
                "status": "not_started",
                "items": {
                    "archived_websites": {"completed": False, "data": {}},
                    "historical_databases": {"completed": False, "data": {}},
                    "digital_collections": {"completed": False, "data": {}},
                    "wayback_machine": {"completed": False, "data": {}}
                }
            },
            "reports": {
                "status": "in_progress",
                "items": {
                    "initial_findings": {"completed": True, "data": {"date": "2025-05-19"}},
                    "timeline_analysis": {"completed": False, "data": {}},
                    "property_history": {"completed": False, "data": {}},
                    "final_report": {"completed": False, "data": {}}
                }
            }
        }
        
        self.verified_info = {
            "property_owner": "Tanaka Family (1940-1942, 1945-1950)",
            "usage": "Strawberry farm (pre-war), Tomato/Pepper farm (post-war)",
            "size": "2.5 acres",
            "value_1940": "$3,200",
            "household_size": "7 members"
        }
        
        self.research_log = [
            {"date": "2025-05-19", "entry": "Initial OSINT structure created"},
            {"date": "2025-05-19", "entry": "Verified historical data imported from japanese_farmers_research"}
        ]
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing data if available
        self.load_data()

    def load_data(self) -> None:
        """Load existing research data if available."""
        if os.path.exists(self.results_file):
            try:
                with open(self.results_file, 'r') as f:
                    data = json.load(f)
                    self.categories = data.get('categories', self.categories)
                    self.verified_info = data.get('verified_info', self.verified_info)
                    print(f"Loaded existing research data from {self.results_file}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading data: {e}")
                
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    self.research_log = [{"date": line.split(': ')[0], "entry": line.split(': ')[1].strip()} 
                                        for line in f.readlines() if ': ' in line]
            except FileNotFoundError:
                pass

    def save_data(self) -> None:
        """Save current research data to file."""
        try:
            with open(self.results_file, 'w') as f:
                json.dump({
                    'categories': self.categories,
                    'verified_info': self.verified_info,
                    'target_address': self.target_address,
                    'time_period': self.time_period
                }, f, indent=2)
            print(f"Saved research data to {self.results_file}")
        except (IOError, PermissionError) as e:
            print(f"Error saving data: {e}")
            
    def save_log(self) -> None:
        """Save research log to file."""
        try:
            with open(self.log_file, 'w') as f:
                for entry in self.research_log:
                    f.write(f"{entry['date']}: {entry['entry']}\n")
            print(f"Saved research log to {self.log_file}")
        except (IOError, PermissionError) as e:
            print(f"Error saving log: {e}")

    def update_item(self, category: str, item: str, completed: bool, data: Dict[str, Any]) -> bool:
        """Update a specific research item with new data."""
        if category in self.categories and item in self.categories[category]['items']:
            self.categories[category]['items'][item]['completed'] = completed
            self.categories[category]['items'][item]['data'].update(data)
            
            # Update category status
            items = self.categories[category]['items']
            completed_items = sum(1 for i in items.values() if i['completed'])
            total_items = len(items)
            
            if completed_items == 0:
                self.categories[category]['status'] = "not_started"
            elif completed_items == total_items:
                self.categories[category]['status'] = "completed"
            else:
                self.categories[category]['status'] = "in_progress" if completed_items < total_items/2 else "partial"
            
            # Add log entry
            self.log_research(f"Updated {category}/{item} - Completed: {completed}")
            self.save_data()
            return True
        return False

    def update_verified_info(self, key: str, value: str) -> None:
        """Update verified information."""
        self.verified_info[key] = value
        self.log_research(f"Updated verified info: {key} = {value}")
        self.save_data()

    def log_research(self, entry: str) -> None:
        """Add an entry to the research log."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.research_log.append({"date": today, "entry": entry})
        self.save_log()

    def export_markdown(self, filename: str = "OSINT_TRACKER.md") -> None:
        """Export current research status to markdown file."""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                f.write(f"# {self.target_address} - OSINT Research Tracker\n")
                f.write(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
                
                # Verified Information
                f.write("## Verified Information\n")
                for key, value in self.verified_info.items():
                    f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
                
                f.write("\n## Research Categories & Status\n\n")
                
                # Categories
                for cat_key, cat_data in self.categories.items():
                    status_upper = cat_data['status'].upper().replace('_', ' ')
                    f.write(f"### {len(self.categories) + 1}. {cat_key.replace('_', ' ').title()} [{status_upper}]\n")
                    
                    for item_key, item_data in cat_data['items'].items():
                        check = "x" if item_data['completed'] else " "
                        f.write(f"- [{check}] {item_key.replace('_', ' ').title()}\n")
                    
                    f.write("\n")
                
                # Research Log
                f.write("## Research Log\n")
                for entry in self.research_log:
                    f.write(f"- {entry['date']}: {entry['entry']}\n")
                
            print(f"Exported markdown to {filepath}")
        except (IOError, PermissionError) as e:
            print(f"Error exporting markdown: {e}")

    def export_csv(self, filename: str = "research_data.csv") -> None:
        """Export research data to CSV file."""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Category", "Item", "Completed", "Data"])
                
                for cat_key, cat_data in self.categories.items():
                    for item_key, item_data in cat_data['items'].items():
                        data_str = ", ".join([f"{k}:{v}" for k, v in item_data['data'].items()])
                        writer.writerow([
                            cat_key.replace('_', ' ').title(),
                            item_key.replace('_', ' ').title(),
                            "Yes" if item_data['completed'] else "No",
                            data_str
                        ])
                
            print(f"Exported CSV to {filepath}")
        except (IOError, PermissionError) as e:
            print(f"Error exporting CSV: {e}")

    def generate_research_urls(self) -> Dict[str, List[str]]:
        """Generate useful research URLs for this address and time period."""
        address_encoded = self.target_address.replace(" ", "+")
        time_period_from, time_period_to = self.time_period.split("-")
        
        urls = {
            "property_records": [
                f"https://www.ocgov.com/residents/property/assessment",
                f"https://www.ocpublicworks.com/government/about/dept/ds",
                f"https://ocrcd.org/land-records"
            ],
            "historical_newspapers": [
                f"https://chroniclingamerica.loc.gov/search/pages/results/?state=California&date1={time_period_from}&date2={time_period_to}&proxtext={address_encoded}",
                f"https://www.newspapers.com/search/#query={address_encoded}&dr_year={time_period_from}-{time_period_to}",
                f"https://cdnc.ucr.edu/"
            ],
            "census_data": [
                f"https://www.archives.gov/research/census",
                f"https://www.census.gov/programs-surveys/decennial-census/decade/decennial-publications.html",
                f"https://www.ancestry.com/search/categories/35/"
            ],
            "maps_imagery": [
                f"https://www.loc.gov/maps/?q={address_encoded}",
                f"https://earthexplorer.usgs.gov/",
                f"https://digital.library.ucla.edu/search?f=region:Orange%20County"
            ],
            "wayback_machine": [
                f"https://web.archive.org/web/*/https://maps.google.com/?q={address_encoded}",
                f"https://archive.org/search.php?query={address_encoded}"
            ],
            "japanese_american_records": [
                "https://www.densho.org/archives/",
                "https://www.janm.org/collections",
                "https://oac.cdlib.org/findaid/ark:/13030/kt6z09r9kr/"
            ]
        }
        
        return urls

    def open_research_page(self, category: str, index: int = 0) -> None:
        """Open a specific research URL in the default browser."""
        urls = self.generate_research_urls()
        if category in urls and index < len(urls[category]):
            url = urls[category][index]
            webbrowser.open(url)
            self.log_research(f"Opened research URL: {url}")
        else:
            print(f"No URL found for {category} at index {index}")

    def search_pattern(self, pattern: str, text: str) -> List[str]:
        """Search for a pattern in text and return matches."""
        return re.findall(pattern, text)

    def analyze_census_data(self, census_text: str) -> Dict[str, Any]:
        """Extract relevant information from census data text."""
        result = {}
        
        # Look for family names
        family_pattern = r"(?:Head of Household|Family Name):\s*([A-Za-z\s]+)"
        families = self.search_pattern(family_pattern, census_text)
        if families:
            result["family_names"] = families
            
        # Look for occupations
        occupation_pattern = r"Occupation:\s*([A-Za-z\s]+)"
        occupations = self.search_pattern(occupation_pattern, census_text)
        if occupations:
            result["occupations"] = occupations
            
        # Look for property values
        value_pattern = r"Value:\s*\$([0-9,\.]+)"
        values = self.search_pattern(value_pattern, census_text)
        if values:
            result["property_values"] = [f"${v}" for v in values]
            
        # Look for land usage
        usage_pattern = r"Usage:\s*([A-Za-z\s/]+)"
        usages = self.search_pattern(usage_pattern, census_text)
        if usages:
            result["land_usage"] = usages
            
        return result

    def display_categories(self) -> None:
        """Display all research categories with their status."""
        print(f"\n{'='*50}")
        print(f"OSINT Research Tracker: {self.target_address} ({self.time_period})")
        print(f"{'='*50}")
        
        for cat_key, cat_data in self.categories.items():
            status_display = cat_data['status'].upper().replace('_', ' ')
            print(f"\n{cat_key.replace('_', ' ').title()} [{status_display}]")
            print('-' * 40)
            
            for item_key, item_data in cat_data['items'].items():
                status = "✓" if item_data['completed'] else "✗"
                data_str = ", ".join([f"{k}: {v}" for k, v in item_data['data'].items()]) if item_data['data'] else "No data"
                print(f"{status} {item_key.replace('_', ' ').title()}: {data_str}")

    def display_verified_info(self) -> None:
        """Display verified information."""
        print(f"\n{'='*50}")
        print(f"Verified Information for {self.target_address}")
        print(f"{'='*50}")
        
        for key, value in self.verified_info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def display_research_log(self) -> None:
        """Display the research log."""
        print(f"\n{'='*50}")
        print(f"Research Log for {self.target_address}")
        print(f"{'='*50}")
        
        for entry in self.research_log:
            print(f"{entry['date']}: {entry['entry']}")


# Main interface function
def main() -> None:
    address = "17642 Beach Blvd, Huntington Beach, CA"
    time_period = "1900-1950"
    
    print(f"\n{'*'*70}")
    print(f"* OSINT Research Tool for {address} ({time_period})")
    print(f"{'*'*70}")
    
    tracker = OSINTTracker(address, time_period)
    
    while True:
        print("\nOptions:")
        print("1. Display Research Categories")
        print("2. Display Verified Information")
        print("3. Display Research Log")
        print("4. Update Research Item")
        print("5. Update Verified Information")
        print("6. Generate Research URLs")
        print("7. Export to Markdown")
        print("8. Export to CSV")
        print("9. Add Research Log Entry")
        print("0. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == "1":
            tracker.display_categories()
        
        elif choice == "2":
            tracker.display_verified_info()
        
        elif choice == "3":
            tracker.display_research_log()
        
        elif choice == "4":
            print("\nCategories:")
            for i, cat in enumerate(tracker.categories.keys(), 1):
                print(f"{i}. {cat.replace('_', ' ').title()}")
            
            cat_idx = int(input("Select category (number): ")) - 1
            if 0 <= cat_idx < len(tracker.categories):
                cat_key = list(tracker.categories.keys())[cat_idx]
                
                print(f"\nItems in {cat_key.replace('_', ' ').title()}:")
                items = list(tracker.categories[cat_key]['items'].keys())
                for i, item in enumerate(items, 1):
                    print(f"{i}. {item.replace('_', ' ').title()}")
                
                item_idx = int(input("Select item (number): ")) - 1
                if 0 <= item_idx < len(items):
                    item_key = items[item_idx]
                    
                    completed = input("Mark as completed? (y/n): ").lower() == 'y'
                    
                    print("Enter data (key=value format, empty line to finish):")
                    data = {}
                    while True:
                        data_line = input()
                        if not data_line:
                            break
                        
                        if '=' in data_line:
                            k, v = data_line.split('=', 1)
                            data[k.strip()] = v.strip()
                    
                    tracker.update_item(cat_key, item_key, completed, data)
                    print(f"Updated {cat_key}/{item_key}")
                else:
                    print("Invalid item selection")
            else:
                print("Invalid category selection")
        
        elif choice == "5":
            key = input("Enter information key (e.g., property_owner): ")
            value = input("Enter value: ")
            tracker.update_verified_info(key, value)
            print(f"Updated verified information: {key}")
        
        elif choice == "6":
            urls = tracker.generate_research_urls()
            print("\nResearch URLs:")
            for category, url_list in urls.items():
                print(f"\n{category.replace('_', ' ').title()}:")
                for i, url in enumerate(url_list, 1):
                    print(f"{i}. {url}")
                
                open_url = input("Open URL? (number, or 0 to skip): ")
                if open_url.isdigit() and int(open_url) > 0 and int(open_url) <= len(url_list):
                    tracker.open_research_page(category, int(open_url) - 1)
        
        elif choice == "7":
            filename = input("Enter filename (default: OSINT_TRACKER.md): ") or "OSINT_TRACKER.md"
            tracker.export_markdown(filename)
        
        elif choice == "8":
            filename = input("Enter filename (default: research_data.csv): ") or "research_data.csv"
            tracker.export_csv(filename)
        
        elif choice == "9":
            entry = input("Enter log entry: ")
            tracker.log_research(entry)
            print("Added research log entry")
        
        elif choice == "0":
            tracker.save_data()
            tracker.save_log()
            print("Exiting OSINT Research Tool. Data saved.")
            break
        
        else:
            print("Invalid choice, please try again.")


if __name__ == "__main__":
    main()

