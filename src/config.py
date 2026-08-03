import os
from pathlib import Path

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Add your MySQL password here
    'database': 'water_pump_db',
    'port': 3306
}

# Arduino Configuration
ARDUINO_CONFIG = {
    'port': 'COM3',  # Change based on your system (COM3 for Windows, /dev/ttyUSB0 for Linux)
    'baud_rate': 9600,
    'timeout': 1
}

# Application Paths
APP_ROOT = Path(__file__).parent.parent
RESOURCES_PATH = APP_ROOT / 'resources'
LOGS_PATH = APP_ROOT / 'logs'
REPORTS_PATH = APP_ROOT / 'reports'

# Create directories if they don't exist
LOGS_PATH.mkdir(exist_ok=True)
REPORTS_PATH.mkdir(exist_ok=True)

# Theme Configuration
THEMES = {
    'light': {
        'primary': '#1976D2',
        'secondary': '#2196F3', 
        'background': '#FFFFFF',
        'surface': '#F5F5F5',
        'text': '#212121',
        'text_secondary': '#757575'
    },
    'dark': {
        'primary': '#90CAF9',
        'secondary': '#64B5F6',
        'background': '#121212',
        'surface': '#1E1E1E',
        'text': '#FFFFFF',
        'text_secondary': '#B0B0B0'
    }
}

# Email Configuration (for notifications)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': '',  # Add your email
    'sender_password': '',  # Add your app password
    'head_technician_email': ''  # Add head technician email
}

# Application Settings
APP_SETTINGS = {
    'company_name': 'Water Management Systems',
    'version': '1.0.0',
    'inventory_threshold': 5,  # Alert when inventory below this count
    'auto_refresh_interval': 5000,  # 5 seconds for pump status refresh
    'session_timeout': 1800  # 30 minutes in seconds
}