#!/usr/bin/env python3
"""
Database initialization script for Water Pump Management System
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import db
import logging

def setup_logging():
    """Setup logging for database initialization"""
    logs_dir = Path(__file__).parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'db_init.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Initialize database"""
    logger = setup_logging()
    
    print("Water Pump Management System - Database Initialization")
    print("=" * 60)
    
    try:
        logger.info("Starting database initialization...")
        
        # Initialize database
        if db.init_database():
            print("✅ Database initialized successfully!")
            print("✅ All tables created")
            print("✅ Default data inserted")
            logger.info("Database initialization completed successfully")
        else:
            print("❌ Failed to initialize database")
            logger.error("Database initialization failed")
            sys.exit(1)
            
        print("\nDatabase Configuration:")
        print("- Host: localhost")
        print("- Port: 3306")
        print("- Database: water_pump_db")
        print("- Default Admin: ADMIN001 / admin123")
        
        print("\nYou can now run the application using:")
        print("python src/main.py")
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()