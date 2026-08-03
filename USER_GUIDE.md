
# Water Pump Management System - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Pump Management](#pump-management)
4. [Maintenance](#maintenance)
5. [Inventory](#inventory)
6. [Reports](#reports)
7. [System Logs](#system-logs)
8. [Settings](#settings)
9. [Arduino Integration](#arduino-integration)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### System Requirements
- Windows 10/11, macOS, or Linux
- MySQL Server 5.7 or higher
- Python 3.8 or higher
- Minimum 4GB RAM

### First Time Setup
1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python init_db.py
   ```

3. **Start Application**
   ```bash
   python src/main.py
   ```

### Login
- **Default Admin Account**:
  - Job ID: `ADMIN001`
  - Password: `admin123`

## Dashboard

The dashboard provides a comprehensive overview of your water pump system.

### Pump Status Monitor
- **Real-time Status**: View current status of all pumps (Online, Offline, Maintenance, Error)
- **Sensor Readings**: Monitor pressure, flow rate, temperature, and power consumption
- **Visual Indicators**: Color-coded status cards with performance metrics
- **Last Updated**: Timestamp showing when data was last refreshed

### Maintenance Calendar
- **Monthly View**: Visual calendar showing scheduled maintenance
- **Date Selection**: Click dates to filter maintenance tasks
- **Maintenance Highlights**: Dates with scheduled maintenance are highlighted

### System Notifications
- **Alert Types**: Info, Warning, Error, Maintenance, Inventory
- **Priority Levels**: Low, Medium, High, Urgent
- **Auto-dismiss**: Notifications are automatically marked as read

### Emergency Controls
- **Emergency Shutdown**: Immediately stop all pumps
- **Safety Confirmation**: Requires confirmation before executing
- **Automatic Logging**: All emergency actions are logged

## Pump Management

### Adding New Pumps
1. Click "➕ Add Pump" button
2. Fill in pump details:
   - **Pump Name**: Descriptive name (e.g., "Main Pump #1")
   - **Location**: Physical location of the pump
   - **Status**: Initial status (Online, Offline, Maintenance, Error)
   - **Operating Hours**: Current operating hours
   - **Sensor Values**: Initial pressure, flow rate, temperature readings
3. Set maintenance dates
4. Click "Save" to add the pump

### Managing Existing Pumps
- **Edit Pump**: Select a pump and click "✏️ Edit Pump"
- **Delete Pump**: Select a pump and click "🗑️ Delete Pump"
- **Search**: Use the search bar to find pumps by name or location
- **Filter**: Filter by status or other criteria

### Pump Details
Each pump card displays:
- **Status**: Color-coded status indicator
- **Location**: Physical location
- **Pressure**: Current pressure in PSI
- **Flow Rate**: Current flow rate in GPM
- **Temperature**: Current temperature in °F
- **Operating Hours**: Total operating hours
- **Last Maintenance**: Date of last maintenance
- **Next Maintenance**: Scheduled maintenance date

## Maintenance

### Scheduling Maintenance
1. Click "➕ Schedule Maintenance"
2. Fill in maintenance details:
   - **Pump**: Select the pump for maintenance
   - **Maintenance Type**: Routine Inspection, Preventive Maintenance, etc.
   - **Scheduled Date**: When maintenance should occur
   - **Assigned Technician**: Who will perform the maintenance
   - **Priority**: Low, Medium, High, Urgent
   - **Estimated Duration**: Expected time in minutes
   - **Description**: Detailed description of work to be done
3. Click "Save" to schedule the maintenance

### Maintenance Calendar
- **Weekly View**: Shows this week's maintenance schedule
- **Task Details**: Each task shows pump name, type, and assigned technician
- **Color Coding**: Tasks are color-coded by priority

### Managing Maintenance Tasks
- **Edit Task**: Modify existing maintenance schedules
- **Mark Complete**: Mark tasks as completed
- **Delete Task**: Remove scheduled maintenance
- **Status Updates**: Track task progress (Scheduled → In Progress → Completed)

## Inventory

### Adding Inventory Items
1. Click "➕ Add Item"
2. Fill in item details:
   - **Part Number**: Unique identifier
   - **Part Name**: Descriptive name
   - **Category**: Motors, Sensors, Bearings, etc.
   - **Quantity**: Current stock level
   - **Minimum Quantity**: Reorder level (alerts when below this)
   - **Unit Price**: Cost per item
   - **Supplier**: Vendor information
   - **Location**: Storage location
3. Click "Save" to add the item

### Inventory Alerts
- **Low Stock**: Items below minimum quantity are highlighted in orange
- **Out of Stock**: Items with zero quantity are highlighted in red
- **Automatic Notifications**: Alerts are sent to dashboard and email

### Managing Inventory
- **Edit Item**: Modify item details
- **Adjust Stock**: Update quantity levels
- **Delete Item**: Remove items from inventory
- **Search**: Find items by part number, name, or supplier
- **Filter**: Filter by category or stock status

### Inventory Summary
- **Total Items**: Total number of different parts
- **Low Stock Items**: Count of items below minimum quantity
- **Total Value**: Total inventory value
- **Categories**: Number of different categories

## Reports

### Report Types
1. **Pump Performance Summary**: Comprehensive pump analysis
2. **Maintenance History**: Complete maintenance records
3. **Inventory Status**: Current stock levels and alerts
4. **System Activity Logs**: User and system activity
5. **User Activity Report**: Login and usage patterns
6. **Maintenance Schedule**: Upcoming maintenance tasks
7. **Pump Status Overview**: Current status of all pumps
8. **Inventory Alerts**: Low stock notifications

### Generating Reports
1. Select report type
2. Choose date range
3. Apply filters (pumps, technicians, priority)
4. Add description
5. Click "Generate Report"

### Report Management
- **View Report**: Open report in viewer
- **Download**: Export as text file
- **Email**: Send report via email (requires configuration)
- **Delete**: Remove old reports

## System Logs

### Log Types
- **Login/Logout**: Authentication events
- **Pump Operations**: Pump control actions
- **Maintenance**: Maintenance activities
- **Inventory**: Stock changes
- **System**: Application errors and warnings

### Log Details
Each log entry contains:
- **Timestamp**: When the event occurred
- **User**: Who performed the action
- **Action**: What was done
- **Details**: Detailed description
- **Severity**: Info, Warning, Error, Critical
- **IP Address**: Source of the action

### Filtering Logs
- **Date Range**: Filter by specific time period
- **User**: Filter by specific user
- **Action Type**: Filter by action category
- **Severity**: Filter by log level
- **Search**: Search within log details

### Log Export
- **Export All**: Download all filtered logs
- **Export Selected**: Download specific log entries
- **Clear Old Logs**: Remove logs older than specified days

## Settings

### Profile Settings
- **Personal Information**: Name, email, department, job type
- **Password Change**: Update login password
- **Contact Information**: Notification preferences

### Appearance Settings
- **Theme Selection**: Light or dark theme
- **Font Settings**: Size and family customization
- **Preview**: See theme changes before applying

### System Settings
- **Auto-refresh**: Configure data refresh intervals
- **Session Timeout**: Set automatic logout time
- **Database**: Connection timeout settings
- **Auto-backup**: Enable automatic database backups

### Notification Settings
- **Email Notifications**: Configure email alerts
- **Dashboard Alerts**: In-app notifications
- **Sound Alerts**: Audio notifications for critical events
- **Frequency**: How often to send alerts

## Arduino Integration

### Hardware Requirements
- **Arduino Uno**: Main controller board
- **Pressure Sensors**: For pump pressure monitoring
- **Flow Sensors**: For flow rate measurement
- **Temperature Sensors**: For temperature monitoring
- **Relay Modules**: For pump control

### Connection Setup
1. **Upload Sketch**: Upload provided Arduino code
2. **Connect Sensors**: Wire sensors to analog pins
3. **Connect Relays**: Wire pump controls to digital pins
4. **Test Communication**: Verify data is being received

### Arduino Commands
- **PUMP1:ON/OFF**: Control pump 1
- **PUMP2:ON/OFF**: Control pump 2
- **SENSORS:1/2**: Request sensor data
- **PING**: Test communication

### Sensor Data Format
Arduino sends JSON data:
```json
{
  "pump_id": 1,
  "pressure": 45.2,
  "flow_rate": 125.5,
  "temperature": 72.3,
  "power": 5.5,
  "status": "online"
}
```

## Troubleshooting

### Common Issues

#### Application Won't Start
1. Check Python version (3.8+)
2. Verify all dependencies installed
3. Check database connection
4. Review application logs

#### Database Connection Failed
1. Verify MySQL is running
2. Check database credentials in config.py
3. Ensure database exists
4. Test connection manually

#### Arduino Not Connecting
1. Check COM port in config.py
2. Verify Arduino drivers installed
3. Ensure Arduino sketch uploaded
4. Check USB cable connection

#### No Data Displayed
1. Check database has data
2. Verify user permissions
3. Check filter settings
4. Refresh data manually

### Getting Help
1. Check application logs in `logs/` directory
2. Review console output for error messages
3. Check database logs
4. Verify configuration settings

### Log Files
- **Application Log**: `logs/application.log`
- **Database Log**: `logs/database.log`
- **Error Log**: Console output

## Best Practices

### Data Management
- Regular database backups
- Monitor disk space
- Archive old log data
- Validate user inputs

### Security
- Change default passwords
- Regular security updates
- Monitor user activity
- Secure network connections

### Maintenance
- Regular system updates
- Monitor system performance
- Clean up old reports
- Review security logs

## Support

For technical support:
1. Check the troubleshooting section
2. Review log files for error details
3. Create an issue in the repository
4. Contact system administrator

## Version History

### Version 1.0.0
- Initial release
- Complete pump monitoring system
- Arduino integration
- Comprehensive reporting
- User management system
- Inventory management
- Maintenance scheduling