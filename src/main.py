#!/usr/bin/env python3
"""
Water Pump Management System
Main entry point for the application
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from main_window import MainWindow
from database import db
import logging

def setup_logging():
    """Setup application logging"""
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).parent.parent / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / 'application.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'PySide6',
        'mysql.connector',
        'pandas',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nPlease install missing packages using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Water Pump Management System")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Water Pump Management System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Water Management Solutions")
    
    # Set application style
    app.setStyle('Fusion')
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        if not db.init_database():
            logger.error("Failed to initialize database")
            sys.exit(1)
        
        logger.info("Database initialized successfully")
        
        # Create and show main window
        logger.info("Creating main window...")
        window = MainWindow()
        window.show()
        
        logger.info("Application started successfully")
        
        # Start application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()