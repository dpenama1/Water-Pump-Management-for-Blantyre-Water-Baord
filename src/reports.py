import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                              QComboBox, QDateEdit, QTextEdit, QMessageBox,
                              QGroupBox, QHeaderView, QFrame, QFileDialog, QInputDialog)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QIcon, QColor
from datetime import datetime, date
from database import db
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class ReportsWidget(QWidget):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.reports = []
        
        self.setup_ui()
        self.load_reports()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Reports Management")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976D2;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Generate Report Button
        self.generate_btn = QPushButton("📊 Generate Report")
        self.generate_btn.setStyleSheet("""
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
        self.generate_btn.clicked.connect(self.generate_report)
        header_layout.addWidget(self.generate_btn)
        
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
        self.refresh_btn.clicked.connect(self.load_reports)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Report Generation Section
        report_gen_group = QGroupBox("Generate New Report")
        report_gen_group.setStyleSheet("""
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
        
        report_gen_layout = QVBoxLayout()
        report_gen_layout.setSpacing(10)
        
        # Report Type and Date Range
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)
        
        # Report Type
        type_layout = QVBoxLayout()
        type_label = QLabel("Report Type:")
        type_label.setStyleSheet("font-weight: bold;")
        type_layout.addWidget(type_label)
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Pump Performance Summary",
            "Maintenance History",
            "Inventory Status",
            "System Activity Logs",
            "User Activity Report",
            "Maintenance Schedule",
            "Pump Status Overview",
            "Inventory Alerts",
            "Custom Report"
        ])
        self.report_type_combo.currentTextChanged.connect(self.on_report_type_changed)
        type_layout.addWidget(self.report_type_combo)
        form_layout.addLayout(type_layout)
        
        # Date Range
        date_layout = QVBoxLayout()
        date_label = QLabel("Date Range:")
        date_label.setStyleSheet("font-weight: bold;")
        date_layout.addWidget(date_label)
        
        date_range_layout = QHBoxLayout()
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        date_range_layout.addWidget(QLabel("From:"))
        date_range_layout.addWidget(self.start_date)
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        date_range_layout.addWidget(QLabel("To:"))
        date_range_layout.addWidget(self.end_date)
        
        date_layout.addLayout(date_range_layout)
        form_layout.addLayout(date_layout)
        
        report_gen_layout.addLayout(form_layout)
        
        # Filters
        self.filters_group = QGroupBox("Report Filters")
        self.filters_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            }
        """)
        
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)
        
        # Pump Filter
        self.pump_filter_combo = QComboBox()
        self.pump_filter_combo.addItem("All Pumps", "all")
        # Will be populated with actual pump data
        
        # Technician Filter
        self.tech_filter_combo = QComboBox()
        self.tech_filter_combo.addItem("All Technicians", "all")
        # Will be populated with actual technician data
        
        # Priority Filter
        self.priority_filter_combo = QComboBox()
        self.priority_filter_combo.addItem("All Priorities", "all")
        self.priority_filter_combo.addItem("Low", "low")
        self.priority_filter_combo.addItem("Medium", "medium")
        self.priority_filter_combo.addItem("High", "high")
        self.priority_filter_combo.addItem("Urgent", "urgent")
        
        filters_layout.addWidget(QLabel("Pump:"))
        filters_layout.addWidget(self.pump_filter_combo)
        filters_layout.addWidget(QLabel("Technician:"))
        filters_layout.addWidget(self.tech_filter_combo)
        filters_layout.addWidget(QLabel("Priority:"))
        filters_layout.addWidget(self.priority_filter_combo)
        
        self.filters_group.setLayout(filters_layout)
        report_gen_layout.addWidget(self.filters_group)
        
        # Report Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Report Description:")
        desc_label.setStyleSheet("font-weight: bold;")
        desc_layout.addWidget(desc_label)
        
        self.report_desc = QTextEdit()
        self.report_desc.setPlaceholderText("Enter description for this report...")
        self.report_desc.setMaximumHeight(80)
        desc_layout.addWidget(self.report_desc)
        
        report_gen_layout.addLayout(desc_layout)
        
        # Generate Button
        generate_layout = QHBoxLayout()
        generate_layout.addStretch()
        
        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.setStyleSheet("""
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
        """)
        self.generate_report_btn.clicked.connect(self.create_report)
        generate_layout.addWidget(self.generate_report_btn)
        
        report_gen_layout.addLayout(generate_layout)
        
        report_gen_group.setLayout(report_gen_layout)
        layout.addWidget(report_gen_group)
        
        # Existing Reports Table
        reports_group = QGroupBox("Existing Reports")
        reports_group.setStyleSheet("""
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
        
        reports_layout = QVBoxLayout()
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search reports by name or type...")
        self.search_input.textChanged.connect(self.filter_reports)
        search_layout.addWidget(self.search_input)
        
        reports_layout.addLayout(search_layout)
        
        # Reports Table
        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(8)
        self.reports_table.setHorizontalHeaderLabels([
            "ID", "Report Name", "Type", "Date Range", "Generated By", 
            "Created Date", "Status", "Actions"
        ])
        
        # Table styling
        self.reports_table.setStyleSheet("""
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
        header = self.reports_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        self.reports_table.setAlternatingRowColors(True)
        self.reports_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        reports_layout.addWidget(self.reports_table)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        
        self.view_btn = QPushButton("👁️ View Report")
        self.view_btn.setStyleSheet("""
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
        self.view_btn.clicked.connect(self.view_report)
        self.view_btn.setEnabled(False)
        
        self.download_btn = QPushButton("⬇️ Download")
        self.download_btn.setStyleSheet("""
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
        self.download_btn.clicked.connect(self.download_report)
        self.download_btn.setEnabled(False)
        
        self.email_btn = QPushButton("📧 Email Report")
        self.email_btn.setStyleSheet("""
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
        self.email_btn.clicked.connect(self.email_report)
        self.email_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("🗑️ Delete")
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
        self.delete_btn.clicked.connect(self.delete_report)
        self.delete_btn.setEnabled(False)
        
        action_layout.addWidget(self.view_btn)
        action_layout.addWidget(self.download_btn)
        action_layout.addWidget(self.email_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addStretch()
        
        reports_layout.addLayout(action_layout)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        self.setLayout(layout)
        
        # Connect table selection
        self.reports_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Initialize
        self.on_report_type_changed()
    
    def on_report_type_changed(self):
        """Update UI based on selected report type"""
        report_type = self.report_type_combo.currentText()
        
        # Show/hide filters based on report type
        if "Pump" in report_type:
            self.pump_filter_combo.setEnabled(True)
            self.tech_filter_combo.setEnabled(False)
            self.priority_filter_combo.setEnabled(False)
        elif "Maintenance" in report_type:
            self.pump_filter_combo.setEnabled(True)
            self.tech_filter_combo.setEnabled(True)
            self.priority_filter_combo.setEnabled(True)
        elif "User" in report_type:
            self.pump_filter_combo.setEnabled(False)
            self.tech_filter_combo.setEnabled(True)
            self.priority_filter_combo.setEnabled(False)
        else:
            self.pump_filter_combo.setEnabled(False)
            self.tech_filter_combo.setEnabled(False)
            self.priority_filter_combo.setEnabled(False)
        
        # Update description
        descriptions = {
            "Pump Performance Summary": "Comprehensive analysis of pump performance metrics and operational data",
            "Maintenance History": "Complete maintenance records and scheduling analysis",
            "Inventory Status": "Current inventory levels and stock management overview",
            "System Activity Logs": "Detailed system usage and activity tracking",
            "User Activity Report": "User login and system interaction analysis",
            "Maintenance Schedule": "Upcoming and overdue maintenance tasks",
            "Pump Status Overview": "Current status of all water pumps",
            "Inventory Alerts": "Low stock and reorder notifications",
            "Custom Report": "Customizable report with selected parameters"
        }
        
        self.report_desc.setPlainText(descriptions.get(report_type, "Custom report"))
    
    def load_reports(self):
        """Load existing reports from database"""
        try:
            if db.connect():
                query = """
                    SELECT r.*, u.name as generated_by_name
                    FROM reports r
                    LEFT JOIN users u ON r.generated_by = u.id
                    ORDER BY r.created_at DESC
                """
                self.reports = db.execute_query(query)
                db.close()
                
                self.populate_reports_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reports: {str(e)}")
    
    def populate_reports_table(self):
        """Populate reports table with data"""
        self.reports_table.setRowCount(len(self.reports))
        
        for row, report in enumerate(self.reports):
            # ID
            self.reports_table.setItem(row, 0, QTableWidgetItem(str(report['id'])))
            
            # Report Name
            self.reports_table.setItem(row, 1, QTableWidgetItem(report['report_name']))
            
            # Type
            self.reports_table.setItem(row, 2, QTableWidgetItem(report['report_type']))
            
            # Date Range
            start_date = report.get('start_date', '')
            end_date = report.get('end_date', '')
            if start_date and end_date:
                date_range = f"{start_date} to {end_date}"
            else:
                date_range = "All Time"
            self.reports_table.setItem(row, 3, QTableWidgetItem(date_range))
            
            # Generated By
            generated_by = report.get('generated_by_name', 'Unknown')
            self.reports_table.setItem(row, 4, QTableWidgetItem(generated_by))
            
            # Created Date
            created_date = report['created_at'].strftime('%Y-%m-%d %H:%M')
            self.reports_table.setItem(row, 5, QTableWidgetItem(created_date))
            
            # Status
            status = report.get('status', 'pending')
            status_item = QTableWidgetItem(status.upper())
            status_colors = {
                'completed': '#4CAF50',
                'pending': '#FF9800',
                'failed': '#F44336'
            }
            color = status_colors.get(status, '#757575')
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor('white'))
            self.reports_table.setItem(row, 6, status_item)
        
        self.reports_table.resizeColumnsToContents()
    
    def filter_reports(self):
        """Filter reports based on search text"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.reports_table.rowCount()):
            name = self.reports_table.item(row, 1).text().lower()
            type_text = self.reports_table.item(row, 2).text().lower()
            
            match = search_text in name or search_text in type_text
            self.reports_table.setRowHidden(row, not match)
    
    def on_selection_changed(self):
        """Enable/disable buttons based on selection"""
        has_selection = len(self.reports_table.selectedItems()) > 0
        self.view_btn.setEnabled(has_selection)
        self.download_btn.setEnabled(has_selection)
        self.email_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def generate_report(self):
        """Open report generation dialog"""
        self.generate_report_btn.setEnabled(False)
        
        # This would typically show the report generation form
        # For now, we'll just enable the main generate button
        self.generate_report_btn.setEnabled(True)
    
    def create_report(self):
        """Create a new report based on form data"""
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date.date().toPython()
        end_date = self.end_date.date().toPython()
        description = self.report_desc.toPlainText().strip()
        
        if not description:
            QMessageBox.warning(self, "Warning", "Please enter a description for the report.")
            return
        
        try:
            if db.connect():
                # Create report record
                query = """
                    INSERT INTO reports (report_name, report_type, start_date, end_date,
                                       description, generated_by, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                report_name = f"{report_type} - {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                params = (report_name, report_type, start_date, end_date, description, self.user_data['id'], 'pending')

                cursor = db.connection.cursor()
                cursor.execute(query, params)
                db.connection.commit()
                report_id = cursor.lastrowid  # <--- Capture ID here
                cursor.close()

                if report_id:
                    # Generate report content
                    report_content = self.generate_report_content(report_type, start_date, end_date)

                    #reconnection to the database
                    db.connect()

                    # Update report with content and mark as completed
                    update_query = """
                                   UPDATE reports \
                                   SET content = %s, \
                                       status  = 'completed' \
                                   WHERE id = %s \
                                   """
                    db.execute_update(update_query, (report_content, report_id))

                    # Log the action
                    log_query = """
                                INSERT INTO system_logs (user_id, action, details, severity)
                                VALUES (%s, %s, %s, %s) \
                                """
                    db.execute_update(log_query,
                                      (self.user_data['id'], 'generate_report',
                                       f"Generated report: {report_name}", 'info'))

                    QMessageBox.information(self, "Success", "Report generated successfully!")
                    self.load_reports()
                else:
                    QMessageBox.critical(self, "Error", "Failed to generate report ID.")
                
                db.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    
    def generate_report_content(self, report_type, start_date, end_date):
        """Generate report content based on type"""
        try:
            if db.connect():
                content = {}
                
                if report_type == "Pump Performance Summary":
                    query = """
                        SELECT w.*, AVG(r.pressure) as avg_pressure, AVG(r.flow_rate) as avg_flow,
                               COUNT(r.id) as reading_count
                        FROM water_pumps w
                        LEFT JOIN pump_readings r ON w.id = r.pump_id
                        WHERE r.timestamp BETWEEN %s AND %s
                        GROUP BY w.id
                    """
                    content['pump_performance'] = db.execute_query(query, (start_date, end_date))
                
                elif report_type == "Maintenance History":
                    query = """
                        SELECT m.*, w.pump_name, u.name as technician_name
                        FROM maintenance_schedule m
                        LEFT JOIN water_pumps w ON m.pump_id = w.id
                        LEFT JOIN users u ON m.assigned_technician_id = u.id
                        WHERE m.scheduled_date BETWEEN %s AND %s
                        ORDER BY m.scheduled_date
                    """
                    content['maintenance_history'] = db.execute_query(query, (start_date, end_date))
                
                elif report_type == "Inventory Status":
                    query = "SELECT * FROM inventory ORDER BY category, part_name"
                    content['inventory_status'] = db.execute_query(query)
                
                elif report_type == "System Activity Logs":
                    query = """
                        SELECT l.*, u.name as user_name
                        FROM system_logs l
                        LEFT JOIN users u ON l.user_id = u.id
                        WHERE l.timestamp BETWEEN %s AND %s
                        ORDER BY l.timestamp DESC
                    """
                    content['system_logs'] = db.execute_query(query, (start_date, end_date))
                
                elif report_type == "User Activity Report":
                    query = """
                        SELECT u.name, u.job_id, u.last_login, COUNT(l.id) as activity_count
                        FROM users u
                        LEFT JOIN system_logs l ON u.id = l.user_id AND l.timestamp BETWEEN %s AND %s
                        GROUP BY u.id
                        ORDER BY activity_count DESC
                    """
                    content['user_activity'] = db.execute_query(query, (start_date, end_date))
                
                db.close()
                
                return json.dumps(content, default=str, indent=2)
                
        except Exception as e:
            return json.dumps({'error': str(e)})
    
    def view_report(self):
        """View selected report"""
        current_row = self.reports_table.currentRow()
        if current_row < 0:
            return
        
        report_id = int(self.reports_table.item(current_row, 0).text())
        report_data = next((r for r in self.reports if r['id'] == report_id), None)
        
        if not report_data:
            return
        
        # Create report viewer dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(f"View Report: {report_data['report_name']}")
        dialog.setFixedSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Report Info
        info_text = f"""
Report Name: {report_data['report_name']}
Type: {report_data['report_type']}
Generated By: {report_data.get('generated_by_name', 'Unknown')}
Date Range: {report_data.get('start_date', 'N/A')} to {report_data.get('end_date', 'N/A')}
Generated: {report_data['created_at'].strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("background-color: #F5F5F5; padding: 10px; border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Report Content
        content_text = QTextEdit()
        content_text.setReadOnly(True)
        content_text.setPlainText(report_data.get('content', 'No content available'))
        layout.addWidget(content_text)
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def download_report(self):
        """Download selected report"""
        current_row = self.reports_table.currentRow()
        if current_row < 0:
            return
        
        report_id = int(self.reports_table.item(current_row, 0).text())
        report_data = next((r for r in self.reports if r['id'] == report_id), None)
        
        if not report_data:
            return
        
        # Save file dialog
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Report", 
            f"{report_data['report_name']}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(f"Report: {report_data['report_name']}\n")
                    f.write(f"Type: {report_data['report_type']}\n")
                    f.write(f"Generated: {report_data['created_at']}\n")
                    f.write(f"Description: {report_data.get('description', '')}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    f.write(report_data.get('content', 'No content available'))
                
                QMessageBox.information(self, "Success", f"Report saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save report: {str(e)}")

    def email_report(self):
        """Email selected report"""
        # 1. Get the selected report data
        current_row = self.reports_table.currentRow()
        if current_row < 0:
            return

        report_id = int(self.reports_table.item(current_row, 0).text())
        report_data = next((r for r in self.reports if r['id'] == report_id), None)

        if not report_data:
            return

        # 2. Ask user for recipient email
        recipient, ok = QInputDialog.getText(self, "Email Report",
                                             "Enter recipient email address:",
                                             QLineEdit.EchoMode.Normal)

        if ok and recipient:
            # 3. Prepare the content (Formatted nicely like the download function)
            formatted_content = f"Report: {report_data['report_name']}\n"
            formatted_content += f"Type: {report_data['report_type']}\n"
            formatted_content += f"Generated: {report_data['created_at']}\n"
            formatted_content += f"Description: {report_data.get('description', '')}\n"
            formatted_content += "\n" + "=" * 50 + "\n\n"
            formatted_content += report_data.get('content', 'No content available')

            # 4. Send the email
            self.send_email_via_smtp(recipient, report_data['report_name'], formatted_content)

    def send_email_via_smtp(self, recipient, subject, body_content):
        """Helper function to send email using SMTP"""
        # ==========================================
        # ⚠️ CONFIGURE YOUR EMAIL SETTINGS HERE ⚠️
        # For Gmail, you must use an 'App Password', not your normal password.
        # ==========================================
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587
        SENDER_EMAIL = "dpenama1@gmail.com"  # <--- CHANGE THIS
        SENDER_PASSWORD = "wfkl rgzz wlis rhnk"  # <--- CHANGE THIS
        # ==========================================

        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = f"BWB Water-pump System Notification: {subject}"

        # Add body text
        body = "Please find the generated report attached."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the report as a text file
        try:
            # Create the attachment
            part = MIMEApplication(body_content.encode('utf-8'), Name=f"{subject}.txt")
            part['Content-Disposition'] = f'attachment; filename="{subject}.txt"'
            msg.attach(part)

            # Connect to Server and Send
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()  # Secure the connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()

            # Log the success
            self.log_email_action(recipient, "success")
            QMessageBox.information(self, "Success", f"Email sent successfully to {recipient}")

        except Exception as e:
            # Log the failure
            self.log_email_action(recipient, "failed")
            QMessageBox.critical(self, "Email Error", f"Failed to send email.\nError: {str(e)}")

    def log_email_action(self, recipient, status):
        """Log the email attempt"""
        try:
            if db.connect():
                log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s) \
                            """
                details = f"Email report to {recipient}: {status}"
                severity = 'info' if status == 'success' else 'error'

                db.execute_update(log_query,
                                  (self.user_data['id'], 'email_report', details, severity))
                db.close()
        except Exception:
            pass  # Fail silently if logging fails, as user already saw the message

    def delete_report(self):
        """Delete selected report"""
        current_row = self.reports_table.currentRow()
        if current_row < 0:
            return
        
        report_id = int(self.reports_table.item(current_row, 0).text())
        report_name = self.reports_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete report '{report_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    query = "DELETE FROM reports WHERE id = %s"
                    
                    if db.execute_update(query, (report_id,)):
                        # Log the action
                        log_query = """
                            INSERT INTO system_logs (user_id, action, details, severity)
                            VALUES (%s, %s, %s, %s)
                        """
                        db.execute_update(log_query, 
                                        (self.user_data['id'], 'delete_report',
                                         f"Deleted report: {report_name}", 'warning'))
                        
                        QMessageBox.information(self, "Success", "Report deleted successfully!")
                        self.load_reports()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to delete report.")
                    
                    db.close()
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete report: {str(e)}")

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
    
    reports = ReportsWidget(demo_user)
    reports.show()
    
    sys.exit(app.exec())