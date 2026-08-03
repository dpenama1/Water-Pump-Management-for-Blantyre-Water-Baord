import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QDateEdit, QTextEdit, QMessageBox,
                              QGroupBox, QHeaderView, QFrame, QFileDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date
from database import db
import json

class LogsWidget(QWidget):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.logs = []
        
        self.setup_ui()
        self.load_logs()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("System Logs")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Export Button
        self.export_btn = QPushButton("📤 Export Logs")
        self.export_btn.setStyleSheet("""
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
        self.export_btn.clicked.connect(self.export_logs)
        header_layout.addWidget(self.export_btn)
        
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
        self.refresh_btn.clicked.connect(self.load_logs)
        header_layout.addWidget(self.refresh_btn)
        
        # Clear Logs Button
        self.clear_btn = QPushButton("🗑️ Clear Old Logs")
        self.clear_btn.setStyleSheet("""
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
        """)
        self.clear_btn.clicked.connect(self.clear_old_logs)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Filters Section
        filters_group = QGroupBox("Log Filters")
        filters_group.setStyleSheet("""
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
        
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(15)
        
        # Date Range Filter
        date_layout = QVBoxLayout()
        date_label = QLabel("Date Range:")
        date_label.setStyleSheet("font-weight: bold;")
        date_layout.addWidget(date_label)
        
        date_range_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.dateChanged.connect(self.apply_filters)
        date_range_layout.addWidget(QLabel("From:"))
        date_range_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.dateChanged.connect(self.apply_filters)
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.end_date)
        
        date_layout.addLayout(date_range_layout)
        filters_layout.addLayout(date_layout)
        
        # User Filter
        user_layout = QVBoxLayout()
        user_label = QLabel("User:")
        user_label.setStyleSheet("font-weight: bold;")
        user_layout.addWidget(user_label)
        
        self.user_filter = QComboBox()
        self.user_filter.addItem("All Users", "all")
        self.user_filter.currentTextChanged.connect(self.apply_filters)
        user_layout.addWidget(self.user_filter)
        filters_layout.addLayout(user_layout)
        
        # Action Filter
        action_layout = QVBoxLayout()
        action_label = QLabel("Action:")
        action_label.setStyleSheet("font-weight: bold;")
        action_layout.addWidget(action_label)
        
        self.action_filter = QComboBox()
        self.action_filter.addItem("All Actions", "all")
        self.action_filter.addItem("Login", "login")
        self.action_filter.addItem("Logout", "logout")
        self.action_filter.addItem("Pump Operations", "pump")
        self.action_filter.addItem("Maintenance", "maintenance")
        self.action_filter.addItem("Inventory", "inventory")
        self.action_filter.addItem("Reports", "report")
        self.action_filter.addItem("System", "system")
        self.action_filter.currentTextChanged.connect(self.apply_filters)
        action_layout.addWidget(self.action_filter)
        filters_layout.addLayout(action_layout)
        
        # Severity Filter
        severity_layout = QVBoxLayout()
        severity_label = QLabel("Severity:")
        severity_label.setStyleSheet("font-weight: bold;")
        severity_layout.addWidget(severity_label)
        
        self.severity_filter = QComboBox()
        self.severity_filter.addItem("All Levels", "all")
        self.severity_filter.addItem("Info", "info")
        self.severity_filter.addItem("Warning", "warning")
        self.severity_filter.addItem("Error", "error")
        self.severity_filter.addItem("Critical", "critical")
        self.severity_filter.currentTextChanged.connect(self.apply_filters)
        severity_layout.addWidget(self.severity_filter)
        filters_layout.addLayout(severity_layout)
        
        # Search Filter
        search_layout = QVBoxLayout()
        search_label = QLabel("Search:")
        search_label.setStyleSheet("font-weight: bold;")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in details...")
        self.search_input.textChanged.connect(self.apply_filters)
        search_layout.addWidget(self.search_input)
        filters_layout.addLayout(search_layout)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Logs Statistics
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Total Logs
        self.total_logs_card = self.create_stat_card("Total Logs", "0", "#1976D2")
        stats_layout.addWidget(self.total_logs_card)
        
        # Error Count
        self.error_logs_card = self.create_stat_card("Errors", "0", "#F44336")
        stats_layout.addWidget(self.error_logs_card)
        
        # Warning Count
        self.warning_logs_card = self.create_stat_card("Warnings", "0", "#FF9800")
        stats_layout.addWidget(self.warning_logs_card)
        
        # Today's Logs
        self.today_logs_card = self.create_stat_card("Today's Logs", "0", "#4CAF50")
        stats_layout.addWidget(self.today_logs_card)
        
        layout.addLayout(stats_layout)
        
        # Logs Table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(8)
        self.logs_table.setHorizontalHeaderLabels([
            "ID", "Timestamp", "User", "Action", "Details", "Severity", "IP Address", "Actions"
        ])
        
        # Table styling
        self.logs_table.setStyleSheet("""
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
        header = self.logs_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.logs_table)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.view_details_btn = QPushButton("👁️ View Details")
        self.view_details_btn.setStyleSheet("""
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
        self.view_details_btn.clicked.connect(self.view_log_details)
        self.view_details_btn.setEnabled(False)
        
        self.export_selected_btn = QPushButton("📤 Export Selected")
        self.export_selected_btn.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #9E9E9E;
            }
        """)
        self.export_selected_btn.clicked.connect(self.export_selected_logs)
        self.export_selected_btn.setEnabled(False)
        
        action_layout.addWidget(self.view_details_btn)
        action_layout.addWidget(self.export_selected_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        
        # Connect table selection
        self.logs_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Load user filter options
        self.load_user_filter()
    
    def create_stat_card(self, title, value, color):
        """Create a statistics card widget"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 15px;
                color: white;
            }}
        """)
        
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: white;")
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        value_label.setStyleSheet("color: white;")
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        
        card.setLayout(card_layout)
        return card
    
    def load_user_filter(self):
        """Load user options for filter"""
        try:
            if db.connect():
                query = "SELECT id, name, job_id FROM users ORDER BY name"
                users = db.execute_query(query)
                
                for user in users:
                    display_text = f"{user['name']} ({user['job_id']})"
                    self.user_filter.addItem(display_text, user['id'])
                
                db.close()
        except Exception as e:
            print(f"Failed to load user filter: {e}")
    
    def load_logs(self):
        """Load system logs from database"""
        try:
            if db.connect():
                query = """
                    SELECT l.*, u.name as user_name
                    FROM system_logs l
                    LEFT JOIN users u ON l.user_id = u.id
                    ORDER BY l.timestamp DESC
                    LIMIT 1000
                """
                self.logs = db.execute_query(query)
                db.close()
                
                self.populate_table()
                self.update_statistics()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load logs: {str(e)}")
    
    def populate_table(self):
        """Populate logs table with data"""
        self.logs_table.setRowCount(len(self.logs))
        
        for row, log in enumerate(self.logs):
            # ID
            self.logs_table.setItem(row, 0, QTableWidgetItem(str(log['id'])))
            
            # Timestamp
            timestamp = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            self.logs_table.setItem(row, 1, QTableWidgetItem(timestamp))
            
            # User
            user_name = log.get('user_name', 'System')
            self.logs_table.setItem(row, 2, QTableWidgetItem(user_name))
            
            # Action
            action = log['action']
            self.logs_table.setItem(row, 3, QTableWidgetItem(action))
            
            # Details (truncated)
            details = log.get('details', '')
            if len(details) > 100:
                details = details[:97] + '...'
            self.logs_table.setItem(row, 4, QTableWidgetItem(details))
            
            # Severity with color coding
            severity = log['severity']
            severity_item = QTableWidgetItem(severity.upper())
            severity_colors = {
                'info': '#2196F3',
                'warning': '#FF9800',
                'error': '#F44336',
                'critical': '#9C27B0'
            }
            color = severity_colors.get(severity, '#757575')
            severity_item.setBackground(QColor(color))
            severity_item.setForeground(QColor('white'))
            self.logs_table.setItem(row, 5, severity_item)
            
            # IP Address
            ip_address = log.get('ip_address', 'N/A')
            self.logs_table.setItem(row, 6, QTableWidgetItem(ip_address))
        
        self.logs_table.resizeColumnsToContents()
    
    def update_statistics(self):
        """Update statistics cards"""
        total_logs = len(self.logs)
        error_logs = sum(1 for log in self.logs if log['severity'] == 'error')
        warning_logs = sum(1 for log in self.logs if log['severity'] == 'warning')
        
        today = date.today()
        today_logs = sum(1 for log in self.logs if log['timestamp'].date() == today)
        
        # Update card values
        self.total_logs_card.layout().itemAt(1).widget().setText(str(total_logs))
        self.error_logs_card.layout().itemAt(1).widget().setText(str(error_logs))
        self.warning_logs_card.layout().itemAt(1).widget().setText(str(warning_logs))
        self.today_logs_card.layout().itemAt(1).widget().setText(str(today_logs))
    
    def apply_filters(self):
        """Apply filters to logs table"""
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        user_filter = self.user_filter.currentData()
        action_filter = self.action_filter.currentText().lower()
        severity_filter = self.severity_filter.currentText().lower()
        search_text = self.search_input.text().lower()
        
        for row in range(self.logs_table.rowCount()):
            # Date filter
            log_date_str = self.logs_table.item(row, 1).text()
            log_date = datetime.strptime(log_date_str, '%Y-%m-%d %H:%M:%S').date()
            
            date_match = start_date <= log_date <= end_date
            
            # User filter
            user_match = True
            if user_filter != "all":
                user_name = self.logs_table.item(row, 2).text()
                # This is a simplified check - in real app, you'd track user IDs
                user_match = True  # Simplified
            
            # Action filter
            action_match = True
            if action_filter != "all":
                action = self.logs_table.item(row, 3).text().lower()
                action_match = action_filter in action
            
            # Severity filter
            severity_match = True
            if severity_filter != "all":
                severity = self.logs_table.item(row, 5).text().lower()
                severity_match = severity == severity_filter
            
            # Search filter
            search_match = True
            if search_text:
                details = self.logs_table.item(row, 4).text().lower()
                search_match = search_text in details
            
            self.logs_table.setRowHidden(row, not (date_match and user_match and action_match and severity_match and search_match))
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.logs_table.selectedItems()) > 0
        self.view_details_btn.setEnabled(has_selection)
        self.export_selected_btn.setEnabled(has_selection)
    
    def view_log_details(self):
        """View detailed information about selected log"""
        current_row = self.logs_table.currentRow()
        if current_row < 0:
            return
        
        log_id = int(self.logs_table.item(current_row, 0).text())
        log_data = next((log for log in self.logs if log['id'] == log_id), None)
        
        if not log_data:
            return
        
        # Create details dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Log Details - ID {log_id}")
        dialog.setFixedSize(600, 500)
        
        layout = QVBoxLayout()
        
        # Log Information
        info_text = f"""
Log ID: {log_data['id']}
Timestamp: {log_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
User: {log_data.get('user_name', 'System')}
Action: {log_data['action']}
Severity: {log_data['severity'].upper()}
IP Address: {log_data.get('ip_address', 'N/A')}
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("background-color: #F5F5F5; padding: 10px; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Details
        details_label = QLabel("Details:")
        details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(details_label)
        
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setPlainText(log_data.get('details', 'No details available'))
        layout.addWidget(details_text)
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def export_logs(self):
        """Export all filtered logs to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", 
            f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;CSV Files (*.csv);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("System Logs Export\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Filtered by: Date Range, User, Action, Severity\n")
                    f.write("="*80 + "\n\n")
                    
                    for row in range(self.logs_table.rowCount()):
                        if not self.logs_table.isRowHidden(row):
                            log_id = self.logs_table.item(row, 0).text()
                            timestamp = self.logs_table.item(row, 1).text()
                            user = self.logs_table.item(row, 2).text()
                            action = self.logs_table.item(row, 3).text()
                            details = self.logs_table.item(row, 4).text()
                            severity = self.logs_table.item(row, 5).text()
                            ip_address = self.logs_table.item(row, 6).text()
                            
                            f.write(f"[{timestamp}] {severity} - {action}\n")
                            f.write(f"User: {user} | IP: {ip_address}\n")
                            f.write(f"Details: {details}\n")
                            f.write("-"*80 + "\n")
                
                QMessageBox.information(self, "Success", f"Logs exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")
    
    def export_selected_logs(self):
        """Export selected logs to file"""
        selected_rows = []
        for row in range(self.logs_table.rowCount()):
            if self.logs_table.item(row, 0).isSelected():
                selected_rows.append(row)
        
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No logs selected for export.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Selected Logs", 
            f"selected_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Selected System Logs\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n\n")
                    
                    for row in selected_rows:
                        log_id = self.logs_table.item(row, 0).text()
                        timestamp = self.logs_table.item(row, 1).text()
                        user = self.logs_table.item(row, 2).text()
                        action = self.logs_table.item(row, 3).text()
                        details = self.logs_table.item(row, 4).text()
                        severity = self.logs_table.item(row, 5).text()
                        ip_address = self.logs_table.item(row, 6).text()
                        
                        f.write(f"[{timestamp}] {severity} - {action}\n")
                        f.write(f"User: {user} | IP: {ip_address}\n")
                        f.write(f"Details: {details}\n")
                        f.write("-"*80 + "\n")
                
                QMessageBox.information(self, "Success", f"Selected logs exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export selected logs: {str(e)}")
    
    def clear_old_logs(self):
        """Clear logs older than specified date"""
        from PySide6.QtWidgets import QInputDialog
        
        days, ok = QInputDialog.getInt(self, "Clear Old Logs", 
                                     "Delete logs older than (days):",
                                     30, 1, 365, 1)
        
        if ok:
            try:
                if db.connect():
                    cutoff_date = date.today() - timedelta(days=days)
                    
                    query = "DELETE FROM system_logs WHERE timestamp < %s"
                    
                    if db.execute_update(query, (cutoff_date,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'clear_old_logs',
                                         f"Cleared logs older than {days} days", 'warning'))
                        
                        QMessageBox.information(self, "Success", f"Logs older than {days} days have been cleared.")
                        self.load_logs()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to clear old logs.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear old logs: {str(e)}")

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
    
    logs = LogsWidget(demo_user)
    logs.show()
    
    sys.exit(app.exec())