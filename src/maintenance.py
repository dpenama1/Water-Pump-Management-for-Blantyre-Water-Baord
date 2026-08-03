import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QDateEdit, QSpinBox, QTextEdit, QMessageBox,
                              QDialog, QDialogButtonBox, QFormLayout, QGroupBox,
                              QHeaderView, QFrame, QListWidget, QListWidgetItem,
                              QSplitter, QCalendarWidget)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont, QIcon, QColor
from datetime import datetime, date, timedelta
from database import db

class MaintenanceDialog(QDialog):
    def __init__(self, maintenance_data=None, pumps=[], technicians=[], parent=None):
        super().__init__(parent)
        self.maintenance_data = maintenance_data
        self.pumps = pumps
        self.technicians = technicians
        
        self.setWindowTitle("Add/Edit Maintenance Schedule")
        self.setFixedSize(600, 700)
        
        self.setup_ui()
        
        if maintenance_data:
            self.load_maintenance_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Pump Selection
        self.pump_combo = QComboBox()
        for pump in self.pumps:
            self.pump_combo.addItem(pump['pump_name'], pump['id'])
        form_layout.addRow("Pump:*", self.pump_combo)
        
        # Maintenance Type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            'Routine Inspection',
            'Preventive Maintenance',
            'Corrective Maintenance',
            'Emergency Repair',
            'Overhaul',
            'Calibration'
        ])
        form_layout.addRow("Maintenance Type:*", self.type_combo)
        
        # Scheduled Date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        form_layout.addRow("Scheduled Date:*", self.date_edit)
        
        # Assigned Technician
        self.technician_combo = QComboBox()
        for tech in self.technicians:
            self.technician_combo.addItem(f"{tech['name']} ({tech['job_id']})", tech['id'])
        form_layout.addRow("Assigned Technician:*", self.technician_combo)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(['low', 'medium', 'high', 'urgent'])
        self.priority_combo.setCurrentText('medium')
        form_layout.addRow("Priority:*", self.priority_combo)
        
        # Estimated Duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 480)  # 1 to 480 minutes (8 hours)
        self.duration_spin.setSuffix(" minutes")
        form_layout.addRow("Estimated Duration:", self.duration_spin)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter maintenance description and details...")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:*", self.description_edit)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['scheduled', 'in_progress', 'completed', 'overdue'])
        form_layout.addRow("Status:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_maintenance_data(self):
        """Load existing maintenance data into form"""
        # Set pump
        pump_id = self.maintenance_data.get('pump_id')
        for i in range(self.pump_combo.count()):
            if self.pump_combo.itemData(i) == pump_id:
                self.pump_combo.setCurrentIndex(i)
                break
        
        # Set other fields
        self.type_combo.setCurrentText(self.maintenance_data.get('maintenance_type', ''))
        
        if self.maintenance_data.get('scheduled_date'):
            self.date_edit.setDate(self.maintenance_data['scheduled_date'])
        
        # Set technician
        tech_id = self.maintenance_data.get('assigned_technician_id')
        for i in range(self.technician_combo.count()):
            if self.technician_combo.itemData(i) == tech_id:
                self.technician_combo.setCurrentIndex(i)
                break
        
        self.priority_combo.setCurrentText(self.maintenance_data.get('priority', 'medium'))
        self.duration_spin.setValue(self.maintenance_data.get('estimated_duration', 60))
        self.description_edit.setPlainText(self.maintenance_data.get('description', ''))
        self.status_combo.setCurrentText(self.maintenance_data.get('status', 'scheduled'))
    
    def get_maintenance_data(self):
        """Get form data as dictionary"""
        return {
            'pump_id': self.pump_combo.currentData(),
            'maintenance_type': self.type_combo.currentText(),
            'scheduled_date': self.date_edit.date().toPython(),
            'assigned_technician_id': self.technician_combo.currentData(),
            'priority': self.priority_combo.currentText(),
            'estimated_duration': self.duration_spin.value(),
            'description': self.description_edit.toPlainText().strip(),
            'status': self.status_combo.currentText()
        }

class MaintenanceWidget(QWidget):
    maintenance_updated = Signal()
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.maintenance_tasks = []
        self.pumps = []
        self.technicians = []
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # Left Panel - Calendar and Weekly Schedule
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Calendar
        calendar_group = QGroupBox("Maintenance Calendar")
        calendar_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        calendar_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton {
                background-color: #1976D2;
                color: white;
            }
        """)
        self.calendar.clicked.connect(self.on_calendar_date_selected)
        calendar_layout.addWidget(self.calendar)
        calendar_group.setLayout(calendar_layout)
        
        left_panel.addWidget(calendar_group)
        
        # Weekly Schedule
        weekly_group = QGroupBox("This Week's Schedule")
        weekly_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        weekly_layout = QVBoxLayout()
        self.weekly_list = QListWidget()
        self.weekly_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FAFAFA;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E0E0E0;
            }
            QListWidget::item:hover {
                background-color: #E3F2FD;
            }
        """)
        weekly_layout.addWidget(self.weekly_list)
        weekly_group.setLayout(weekly_layout)
        
        left_panel.addWidget(weekly_group)
        
        # Right Panel - Maintenance Table and Controls
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Maintenance Management")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Add Maintenance Button
        self.add_btn = QPushButton("➕ Schedule Maintenance")
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
        self.add_btn.clicked.connect(self.add_maintenance)
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
        self.refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(self.refresh_btn)
        
        right_panel.addLayout(header_layout)
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search maintenance tasks...")
        self.search_input.textChanged.connect(self.filter_maintenance)
        search_layout.addWidget(self.search_input)
        
        # Status Filter
        self.status_filter = QComboBox()
        self.status_filter.addItem("All Status", "all")
        self.status_filter.addItem("Scheduled", "scheduled")
        self.status_filter.addItem("In Progress", "in_progress")
        self.status_filter.addItem("Completed", "completed")
        self.status_filter.addItem("Overdue", "overdue")
        self.status_filter.currentTextChanged.connect(self.filter_maintenance)
        search_layout.addWidget(self.status_filter)
        
        right_panel.addLayout(search_layout)
        
        # Maintenance Table
        self.maintenance_table = QTableWidget()
        self.maintenance_table.setColumnCount(11)
        self.maintenance_table.setHorizontalHeaderLabels([
            "ID", "Pump", "Type", "Scheduled Date", "Technician", 
            "Priority", "Status", "Duration", "Description", "Created", "Actions"
        ])
        
        # Table styling
        self.maintenance_table.setStyleSheet("""
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
        header = self.maintenance_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.maintenance_table.setAlternatingRowColors(True)
        self.maintenance_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        right_panel.addWidget(self.maintenance_table)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("✏️ Edit Task")
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
        self.edit_btn.clicked.connect(self.edit_maintenance)
        self.edit_btn.setEnabled(False)
        
        self.complete_btn = QPushButton("✅ Mark Complete")
        self.complete_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.complete_btn.clicked.connect(self.mark_complete)
        self.complete_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete Task")
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
        self.delete_btn.clicked.connect(self.delete_maintenance)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.complete_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        right_panel.addLayout(action_layout)
        
        # Create main widget containers
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMaximumWidth(400)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        # Add to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget, 1)
        
        self.setLayout(main_layout)
        
        # Connect table selection
        self.maintenance_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_data(self):
        """Load all maintenance data"""
        try:
            if db.connect():
                # Load maintenance tasks
                query = """
                    SELECT m.*, w.pump_name, u.name as technician_name
                    FROM maintenance_schedule m
                    LEFT JOIN water_pumps w ON m.pump_id = w.id
                    LEFT JOIN users u ON m.assigned_technician_id = u.id
                    ORDER BY m.scheduled_date, m.priority
                """
                self.maintenance_tasks = db.execute_query(query)
                
                # Load pumps
                query = "SELECT id, pump_name FROM water_pumps ORDER BY pump_name"
                self.pumps = db.execute_query(query)
                
                # Load technicians
                query = "SELECT id, name, job_id FROM users WHERE role IN ('technician', 'supervisor') ORDER BY name"
                self.technicians = db.execute_query(query)
                
                db.close()
                
                self.populate_table()
                self.update_weekly_schedule()
                self.update_calendar_highlights()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load maintenance data: {str(e)}")
    
    def populate_table(self):
        """Populate maintenance table with data"""
        self.maintenance_table.setRowCount(len(self.maintenance_tasks))
        
        for row, task in enumerate(self.maintenance_tasks):
            # ID
            self.maintenance_table.setItem(row, 0, QTableWidgetItem(str(task['id'])))
            
            # Pump Name
            self.maintenance_table.setItem(row, 1, QTableWidgetItem(task.get('pump_name', 'Unknown')))
            
            # Maintenance Type
            self.maintenance_table.setItem(row, 2, QTableWidgetItem(task['maintenance_type']))
            
            # Scheduled Date
            date_str = task['scheduled_date'].strftime('%Y-%m-%d')
            self.maintenance_table.setItem(row, 3, QTableWidgetItem(date_str))
            
            # Technician
            tech_name = task.get('technician_name', 'Unassigned')
            self.maintenance_table.setItem(row, 4, QTableWidgetItem(tech_name))
            
            # Priority with color coding
            priority = task['priority']
            priority_item = QTableWidgetItem(priority.upper())
            priority_colors = {
                'low': '#4CAF50',
                'medium': '#FF9800',
                'high': '#F44336',
                'urgent': '#9C27B0'
            }
            color = priority_colors.get(priority, '#757575')
            priority_item.setBackground(QColor(color))
            priority_item.setForeground(QColor('white'))
            self.maintenance_table.setItem(row, 5, priority_item)
            
            # Status with color coding
            status = task['status']
            status_item = QTableWidgetItem(status.upper().replace('_', ' '))
            status_colors = {
                'scheduled': '#2196F3',
                'in_progress': '#FF9800',
                'completed': '#4CAF50',
                'overdue': '#F44336'
            }
            color = status_colors.get(status, '#757575')
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor('white'))
            self.maintenance_table.setItem(row, 6, status_item)
            
            # Duration
            duration = f"{task.get('estimated_duration', 0)} min"
            self.maintenance_table.setItem(row, 7, QTableWidgetItem(duration))
            
            # Description
            description = task.get('description', '')[:50] + '...' if len(task.get('description', '')) > 50 else task.get('description', '')
            self.maintenance_table.setItem(row, 8, QTableWidgetItem(description))
            
            # Created
            created_str = task['created_at'].strftime('%Y-%m-%d %H:%M')
            self.maintenance_table.setItem(row, 9, QTableWidgetItem(created_str))
        
        self.maintenance_table.resizeColumnsToContents()
    
    def update_weekly_schedule(self):
        """Update weekly schedule display"""
        self.weekly_list.clear()
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_tasks = [task for task in self.maintenance_tasks 
                       if week_start <= task['scheduled_date'] <= week_end]
        
        if not weekly_tasks:
            item = QListWidgetItem("No maintenance scheduled this week")
            item.setForeground(QColor('#757575'))
            self.weekly_list.addItem(item)
        else:
            for task in weekly_tasks:
                date_str = task['scheduled_date'].strftime('%a %m/%d')
                pump_name = task.get('pump_name', 'Unknown')
                tech_name = task.get('technician_name', 'Unassigned')
                
                item_text = f"{date_str} - {pump_name}\n    {task['maintenance_type']} - {tech_name}"
                item = QListWidgetItem(item_text)
                
                # Color based on priority
                priority_colors = {
                    'low': '#4CAF50',
                    'medium': '#FF9800',
                    'high': '#F44336',
                    'urgent': '#9C27B0'
                }
                color = priority_colors.get(task['priority'], '#757575')
                item.setForeground(QColor(color))
                
                self.weekly_list.addItem(item)
    
    def update_calendar_highlights(self):
        """Highlight maintenance dates on calendar"""
        # This would be implemented with custom calendar painting
        # For now, we'll just note the dates
        maintenance_dates = [task['scheduled_date'] for task in self.maintenance_tasks]
        # Calendar highlighting logic would go here
    
    def filter_maintenance(self):
        """Filter maintenance tasks based on search and status"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentData() if self.status_filter.currentData() != "all" else None
        
        for row in range(self.maintenance_table.rowCount()):
            # Search filter
            pump_name = self.maintenance_table.item(row, 1).text().lower()
            maintenance_type = self.maintenance_table.item(row, 2).text().lower()
            description = self.maintenance_table.item(row, 8).text().lower()
            
            search_match = (search_text in pump_name or 
                          search_text in maintenance_type or 
                          search_text in description)
            
            # Status filter
            status_match = True
            if status_filter:
                status_item = self.maintenance_table.item(row, 6)
                status_match = status_filter == status_item.text().lower().replace(' ', '_')
            
            self.maintenance_table.setRowHidden(row, not (search_match and status_match))
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.maintenance_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.complete_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def on_calendar_date_selected(self, date):
        """Handle calendar date selection"""
        # Filter table to show tasks for selected date
        date_str = date.toString('yyyy-MM-dd')
        
        for row in range(self.maintenance_table.rowCount()):
            task_date = self.maintenance_table.item(row, 3).text()
            self.maintenance_table.setRowHidden(row, task_date != date_str)
    
    def add_maintenance(self):
        """Add new maintenance task"""
        if not self.pumps or not self.technicians:
            QMessageBox.warning(self, "Warning", "Please ensure there are pumps and technicians available.")
            return
        
        dialog = MaintenanceDialog(pumps=self.pumps, technicians=self.technicians, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            maintenance_data = dialog.get_maintenance_data()
            
            try:
                if db.connect():
                    query = """
                        INSERT INTO maintenance_schedule (pump_id, maintenance_type, scheduled_date,
                                                        assigned_technician_id, priority, estimated_duration,
                                                        description, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (
                        maintenance_data['pump_id'],
                        maintenance_data['maintenance_type'],
                        maintenance_data['scheduled_date'],
                        maintenance_data['assigned_technician_id'],
                        maintenance_data['priority'],
                        maintenance_data['estimated_duration'],
                        maintenance_data['description'],
                        maintenance_data['status']
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'add_maintenance',
                                         f"Added maintenance: {maintenance_data['maintenance_type']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Maintenance task scheduled successfully!")
                        self.load_data()
                        self.maintenance_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to schedule maintenance.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to schedule maintenance: {str(e)}")
    
    def edit_maintenance(self):
        """Edit selected maintenance task"""
        current_row = self.maintenance_table.currentRow()
        if current_row < 0:
            return
        
        task_id = int(self.maintenance_table.item(current_row, 0).text())
        task_data = next((t for t in self.maintenance_tasks if t['id'] == task_id), None)
        
        if not task_data:
            return
        
        dialog = MaintenanceDialog(task_data, self.pumps, self.technicians, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_maintenance_data()
            
            try:
                if db.connect():
                    query = """
                        UPDATE maintenance_schedule 
                        SET pump_id = %s, maintenance_type = %s, scheduled_date = %s,
                            assigned_technician_id = %s, priority = %s, estimated_duration = %s,
                            description = %s, status = %s
                        WHERE id = %s
                    """
                    params = (
                        updated_data['pump_id'],
                        updated_data['maintenance_type'],
                        updated_data['scheduled_date'],
                        updated_data['assigned_technician_id'],
                        updated_data['priority'],
                        updated_data['estimated_duration'],
                        updated_data['description'],
                        updated_data['status'],
                        task_id
                    )
                    
                    if db.execute_update(query, params):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'edit_maintenance',
                                         f"Updated maintenance: {updated_data['maintenance_type']}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Maintenance task updated successfully!")
                        self.load_data()
                        self.maintenance_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update maintenance task.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update maintenance task: {str(e)}")
    
    def mark_complete(self):
        """Mark maintenance task as completed"""
        current_row = self.maintenance_table.currentRow()
        if current_row < 0:
            return
        
        task_id = int(self.maintenance_table.item(current_row, 0).text())
        task_name = self.maintenance_table.item(current_row, 2).text()
        
        reply = QMessageBox.question(self, "Confirm Completion",
                                   f"Mark '{task_name}' as completed?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    query = "UPDATE maintenance_schedule SET status = 'completed' WHERE id = %s"
                    
                    if db.execute_update(query, (task_id,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'complete_maintenance',
                                         f"Completed maintenance: {task_name}", 'info'))
                        
                        QMessageBox.information(self, "Success", "Maintenance task marked as completed!")
                        self.load_data()
                        self.maintenance_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update maintenance task.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update maintenance task: {str(e)}")
    
    def delete_maintenance(self):
        """Delete selected maintenance task"""
        current_row = self.maintenance_table.currentRow()
        if current_row < 0:
            return
        
        task_id = int(self.maintenance_table.item(current_row, 0).text())
        task_name = self.maintenance_table.item(current_row, 2).text()
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete '{task_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    query = "DELETE FROM maintenance_schedule WHERE id = %s"
                    
                    if db.execute_update(query, (task_id,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'delete_maintenance',
                                         f"Deleted maintenance: {task_name}", 'warning'))
                        
                        QMessageBox.information(self, "Success", "Maintenance task deleted successfully!")
                        self.load_data()
                        self.maintenance_updated.emit()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to delete maintenance task.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete maintenance task: {str(e)}")

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
    
    maintenance = MaintenanceWidget(demo_user)
    maintenance.show()
    
    sys.exit(app.exec())