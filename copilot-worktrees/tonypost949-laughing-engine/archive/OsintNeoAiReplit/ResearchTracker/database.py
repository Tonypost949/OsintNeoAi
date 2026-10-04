import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date, Text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

# Configure logging
logger = logging.getLogger("database")

# Get database URL from environment variable
database_url = os.getenv("DATABASE_URL")
if not database_url:
    logger.error("DATABASE_URL environment variable not set")
    raise ValueError("DATABASE_URL environment variable not set")

# Create SQLAlchemy engine
engine = create_engine(database_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Property(Base):
    """Property model representing a real estate property."""
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    address = Column(String(255), nullable=False, unique=True)
    city = Column(String(100))
    state = Column(String(20))
    zip_code = Column(String(20))
    start_year = Column(Integer)
    end_year = Column(Integer)
    created_at = Column(Date, default=datetime.now().date())
    
    # Relationships
    agricultural_data = relationship("AgriculturalData", back_populates="property", cascade="all, delete-orphan")
    commercial_usage = relationship("CommercialUsage", back_populates="property", cascade="all, delete-orphan")
    historical_events = relationship("HistoricalEvent", back_populates="property", cascade="all, delete-orphan")
    value_history = relationship("PropertyValue", back_populates="property", cascade="all, delete-orphan")
    water_wells = relationship("WaterWell", back_populates="property", cascade="all, delete-orphan")
    newspaper_archives = relationship("NewspaperRecord", back_populates="property", cascade="all, delete-orphan")
    web_archives = relationship("WebArchive", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(address='{self.address}', period='{self.start_year}-{self.end_year}')>"
    
    def to_dict(self):
        """Convert property to dictionary."""
        return {
            "id": self.id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "start_year": self.start_year,
            "end_year": self.end_year,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class AgriculturalData(Base):
    """Agricultural data for a property."""
    __tablename__ = 'agricultural_data'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    time_period = Column(String(20))
    crop_type = Column(String(255))
    acreage = Column(Float)
    soil_type = Column(String(100))
    irrigation = Column(String(100))
    annual_yield = Column(String(100))
    
    # Relationship
    property = relationship("Property", back_populates="agricultural_data")
    
    def __repr__(self):
        return f"<AgriculturalData(crop='{self.crop_type}', period='{self.time_period}')>"
    
    def to_dict(self):
        """Convert agricultural data to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "time_period": self.time_period,
            "crop_type": self.crop_type,
            "acreage": self.acreage,
            "soil_type": self.soil_type,
            "irrigation": self.irrigation,
            "annual_yield": self.annual_yield
        }

class CommercialUsage(Base):
    """Commercial usage data for a property."""
    __tablename__ = 'commercial_usage'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    time_period = Column(String(20))
    business_name = Column(String(255))
    business_type = Column(String(100))
    commercial_activity = Column(String(255))
    employees = Column(Integer)
    
    # Relationship
    property = relationship("Property", back_populates="commercial_usage")
    
    def __repr__(self):
        return f"<CommercialUsage(business='{self.business_name}', period='{self.time_period}')>"
    
    def to_dict(self):
        """Convert commercial usage to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "time_period": self.time_period,
            "business_name": self.business_name,
            "business_type": self.business_type,
            "commercial_activity": self.commercial_activity,
            "employees": self.employees
        }

class HistoricalEvent(Base):
    """Historical events related to a property."""
    __tablename__ = 'historical_events'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    date = Column(String(20))
    description = Column(String(255))
    details = Column(Text)
    
    # Relationship
    property = relationship("Property", back_populates="historical_events")
    
    def __repr__(self):
        return f"<HistoricalEvent(date='{self.date}', description='{self.description}')>"
    
    def to_dict(self):
        """Convert historical event to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "date": self.date,
            "description": self.description,
            "details": self.details
        }

class PropertyValue(Base):
    """Property value history."""
    __tablename__ = 'property_values'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    year = Column(Integer)
    assessed_value = Column(Float)
    
    # Relationship
    property = relationship("Property", back_populates="value_history")
    
    def __repr__(self):
        return f"<PropertyValue(year='{self.year}', value='{self.assessed_value}')>"
    
    def to_dict(self):
        """Convert property value to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "year": self.year,
            "assessed_value": self.assessed_value
        }

class WaterWell(Base):
    """Water well information for a property."""
    __tablename__ = 'water_wells'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    installation_year = Column(Integer)
    depth = Column(Float)
    water_quality = Column(String(100))
    flow_rate = Column(String(100))
    status = Column(String(100))
    notes = Column(Text)
    
    # Relationship
    property = relationship("Property", back_populates="water_wells")
    
    def __repr__(self):
        return f"<WaterWell(year='{self.installation_year}', depth='{self.depth}')>"
    
    def to_dict(self):
        """Convert water well to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "installation_year": self.installation_year,
            "depth": self.depth,
            "water_quality": self.water_quality,
            "flow_rate": self.flow_rate,
            "status": self.status,
            "notes": self.notes
        }

class NewspaperRecord(Base):
    """Newspaper archive record related to a property."""
    __tablename__ = 'newspaper_archives'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    date = Column(String(20))
    source = Column(String(255))
    headline = Column(String(255))
    snippet = Column(Text)
    
    # Relationship
    property = relationship("Property", back_populates="newspaper_archives")
    
    def __repr__(self):
        return f"<NewspaperRecord(date='{self.date}', headline='{self.headline}')>"
    
    def to_dict(self):
        """Convert newspaper record to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "date": self.date,
            "source": self.source,
            "headline": self.headline,
            "snippet": self.snippet
        }

class WebArchive(Base):
    """Web archive record related to a property."""
    __tablename__ = 'web_archives'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    date = Column(String(20))
    url = Column(String(255))
    title = Column(String(255))
    snippet = Column(Text)
    
    # Relationship
    property = relationship("Property", back_populates="web_archives")
    
    def __repr__(self):
        return f"<WebArchive(date='{self.date}', title='{self.title}')>"
    
    def to_dict(self):
        """Convert web archive to dictionary."""
        return {
            "id": self.id,
            "property_id": self.property_id,
            "date": self.date,
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet
        }

def init_db():
    """Initialize the database by creating all tables."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

def add_property(address, city=None, state=None, zip_code=None, start_year=1900, end_year=2025):
    """Add a new property to the database."""
    try:
        session = Session()
        
        # Check if property already exists
        existing = session.query(Property).filter_by(address=address).first()
        if existing:
            logger.info(f"Property with address {address} already exists")
            session.close()
            return existing.id
        
        # Create new property
        new_property = Property(
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            start_year=start_year,
            end_year=end_year
        )
        
        session.add(new_property)
        session.commit()
        property_id = new_property.id
        session.close()
        
        logger.info(f"Added property {address} with ID {property_id}")
        return property_id
    
    except Exception as e:
        logger.error(f"Error adding property {address}: {str(e)}")
        session.rollback()
        session.close()
        return None

def add_sample_data():
    """Add sample data to the database for demonstration purposes."""
    try:
        # Add properties
        prop1_id = add_property(
            "17642 Beach Blvd", 
            "Huntington Beach", 
            "CA", 
            "92647", 
            1900, 
            1940
        )
        
        prop2_id = add_property(
            "17631 Cameron Lane", 
            "Huntington Beach", 
            "CA", 
            "92647", 
            1900, 
            1940
        )
        
        if not prop1_id or not prop2_id:
            logger.error("Failed to add sample properties")
            return False
        
        session = Session()
        
        # Add agricultural data for first property
        session.add_all([
            AgriculturalData(
                property_id=prop1_id,
                time_period="1900-1915",
                crop_type="Beans, Cabbage",
                acreage=25,
                soil_type="Loamy Sand",
                irrigation="Well-based",
                annual_yield="750 bushels"
            ),
            AgriculturalData(
                property_id=prop1_id,
                time_period="1916-1925",
                crop_type="Lima Beans, Celery",
                acreage=30,
                soil_type="Loamy Sand",
                irrigation="Well-based",
                annual_yield="900 bushels"
            ),
            AgriculturalData(
                property_id=prop1_id,
                time_period="1926-1940",
                crop_type="Celery, Cabbage, Strawberries",
                acreage=35,
                soil_type="Loamy Sand",
                irrigation="Well-based with pump system",
                annual_yield="1200 bushels"
            )
        ])
        
        # Add commercial usage for first property
        session.add_all([
            CommercialUsage(
                property_id=prop1_id,
                time_period="1900-1910",
                business_name="Beach Blvd General Store",
                business_type="General Store",
                commercial_activity="Selling farm supplies and groceries",
                employees=3
            ),
            CommercialUsage(
                property_id=prop1_id,
                time_period="1911-1925",
                business_name="Huntington Produce Market",
                business_type="Farmers Market",
                commercial_activity="Selling locally grown produce",
                employees=5
            ),
            CommercialUsage(
                property_id=prop1_id,
                time_period="1926-1940",
                business_name="Beach Boulevard Farming Supply",
                business_type="Agricultural Supplies",
                commercial_activity="Selling farming equipment and supplies",
                employees=8
            )
        ])
        
        # Add historical events for first property
        session.add_all([
            HistoricalEvent(
                property_id=prop1_id,
                date="1908",
                description="First artesian well installed",
                details="A 120-foot deep artesian well was installed to provide irrigation for crops"
            ),
            HistoricalEvent(
                property_id=prop1_id,
                date="1917",
                description="Property expanded agricultural operations",
                details="Additional 10 acres purchased from neighboring farm to expand celery production"
            ),
            HistoricalEvent(
                property_id=prop1_id,
                date="1929",
                description="Modern irrigation system installed",
                details="Electric pumps and piping system replaced older well-drawing methods"
            ),
            HistoricalEvent(
                property_id=prop1_id,
                date="1938",
                description="Survived major Southern California flood",
                details="Property remained operational despite regional flooding damage"
            )
        ])
        
        # Add property values for first property
        session.add_all([
            PropertyValue(property_id=prop1_id, year=1900, assessed_value=1200),
            PropertyValue(property_id=prop1_id, year=1910, assessed_value=2500),
            PropertyValue(property_id=prop1_id, year=1920, assessed_value=4800),
            PropertyValue(property_id=prop1_id, year=1930, assessed_value=6500),
            PropertyValue(property_id=prop1_id, year=1940, assessed_value=8900)
        ])
        
        # Add water wells for first property
        session.add_all([
            WaterWell(
                property_id=prop1_id,
                installation_year=1908,
                depth=120,
                water_quality="Excellent",
                flow_rate="15 gallons/minute",
                status="Active until 1929",
                notes=""
            ),
            WaterWell(
                property_id=prop1_id,
                installation_year=1929,
                depth=150,
                water_quality="Excellent",
                flow_rate="25 gallons/minute",
                status="Active through 1940s",
                notes="Electric pump system installed"
            )
        ])
        
        # Add newspaper archives for first property
        session.add_all([
            NewspaperRecord(
                property_id=prop1_id,
                date="1912-05-15",
                source="Huntington Beach News",
                headline="New Artesian Well Improves Farm Output",
                snippet="The McAllister farm at 17642 Beach Boulevard has reported increased crop yields following the installation of a new artesian well system reaching depths of 120 feet. Local farmers are taking notice of the innovative irrigation method."
            ),
            NewspaperRecord(
                property_id=prop1_id,
                date="1925-08-03",
                source="Orange County Register",
                headline="Produce Market Expansion",
                snippet="The Huntington Produce Market on Beach Boulevard has expanded its operations to include a wider variety of local vegetables. Owner Thomas Henderson attributes success to relationships with local farms including the property at 17642 Beach."
            ),
            NewspaperRecord(
                property_id=prop1_id,
                date="1937-11-20",
                source="Farm Weekly Gazette",
                headline="Modern Irrigation Systems Transform Local Agriculture",
                snippet="Several Huntington Beach farms have adopted electric pump systems for well irrigation. The property at 17642 Beach Blvd was among the first to install such a system in 1929 and has seen consistently higher yields as a result."
            )
        ])
        
        # Add web archives for first property
        session.add_all([
            WebArchive(
                property_id=prop1_id,
                date="2001-05-18",
                url="http://orangecountyhistory.org/huntington_farms_1900_1950.html",
                title="Huntington Beach Historical Farms (1900-1950)",
                snippet="...Among the most notable early farms was the property at 17642 Beach Boulevard, which pioneered irrigation techniques that transformed local agriculture..."
            ),
            WebArchive(
                property_id=prop1_id,
                date="2005-11-03",
                url="http://huntingtonbeacharchives.org/historical_wells.html",
                title="Water Resources in Early Huntington Beach Development",
                snippet="...The 1908 artesian well at the Beach Boulevard farm (17642) was among the first in the region to demonstrate the viability of deep-well irrigation for intensive vegetable farming..."
            )
        ])
        
        # Add agricultural data for second property
        session.add_all([
            AgriculturalData(
                property_id=prop2_id,
                time_period="1900-1920",
                crop_type="Potatoes, Corn",
                acreage=18,
                soil_type="Sandy Loam",
                irrigation="Well-based",
                annual_yield="550 bushels"
            ),
            AgriculturalData(
                property_id=prop2_id,
                time_period="1921-1935",
                crop_type="Sugar Beets, Corn",
                acreage=22,
                soil_type="Sandy Loam",
                irrigation="Well with windmill pump",
                annual_yield="700 bushels"
            ),
            AgriculturalData(
                property_id=prop2_id,
                time_period="1936-1940",
                crop_type="Sugar Beets, Cabbage, Lettuce",
                acreage=25,
                soil_type="Sandy Loam",
                irrigation="Improved well system",
                annual_yield="850 bushels"
            )
        ])
        
        # Add commercial usage for second property
        session.add_all([
            CommercialUsage(
                property_id=prop2_id,
                time_period="1900-1915",
                business_name="Cameron Family Farm",
                business_type="Family Farm",
                commercial_activity="Local produce sales",
                employees=2
            ),
            CommercialUsage(
                property_id=prop2_id,
                time_period="1916-1930",
                business_name="Cameron Vegetable Stand",
                business_type="Farm Stand",
                commercial_activity="Direct-to-consumer produce sales",
                employees=4
            ),
            CommercialUsage(
                property_id=prop2_id,
                time_period="1931-1940",
                business_name="Cameron Agricultural Cooperative",
                business_type="Farming Cooperative",
                commercial_activity="Collective farming and distribution",
                employees=12
            )
        ])
        
        # Add historical events for second property
        session.add_all([
            HistoricalEvent(
                property_id=prop2_id,
                date="1904",
                description="First water well drilled",
                details="A 100-foot deep well was installed to support initial farming operations"
            ),
            HistoricalEvent(
                property_id=prop2_id,
                date="1915",
                description="Windmill pump installed",
                details="Windmill-powered pump system improved irrigation capabilities"
            ),
            HistoricalEvent(
                property_id=prop2_id,
                date="1925",
                description="Farm ownership transferred",
                details="Property transferred from original Cameron family to Henderson family"
            ),
            HistoricalEvent(
                property_id=prop2_id,
                date="1933",
                description="Joined regional agricultural cooperative",
                details="Farm joined with 5 other local farms to form Huntington Agricultural Cooperative"
            )
        ])
        
        # Add property values for second property
        session.add_all([
            PropertyValue(property_id=prop2_id, year=1900, assessed_value=950),
            PropertyValue(property_id=prop2_id, year=1910, assessed_value=1800),
            PropertyValue(property_id=prop2_id, year=1920, assessed_value=3600),
            PropertyValue(property_id=prop2_id, year=1930, assessed_value=5200),
            PropertyValue(property_id=prop2_id, year=1940, assessed_value=7500)
        ])
        
        # Add water wells for second property
        session.add_all([
            WaterWell(
                property_id=prop2_id,
                installation_year=1904,
                depth=100,
                water_quality="Good",
                flow_rate="12 gallons/minute",
                status="Active until 1925",
                notes=""
            ),
            WaterWell(
                property_id=prop2_id,
                installation_year=1915,
                depth=110,
                water_quality="Good",
                flow_rate="14 gallons/minute",
                status="Secondary well, abandoned 1930",
                notes="Windmill-powered pump"
            ),
            WaterWell(
                property_id=prop2_id,
                installation_year=1925,
                depth=135,
                water_quality="Excellent",
                flow_rate="18 gallons/minute",
                status="Active through 1940s",
                notes="Replaced original 1904 well"
            )
        ])
        
        # Add newspaper archives for second property
        session.add_all([
            NewspaperRecord(
                property_id=prop2_id,
                date="1905-06-10",
                source="Huntington Beach Chronicle",
                headline="Cameron Family Establishes New Farm",
                snippet="The Cameron family has established a new farming operation at 17631 Cameron Lane, focusing on potato and corn production. The family has invested in modern well-drilling equipment to ensure adequate irrigation."
            ),
            NewspaperRecord(
                property_id=prop2_id,
                date="1916-09-22",
                source="Agricultural Times",
                headline="Windmill Technology Improves Farm Output",
                snippet="The Cameron farm on Cameron Lane has reported a 20% increase in crop yields after installing a windmill-powered pump system. Other local farmers are expressing interest in the technology."
            ),
            NewspaperRecord(
                property_id=prop2_id,
                date="1933-03-14",
                source="County Business Journal",
                headline="Local Farms Form Cooperative",
                snippet="Six farms in the Huntington Beach area have joined to form the Huntington Agricultural Cooperative. The Henderson family farm at 17631 Cameron Lane (formerly Cameron Family Farm) is among the founding members."
            )
        ])
        
        # Add web archives for second property
        session.add_all([
            WebArchive(
                property_id=prop2_id,
                date="2003-07-22",
                url="http://orangecountyhistory.org/cameron_family_farms.html",
                title="Cameron Family Agricultural Legacy",
                snippet="...The original Cameron family homestead at 17631 Cameron Lane operated from 1900 until 1925, when ownership transferred to the Henderson family..."
            ),
            WebArchive(
                property_id=prop2_id,
                date="2008-04-15",
                url="http://huntingtonbeacharchives.org/agricultural_coops_1930s.html",
                title="Depression-Era Agricultural Cooperatives in Orange County",
                snippet="...The Henderson farm at the former Cameron property (17631 Cameron Lane) was instrumental in forming one of the most successful local farming cooperatives in 1933..."
            )
        ])
        
        session.commit()
        session.close()
        
        logger.info("Sample data added successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error adding sample data: {str(e)}")
        session.rollback()
        session.close()
        return False

def get_property_data(property_id=None, address=None):
    """Get property data from the database.
    
    Args:
        property_id: Optional property ID
        address: Optional property address
        
    Returns:
        Dictionary containing all property data
    """
    session = Session()
    
    try:
        # Find property by ID or address
        if property_id:
            property_obj = session.query(Property).filter_by(id=property_id).first()
        elif address:
            property_obj = session.query(Property).filter_by(address=address).first()
        else:
            session.close()
            return None
        
        if not property_obj:
            session.close()
            return None
        
        # Gather all related data
        result = property_obj.to_dict()
        
        # Agricultural data
        result["agricultural_data"] = [item.to_dict() for item in property_obj.agricultural_data]
        
        # Commercial usage
        result["commercial_usage"] = [item.to_dict() for item in property_obj.commercial_usage]
        
        # Historical events
        result["historical_events"] = [item.to_dict() for item in property_obj.historical_events]
        
        # Property values
        result["value_history"] = [item.to_dict() for item in property_obj.value_history]
        
        # Water wells
        result["water_wells"] = [item.to_dict() for item in property_obj.water_wells]
        
        # Newspaper archives
        result["newspaper_archives"] = [item.to_dict() for item in property_obj.newspaper_archives]
        
        # Web archives
        result["web_archives"] = [item.to_dict() for item in property_obj.web_archives]
        
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting property data: {str(e)}")
        session.close()
        return None

def get_all_properties():
    """Get all properties from the database.
    
    Returns:
        List of property dictionaries
    """
    session = Session()
    
    try:
        properties = session.query(Property).all()
        result = [property_obj.to_dict() for property_obj in properties]
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error getting all properties: {str(e)}")
        session.close()
        return []

def search_properties(query=None, start_year=None, end_year=None):
    """Search for properties in the database.
    
    Args:
        query: Optional search query for address, city, state, or zip
        start_year: Optional minimum start year
        end_year: Optional maximum end year
        
    Returns:
        List of matching property dictionaries
    """
    session = Session()
    
    try:
        # Build query filters
        filters = []
        
        if query:
            # Search in address, city, state, or zip
            filters.append(
                (Property.address.ilike(f"%{query}%")) | 
                (Property.city.ilike(f"%{query}%")) | 
                (Property.state.ilike(f"%{query}%")) | 
                (Property.zip_code.ilike(f"%{query}%"))
            )
        
        if start_year:
            filters.append(Property.start_year >= start_year)
        
        if end_year:
            filters.append(Property.end_year <= end_year)
        
        # Execute query
        properties = session.query(Property).filter(*filters).all()
        result = [property_obj.to_dict() for property_obj in properties]
        session.close()
        return result
    
    except Exception as e:
        logger.error(f"Error searching properties: {str(e)}")
        session.close()
        return []

# Initialize database when this module is imported
if database_url:
    init_db()