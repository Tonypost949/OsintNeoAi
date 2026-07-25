from typing import List, Tuple, TextIO
import re
import logging

# Initialize logger
logger = logging.getLogger("utils")

def load_addresses(file_obj: TextIO) -> List[str]:
    """Load addresses from a text file (one per line)."""
    addresses = []
    
    for line in file_obj:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
            
        # Check if the line contains a date range at the end (e.g., "(1900-1940)")
        date_range_match = re.search(r'\((\d{4})-(\d{4})\)$', line)
        if date_range_match:
            # Remove the date range part for the actual address
            address = line[:date_range_match.start()].strip()
        else:
            address = line
            
        if address:
            addresses.append(address)
    
    logger.info(f"Loaded {len(addresses)} addresses from file")
    return addresses

def parse_address_list(text: str) -> List[str]:
    """Parse a string containing multiple addresses (one per line)."""
    if not text:
        return []
        
    lines = text.split('\n')
    addresses = []
    
    for line in lines:
        line = line.strip()
        if line:
            # Check if the line contains a date range at the end (e.g., "(1900-1940)")
            date_range_match = re.search(r'\((\d{4})-(\d{4})\)$', line)
            if date_range_match:
                # Remove the date range part for the actual address
                address = line[:date_range_match.start()].strip()
            else:
                address = line
                
            if address:
                addresses.append(address)
    
    return addresses

def extract_date_range(address_line: str) -> Tuple[str, int, int]:
    """Extract address and date range from a line.
    
    Returns:
        Tuple of (address, start_year, end_year)
    """
    # Default time period if not specified
    start_year, end_year = 1900, 2023
    
    # Check if the line contains a date range at the end (e.g., "(1900-1940)")
    date_range_match = re.search(r'\((\d{4})-(\d{4})\)$', address_line)
    
    if date_range_match:
        # Extract the date range
        start_year = int(date_range_match.group(1))
        end_year = int(date_range_match.group(2))
        
        # Remove the date range part for the actual address
        address = address_line[:date_range_match.start()].strip()
    else:
        address = address_line.strip()
    
    return address, start_year, end_year

def validate_year_range(start_year: int, end_year: int) -> bool:
    """Validate the year range is logical."""
    if start_year > end_year:
        return False
    
    current_year = 2023  # You could use datetime.now().year for more accuracy
    
    if start_year < 1700 or end_year > current_year + 10:  # Allow some future prediction
        return False
        
    return True

def extract_location_from_address(address: str) -> Tuple[str, str, str]:
    """Extract city, state, and zip code from an address string.
    
    Returns:
        Tuple of (city, state, zip_code)
    """
    # This is a very simplistic parser and would need to be more robust in production
    # Best approach would be to use a dedicated address parsing library
    
    city, state, zip_code = "", "", ""
    
    # Try to match state abbreviation (2 uppercase letters)
    state_match = re.search(r'\b([A-Z]{2})\b', address)
    if state_match:
        state = state_match.group(1)
        
        # Look for zip code after state (5 digits)
        zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address[state_match.end():])
        if zip_match:
            zip_code = zip_match.group(1)
            
        # City is typically the word before the state
        city_end = state_match.start()
        address_before_state = address[:city_end].strip()
        
        # The city is probably the last word group before the state
        city_match = re.search(r'([A-Za-z\s]+)$', address_before_state)
        if city_match:
            city = city_match.group(1).strip()
    
    return city, state, zip_code
