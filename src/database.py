import mysql.connector
from mysql.connector import Error
import logging
import os
from datetime import datetime
from config import DB_CONFIG
import json

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/database.log'),
                logging.StreamHandler()
            ]
        )
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                self.logger.info("Database connection established")
                return True
        except Error as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.logger.info("Database connection closed")
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Error as e:
            self.logger.error(f"Query execution failed: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Execute an update/insert query"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            self.logger.error(f"Update execution failed: {e}")
            self.connection.rollback()
            return False
    
    def init_database(self):
        """Initialize database tables"""
        try:
            # First connect to MySQL server (without database)
            temp_config = DB_CONFIG.copy()
            temp_config['database'] = None
            
            connection = mysql.connector.connect(**temp_config)
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")

            cursor.execute(f"USE {DB_CONFIG['database']}")
            
            # Create tables
            self.create_tables(connection)
            
            cursor.close()
            connection.close()
            
            return True
        except Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def create_tables(self, connection):
        """Create all necessary tables"""
        cursor = connection.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_id VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(50),
                job_type VARCHAR(50),
                email VARCHAR(100),
                role ENUM('technician', 'supervisor', 'admin') DEFAULT 'technician',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Water pumps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS water_pumps (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pump_name VARCHAR(100) NOT NULL,
                location VARCHAR(200),
                status ENUM('online', 'offline', 'maintenance', 'error') DEFAULT 'offline',
                last_maintenance DATE,
                next_maintenance DATE,
                operating_hours FLOAT DEFAULT 0,
                pressure_level FLOAT,
                flow_rate FLOAT,
                temperature FLOAT,
                power_consumption FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # Maintenance schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_schedule (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pump_id INT,
                maintenance_type VARCHAR(50) NOT NULL,
                scheduled_date DATE NOT NULL,
                assigned_technician_id INT,
                description TEXT,
                status ENUM('scheduled', 'in_progress', 'completed', 'overdue') DEFAULT 'scheduled',
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                estimated_duration INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pump_id) REFERENCES water_pumps(id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_technician_id) REFERENCES users(id)
            )
        """)
        
        # Inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                part_number VARCHAR(50) UNIQUE NOT NULL,
                part_name VARCHAR(200) NOT NULL,
                category VARCHAR(50),
                quantity INT NOT NULL DEFAULT 0,
                min_quantity INT DEFAULT 5,
                unit_price DECIMAL(10,2),
                supplier VARCHAR(100),
                location VARCHAR(100),
                last_restocked DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                action VARCHAR(100) NOT NULL,
                details TEXT,
                severity ENUM('info', 'warning', 'error', 'critical') DEFAULT 'info',
                ip_address VARCHAR(45),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Pump readings table (for Arduino data)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pump_readings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pump_id INT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                pressure FLOAT,
                flow_rate FLOAT,
                temperature FLOAT,
                power_consumption FLOAT,
                status VARCHAR(20),
                FOREIGN KEY (pump_id) REFERENCES water_pumps(id) ON DELETE CASCADE
            )
        """)
        
        # Notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                type ENUM('info', 'warning', 'error', 'maintenance', 'inventory') DEFAULT 'info',
                priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Reports table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports(
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_name VARCHAR(200) NOT NULL,
                report_type VARCHAR(50) NOT NULL,
                start_date DATE,
                end_date DATE,
                description TEXT,
                generated_by INT,
                status ENUM('pending', 'processing', 'completed',  'failed') 
                DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                FOREIGN KEY ( generated_by ) 
                REFERENCES users(id) ON DELETE SET NULL)
        """)
        
        # Insert default data
        self.insert_default_data(cursor)
        
        connection.commit()
        cursor.close()
    
    def insert_default_data(self, cursor):
        """Insert default data for testing"""
        # Check if admin user exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE job_id = 'ADMIN001'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (job_id, password, name, department, job_type, role, email)
                VALUES ('ADMIN001', 'admin123', 'System Administrator', 'IT', 'Administrator', 'admin', 'admin@company.com')
            """)
        
        # Check if test pumps exist
        cursor.execute("SELECT COUNT(*) FROM water_pumps")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO water_pumps (pump_name, location, status, operating_hours)
                VALUES 
                ('Main Pump #1', 'Building A - Basement', 'online', 1250.5),
                ('Main Pump #2', 'Building B - Basement', 'offline', 850.2)
            """)
        
        # Check if inventory items exist
        cursor.execute("SELECT COUNT(*) FROM inventory")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO inventory (part_number, part_name, category, quantity, min_quantity, unit_price, supplier, location)
                VALUES 
                ('PMP-001', 'Water Pump Motor', 'Motors', 8, 5, 450.00, 'Industrial Supplies Co.', 'Warehouse A'),
                ('PMP-002', 'Pressure Sensor', 'Sensors', 12, 5, 85.50, 'Tech Components Inc.', 'Warehouse B'),
                ('PMP-003', 'Flow Meter', 'Meters', 15, 5, 120.00, 'Flow Tech Solutions', 'Warehouse A'),
                ('PMP-004', 'Motor Bearing', 'Bearings', 3, 5, 25.00, 'Bearing Specialists', 'Warehouse C'),
                ('PMP-005', 'Seal Kit', 'Seals', 7, 5, 35.00, 'Sealing Solutions', 'Warehouse B')
            """)

# Global database instance
db = DatabaseManager()