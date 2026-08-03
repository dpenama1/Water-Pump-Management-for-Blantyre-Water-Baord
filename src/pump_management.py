import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
                              QTextEdit, QMessageBox, QDialog, QDialogButtonBox,
                              QFormLayout, QGroupBox, QHeaderView, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QColor
from datetime import datetime, date
from database import db

class PumpDialog(QDialog):
    def __init__(self, pump_data=None, parent=None):
        super().__init__(parent)
        self.pump_data = pump_data
        self.setWindowTitle("Add/Edit Water Pump")
        self.setFixedSize(500, 600)
        
        self.setup_ui()
        
        if pump_data:
            self.load_pump_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Pump Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter pump name (e.g., Main Pump #1)")
        form_layout.addRow("Pump Name:*", self.name_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter pump location")
        form_layout.addRow("Location:*", self.location_input)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['online', 'offline', 'maintenance', 'error'])
        form_layout.addRow("Status:", self.status_combo)
        
        # Operating Hours
        self.hours_spin = QDoubleSpinBox()
        self.hours_spin.setRange(0, 100000)
        self.hours_spin.setDecimals(1)
        self.hours_spin.setSuffix(" hrs")
        form_layout.addRow("Operating Hours:", self.hours_spin)
        
        # Pressure Level
        self.pressure_spin = QDoubleSpinBox()
        self.pressure_spin.setRange(0, 1000)
        self.pressure_spin.setDecimals(1)
        self.pressure_spin.setSuffix(" PSI")
        form_layout.addRow("Pressure Level:", self.pressure_spin)
        
        # Flow Rate
        self.flow_spin = QDoubleSpinBox()
        self.flow_spin.setRange(0, 10000)
        self.flow_spin.setDecimals(1)
        self.flow_spin.setSuffix(" GPM")
        form_layout.addRow("Flow Rate:", self.flow_spin)
        
        # Temperature
        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(-50, 200)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setSuffix(" °F")
        form_layout.addRow("Temperature:", self.temp_spin)
        
        # Power Consumption
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(0, 10000)
        self.power_spin.setDecimals(1)
        self.power_spin.setSuffix(" kW")
        form_layout.addRow("Power Consumption:", self.power_spin)
        
        # Last Maintenance
        self.last_maintenance_edit = QDateEdit()
        self.last_maintenance_edit.setCalendarPopup(True)
        self.last_maintenance_edit.setDate(date.today())
        form_layout.addRow("Last Maintenance:", self.last_maintenance_edit)
        
        # Next Maintenance
        self.next_maintenance_edit = QDateEdit()
        self.next_maintenance_edit.setCalendarPopup(True)
        next_month = date.today() + timedelta(days=30)
        self.next_maintenance_edit.setDate(next_month)
        form_layout.addRow("Next Maintenance:", self.next_maintenance_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_pump_data(self):
        """Load existing pump data into form"""
        self.name_input.setText(self.pump_data.get('pump_name', ''))
        self.location_input.setText(self.pump_data.get('location', ''))
        self.status_combo.setCurrentText(self.pump_data.get('status', 'offline'))
        self.hours_spin.setValue(self.pump_data.get('operating_hours', 0))
        self.pressure_spin.setValue(self.pump_data.get('pressure_level', 0))
        self.flow_spin.setValue(self.pump_data.get('flow_rate', 0))
        self.temp_spin.setValue(self.pump_data.get('temperature', 0))
        self.power_spin.setValue(self.pump_data.get('power_consumption', 0))
        
        if self.pump_data.get('last_maintenance'):
            self.last_maintenance_edit.setDate(self.pump_data['last_maintenance'])
        if self.pump_data.get('next_maintenance'):
            self.next_maintenance_edit.setDate(self.pump_data['next_maintenance'])
    
    def get_pump_data(self):
        """Get form data as dictionary"""
        return {
            'pump_name': self.name_input.text().strip(),
            'location': self.location_input.text().strip(),
            'status': self.status_combo.currentText(),
            'operating_hours': self.hours_spin.value(),
            'pressure_level': self.pressure_spin.value(),
            'flow_rate': self.flow_spin.value(),
            'temperature': self.temp_spin.value(),
            'power_consumption': self.power_spin.value(),
            'last_maintenance': self.last_maintenance_edit.date().toPython(),
            'next_maintenance': self.next_maintenance_edit.date().toPython()
        }

class PumpManagementWidget(QWidget):
    pump_updated = Signal()
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.pumps = []
        
        self.setup_ui()
        self.load_pumps()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Water Pump Management")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add Pump Button
        self.add_btn = QPushButton("➕ Add Pump")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_btn.clicked.connect(self.add_pump)
        header_layout.addWidget(self.add_btn)
        
        # Refresh Button
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_pumps)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search pumps by name or location...")
        self.search_input.textChanged.connect(self.filter_pumps)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Pump Table
        self.pump_table = QTableWidget()
        self.pump_table.setColumnCount(10)
        self.pump_table.setHorizontalHeaderLabels([
            "ID", "Pump Name", "Location", "Status", "Operating Hours", 
            "Pressure (PSI)", "Flow Rate (GPM)", "Temperature (°F)", 
            "Last Maintenance", "Next Maintenance"
        ])
        
        # Table styling
        self.pump_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #E0E0E0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        
        # Configure table
        header = self.pump_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.pump_table.setAlternatingRowColors(True)
        self.pump_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.pump_table)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit Pump")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.edit_btn.clicked.connect(self.edit_pump)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete Pump")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_pump)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        
        # Connect table selection
        self.pump_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_pumps(self):
        """Load pumps from database"""
        try:
            if db.connect():
                query = "SELECT * FROM water_pumps ORDER BY id"
                self.pumps = db.execute_query(query)
                db.close()
                
                self.populate_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load pumps: {str(e)}")
    
    def populate_table(self):
        """Populate table with pump data"""
        self.pump_table.setRowCount(len(self.pumps))
        
        for row, pump in enumerate(self.pumps):
            # ID
            self.pump_table.setItem(row, 0, QTableWidgetItem(str(pump['id'])))
            
            # Pump Name
            self.pump_table.setItem(row, 1, QTableWidgetItem(pump['pump_name']))
            
            # Location
            self.pump_table.setItem(row, 2, QTableWidgetItem(pump['location']))
            
            # Status with color coding
            status_item = QTableWidgetItem(pump['status'].upper())
            status_colors = {
                'online': '#4CAF50',
                'offline': '#F44336',
                'maintenance': '#FF9800',
                'error': '#9C27B0'
            }
            color = status_colors.get(pump['status'], '#757575')
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor('white'))
            self.pump_table.setItem(row, 3, status_item)

            # Operating Hours (SAFE FIX)
            op_hours = pump.get('operating_hours')
            hours = f"{float(op_hours if op_hours is not None else 0.0):.1f} hrs"
            self.pump_table.setItem(row, 4, QTableWidgetItem(hours))

            # Pressure (SAFE FIX)
            p_val = pump.get('pressure_level')
            pressure = f"{float(p_val if p_val is not None else 0.0):.1f}"
            self.pump_table.setItem(row, 5, QTableWidgetItem(pressure))

            # Flow Rate (SAFE FIX)
            f_val = pump.get('flow_rate')
            flow = f"{float(f_val if f_val is not None else 0.0):.1f}"
            self.pump_table.setItem(row, 6, QTableWidgetItem(flow))

            # Temperature (SAFE FIX)
            t_val = pump.get('temperature')
            temp = f"{float(t_val if t_val is not None else 0.0):.1f}"
            self.pump_table.setItem(row, 7, QTableWidgetItem(temp))
            
            # Last Maintenance
            last_maint = pump.get('last_maintenance')
            if last_maint:
                last_maint_str = last_maint.strftime('%Y-%m-%d')
            else:
                last_maint_str = 'N/A'
            self.pump_table.setItem(row, 8, QTableWidgetItem(last_maint_str))
            
            # Next Maintenance
            next_maint = pump.get('next_maintenance')
            if next_maint:
                next_maint_str = next_maint.strftime('%Y-%m-%d')
            else:
                next_maint_str = 'N/A'
            self.pump_table.setItem(row, 9, QTableWidgetItem(next_maint_str))
        
        self.pump_table.resizeColumnsToContents()
    
    def filter_pumps(self, text):
        """Filter pumps based on search text"""
        for row in range(self.pump_table.rowCount()):
            name_item = self.pump_table.item(row, 1)
            location_item = self.pump_table.item(row, 2)
            
            name_match = text.lower() in name_item.text().lower()
            location_match = text.lower() in location_item.text().lower()
            
            self.pump_table.setRowHidden(row, not (name_match or location_match))
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.pump_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_pump(self):
        """Add new pump"""
        dialog = PumpDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            pump_data = dialog.get_pump_data()
            
            try:
                if db.connect():
                    query = """
                        INSERT INTO water_pumps (pump_name, location, status, operating_hours,
                                               pressure_level, flow_rate, temperature, power_consumption,
                                               last_maintenance, next_maintenance)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        pump_data['pump_name'],
                        pump_data['location'],
                        pump_data['status'],
                        pump_data['operating_hours'],
                        pump_data['pressure_level'],
                        pump_data['flow_rate'],
                        pump_data['temperature'],
                        pump_data['power_consumption'],
                        pump_data['last_maintenance'],
                        pump_data['next_maintenance']
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'add_pump',
                                         f"Added new pump: {pump_data['pump_name']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Pump added successfully!")
                        self.load_pumps()
                        self.pump_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add pump.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add pump: {str(e)}")
    
    def edit_pump(self):
        """Edit selected pump"""
        current_row = self.pump_table.currentRow()
        if current_row < 0:
            return
        
        pump_id = int(self.pump_table.item(current_row, 0).text())
        pump_data = next((p for p in self.pumps if p['id'] == pump_id), None)
        
        if not pump_data:
            return
        
        dialog = PumpDialog(pump_data, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_pump_data()
            
            try:
                if db.connect():
                    query = """
                        UPDATE water_pumps 
                        SET pump_name = %s, location = %s, status = %s, 
                            operating_hours = %s, pressure_level = %s, flow_rate = %s,
                            temperature = %s, power_consumption = %s,
                            last_maintenance = %s, next_maintenance = %s
                        WHERE id = %s
                    """
                    params = (
                        updated_data['pump_name'],
                        updated_data['location'],
                        updated_data['status'],
                        updated_data['operating_hours'],
                        updated_data['pressure_level'],
                        updated_data['flow_rate'],
                        updated_data['temperature'],
                        updated_data['power_consumption'],
                        updated_data['last_maintenance'],
                        updated_data['next_maintenance'],
                        pump_id
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'edit_pump',
                                         f"Updated pump: {updated_data['pump_name']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Pump updated successfully!")
                        self.load_pumps()
                        self.pump_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update pump.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update pump: {str(e)}")
    
    def delete_pump(self):
        """Delete selected pump"""
        current_row = self.pump_table.currentRow()
        if current_row < 0:
            return
        
        pump_id = int(self.pump_table.item(current_row, 0).text())
        pump_name = self.pump_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete pump '{pump_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    query = "DELETE FROM water_pumps WHERE id = %s"
                    
                    if db.execute_update(query, (pump_id,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'delete_pump',
                                         f"Deleted pump: {pump_name}", 'warning'))
                        
                        QMessageBox.information(self, "Success", "Pump deleted successfully!")
                        self.load_pumps()
                        self.pump_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to delete pump.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete pump: {str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Initialize database
    db.init_database()
    
    # Demo user data
    demo_user = {
        'id': 1,
        'name': 'Demo User'
    }
    
    pump_mgmt = PumpManagementWidget(demo_user)
    pump_mgmt.show()
    
    sys.exit(app.exec())