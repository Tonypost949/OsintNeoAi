import logging
from database import init_db, add_sample_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_init.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_init")

def main():
    """Initialize database and add sample data."""
    logger.info("Initializing database...")
    
    # Create database tables
    if init_db():
        logger.info("Database tables created successfully")
        
        # Add sample data
        if add_sample_data():
            logger.info("Sample data added successfully")
        else:
            logger.error("Failed to add sample data")
    else:
        logger.error("Failed to initialize database")

if __name__ == "__main__":
    main()