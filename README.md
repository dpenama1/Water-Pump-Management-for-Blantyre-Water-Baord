# Water Pump Management System

A comprehensive desktop application for monitoring and managing water pump systems, built with Python, PySide6, and MySQL.

## Features

### 🔧 Core Functionality
- **Real-time Pump Monitoring**: Monitor pump status, pressure, flow rate, temperature, and power consumption
- **Maintenance Scheduling**: Create and manage maintenance schedules with calendar integration
- **Inventory Management**: Track spare parts with automatic low-stock alerts
- **User Management**: Role-based access control with job ID authentication
- **Comprehensive Reporting**: Generate detailed reports on pump performance and system activity
- **System Logging**: Complete audit trail of all system activities

### 🎨 User Interface
- **Modern Design**: Clean, professional interface with light/dark themes
- **Responsive Layout**: Optimized for desktop use with intuitive navigation
- **Real-time Updates**: Live data refresh with configurable intervals
- **Interactive Dashboard**: Visual pump status with emergency controls

### 🔐 Security & Administration
- **Secure Login**: Job ID and password authentication
- **Role-based Access**: Different permissions for technicians, supervisors, and admins
- **Session Management**: Automatic timeout for security
- **Audit Trail**: Complete logging of all user actions

## System Requirements

### Software Requirements
- **Python**: 3.8 or higher
- **MySQL**: 5.7 or higher
- **Operating System**: Windows 10/11, macOS, or Linux

### Python Dependencies
```
PySide6>=6.5.0
mysql-connector-python>=8.0.33
pandas>=2.0.0
matplotlib>=3.7.0
requests>=2.31.0
cryptography>=41.0.0
python-dateutil>=2.8.2
openpyxl>=3.1.0
reportlab>=4.0.0
pyserial>=3.5
```

### Hardware Requirements
- **Arduino Uno**: For pump control and sensor reading (optional)
- **Sensors**: Pressure, flow, temperature sensors (optional)
- **Minimum RAM**: 4GB
- **Storage**: 500MB free space

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd water_pump_management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database
1. Install MySQL Server if not already installed
2. Create a database named `water_pump_db`
3. Update database configuration in `src/config.py`

### 4. Initialize Database
```bash
python init_db.py
```

### 5. Run the Application
```bash
python src/main.py
```

## Configuration

### Database Configuration
Edit `src/config.py` to match your MySQL setup:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Add your MySQL password
    'database': 'water_pump_db',
    'port': 3306
}
```

### Arduino Configuration (Optional)
If using Arduino for pump control:
```python
ARDUINO_CONFIG = {
    'port': 'COM3',  # Change based on your system
    'baud_rate': 9600,
    'timeout': 1
}
```

## Usage

### First Login
- **Default Admin Account**:
  - Job ID: `ADMIN001`
  - Password: `admin123`

### Navigation
1. **Dashboard**: View real-time pump status and maintenance calendar
2. **Pump Management**: Add, edit, and monitor water pumps
3. **Maintenance**: Schedule and track maintenance activities
4. **Inventory**: Manage spare parts and receive alerts
5. **Reports**: Generate and export system reports
6. **System Logs**: View and export system activity logs
7. **Settings**: Customize application appearance and behavior

### Key Features

#### Pump Management
- Add new pumps with detailed specifications
- Monitor real-time sensor readings
- Control pump operations (start/stop)
- View pump performance history

#### Maintenance Scheduling
- Create maintenance schedules with calendar integration
- Assign technicians to specific tasks
- Track maintenance completion status
- Receive overdue maintenance alerts

#### Inventory Management
- Add and track spare parts inventory
- Set minimum stock levels for alerts
- Automatic low-stock notifications
- Track inventory value and categories

#### Reporting System
- Generate various reports (pump performance, maintenance history, etc.)
- Export reports in multiple formats
- Schedule automated report generation
- Email reports to stakeholders

## Arduino Integration

### Hardware Setup
1. Connect Arduino Uno to computer via USB
2. Upload the provided Arduino sketch
3. Connect sensors to appropriate analog pins
4. Connect pump control relays to digital pins

### Supported Sensors
- Pressure sensors (analog input)
- Flow meters (analog input)
- Temperature sensors (analog input)
- Power monitoring (calculated/simulated)

### Arduino Sketch
The Arduino sketch is provided in `src/arduino_communication.py` as a comment. Upload this to your Arduino board.

## Database Schema

### Key Tables
- `users`: User accounts and authentication
- `water_pumps`: Pump information and status
- `maintenance_schedule`: Maintenance tasks and scheduling
- `inventory`: Spare parts inventory
- `system_logs`: System activity and audit logs
- `pump_readings`: Real-time sensor data
- `notifications`: System alerts and notifications

## Security Features

### Authentication
- Secure login with job ID and password
- Password hashing (implement in production)
- Session management with timeout

### Authorization
- Role-based access control
- Different permissions for different user types
- Audit logging of all actions

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- Secure session handling

## Troubleshooting

### Common Issues

#### Database Connection Failed
1. Check MySQL service is running
2. Verify database credentials in `config.py`
3. Ensure database `water_pump_db` exists

#### Arduino Connection Issues
1. Verify correct COM port in `config.py`
2. Check Arduino drivers are installed
3. Ensure Arduino sketch is uploaded

#### Application Won't Start
1. Check all dependencies are installed
2. Verify Python version compatibility
3. Check database initialization

### Log Files
- Application logs: `logs/application.log`
- Database logs: `logs/database.log`
- Error logs: Check console output

## Development

### Project Structure
```
water_pump_management/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── main_window.py     # Main application window
│   ├── login_dialog.py    # Login interface
│   ├── dashboard.py       # Dashboard widget
│   ├── pump_management.py # Pump management
│   ├── maintenance.py     # Maintenance scheduling
│   ├── inventory.py       # Inventory management
│   ├── reports.py         # Reports system
│   ├── logs.py           # System logs viewer
│   ├── settings.py       # Application settings
│   ├── database.py       # Database connection
│   ├── config.py         # Configuration settings
│   └── arduino_communication.py  # Arduino interface
├── resources/            # Icons, images, etc.
├── logs/                # Log files
├── docs/                # Documentation
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── init_db.py          # Database initialization
└── README.md           # This file
```

### Adding New Features
1. Create new widget class in `src/`
2. Add navigation button in `main_window.py`
3. Update database schema if needed
4. Add menu items and shortcuts

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_database.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support or questions:
- Create an issue in the repository
- Check the user guide in the Help menu
- Review log files for error details

## Changelog

### Version 1.0.0
- Initial release
- Complete pump management system
- Arduino integration
- Comprehensive reporting
- User management system
- Inventory management
- Maintenance scheduling