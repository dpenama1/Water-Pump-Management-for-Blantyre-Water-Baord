import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QComboBox, QCheckBox,
                              QGroupBox, QFrame, QMessageBox, QTabWidget,
                              QFormLayout, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPalette, QColor
from database import db

class SettingsWidget(QWidget):
    settings_changed = Signal()
    theme_changed = Signal(str)
    
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.current_theme = 'light'
        
        self.setup_ui()
        self.load_user_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("Settings")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #1976D2;")
        layout.addWidget(header_label)
        
        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1976D2;
                color: white;
            }
        """)
        
        # Profile Tab
        self.create_profile_tab()
        
        # Appearance Tab
        self.create_appearance_tab()
        
        # System Tab
        self.create_system_tab()
        
        # Notifications Tab
        self.create_notifications_tab()
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)
    
    def create_profile_tab(self):
        """Create profile settings tab"""
        profile_widget = QWidget()
        profile_layout = QVBoxLayout()
        profile_layout.setSpacing(15)
        
        # Profile Information
        profile_group = QGroupBox("Profile Information")
        profile_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setMaxLength(100)
        form_layout.addRow("Full Name:*", self.name_input)
        
        # Job ID (read-only)
        self.job_id_label = QLabel()
        self.job_id_label.setStyleSheet("padding: 8px; background-color: #F5F5F5; border-radius: 4px;")
        form_layout.addRow("Job ID:", self.job_id_label)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setMaxLength(100)
        form_layout.addRow("Email:*", self.email_input)
        
        # Department
        self.department_combo = QComboBox()
        self.department_combo.addItems([
            "Engineering",
            "Maintenance",
            "Operations",
            "Quality Control",
            "Safety",
            "Management",
            "IT Support",
            "Other"
        ])
        self.department_combo.setEditable(True)
        form_layout.addRow("Department:*", self.department_combo)
        
        # Job Type
        self.job_type_combo = QComboBox()
        self.job_type_combo.addItems([
            "Technician",
            "Senior Technician",
            "Supervisor",
            "Manager",
            "Engineer",
            "Administrator",
            "Other"
        ])
        self.job_type_combo.setEditable(True)
        form_layout.addRow("Job Type:*", self.job_type_combo)
        
        profile_group.setLayout(form_layout)
        profile_layout.addWidget(profile_group)
        
        # Change Password Section
        password_group = QGroupBox("Change Password")
        password_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        password_form = QFormLayout()
        password_form.setSpacing(10)
        
        # Current Password
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password.setPlaceholderText("Enter current password")
        password_form.addRow("Current Password:", self.current_password)
        
        # New Password
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password.setPlaceholderText("Enter new password")
        password_form.addRow("New Password:", self.new_password)
        
        # Confirm Password
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password.setPlaceholderText("Confirm new password")
        password_form.addRow("Confirm Password:", self.confirm_password)
        
        password_group.setLayout(password_form)
        profile_layout.addWidget(password_group)
        
        # Save Button
        save_profile_btn = QPushButton("💾 Save Profile Changes")
        save_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_profile_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_profile_btn)
        
        profile_widget.setLayout(profile_layout)
        self.tab_widget.addTab(profile_widget, "👤 Profile")
    
    def create_appearance_tab(self):
        """Create appearance settings tab"""
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(15)
        
        # Theme Selection
        theme_group = QGroupBox("Theme")
        theme_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(10)
        
        # Theme buttons
        self.theme_group = QButtonGroup()
        
        light_theme = QRadioButton("Light Theme")
        light_theme.setChecked(True)
        self.theme_group.addButton(light_theme, 0)
        theme_layout.addWidget(light_theme)
        
        dark_theme = QRadioButton("Dark Theme")
        self.theme_group.addButton(dark_theme, 1)
        theme_layout.addWidget(dark_theme)
        
        # Theme preview
        preview_label = QLabel("Theme Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        theme_layout.addWidget(preview_label)
        
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.Box)
        preview_frame.setMinimumHeight(100)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        theme_layout.addWidget(preview_frame)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        # Font Settings
        font_group = QGroupBox("Font Settings")
        font_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        font_layout = QFormLayout()
        font_layout.setSpacing(10)
        
        # Font Size
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["Small", "Medium", "Large", "Extra Large"])
        self.font_size_combo.setCurrentText("Medium")
        font_layout.addRow("Font Size:", self.font_size_combo)
        
        # Font Family
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "Arial", "Helvetica", "Times New Roman", "Courier New", 
            "Verdana", "Georgia", "Tahoma", "Trebuchet MS"
        ])
        self.font_family_combo.setCurrentText("Arial")
        font_layout.addRow("Font Family:", self.font_family_combo)
        
        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)
        
        # Apply Theme Button
        apply_theme_btn = QPushButton("🎨 Apply Theme")
        apply_theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        apply_theme_btn.clicked.connect(self.apply_theme)
        appearance_layout.addWidget(apply_theme_btn)
        
        appearance_widget.setLayout(appearance_layout)
        self.tab_widget.addTab(appearance_widget, "🎨 Appearance")
    
    def create_system_tab(self):
        """Create system settings tab"""
        system_widget = QWidget()
        system_layout = QVBoxLayout()
        system_layout.setSpacing(15)
        
        # Auto-Refresh Settings
        refresh_group = QGroupBox("Auto-Refresh Settings")
        refresh_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        refresh_layout = QFormLayout()
        refresh_layout.setSpacing(10)
        
        # Dashboard Refresh Interval
        self.refresh_interval_combo = QComboBox()
        self.refresh_interval_combo.addItems([
            "5 seconds", "10 seconds", "30 seconds", 
            "1 minute", "2 minutes", "5 minutes", "Disabled"
        ])
        self.refresh_interval_combo.setCurrentText("5 seconds")
        refresh_layout.addRow("Dashboard Refresh:", self.refresh_interval_combo)
        
        # Log Refresh Interval
        self.log_refresh_combo = QComboBox()
        self.log_refresh_combo.addItems([
            "10 seconds", "30 seconds", "1 minute", 
            "2 minutes", "5 minutes", "Disabled"
        ])
        self.log_refresh_combo.setCurrentText("1 minute")
        refresh_layout.addRow("Logs Refresh:", self.log_refresh_combo)
        
        refresh_group.setLayout(refresh_layout)
        system_layout.addWidget(refresh_group)
        
        # Session Settings
        session_group = QGroupBox("Session Settings")
        session_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        session_layout = QFormLayout()
        session_layout.setSpacing(10)
        
        # Session Timeout
        self.session_timeout_combo = QComboBox()
        self.session_timeout_combo.addItems([
            "15 minutes", "30 minutes", "1 hour", 
            "2 hours", "4 hours", "8 hours", "Never"
        ])
        self.session_timeout_combo.setCurrentText("30 minutes")
        session_layout.addRow("Session Timeout:", self.session_timeout_combo)
        
        # Auto-save Settings
        self.auto_save_check = QCheckBox("Auto-save form data")
        self.auto_save_check.setChecked(True)
        session_layout.addRow("", self.auto_save_check)
        
        session_group.setLayout(session_layout)
        system_layout.addWidget(session_group)
        
        # Database Settings
        db_group = QGroupBox("Database Settings")
        db_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        db_layout = QFormLayout()
        db_layout.setSpacing(10)
        
        # Connection Timeout
        self.connection_timeout_combo = QComboBox()
        self.connection_timeout_combo.addItems([
            "5 seconds", "10 seconds", "30 seconds", "1 minute", "2 minutes"
        ])
        self.connection_timeout_combo.setCurrentText("30 seconds")
        db_layout.addRow("Connection Timeout:", self.connection_timeout_combo)
        
        # Auto-backup
        self.auto_backup_check = QCheckBox("Enable automatic backups")
        self.auto_backup_check.setChecked(True)
        db_layout.addRow("", self.auto_backup_check)
        
        db_group.setLayout(db_layout)
        system_layout.addWidget(db_group)
        
        # Save System Settings Button
        save_system_btn = QPushButton("⚙️ Save System Settings")
        save_system_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        save_system_btn.clicked.connect(self.save_system_settings)
        system_layout.addWidget(save_system_btn)
        
        system_widget.setLayout(system_layout)
        self.tab_widget.addTab(system_widget, "⚙️ System")
    
    def create_notifications_tab(self):
        """Create notifications settings tab"""
        notifications_widget = QWidget()
        notifications_layout = QVBoxLayout()
        notifications_layout.setSpacing(15)
        
        # Email Notifications
        email_group = QGroupBox("Email Notifications")
        email_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        email_layout = QVBoxLayout()
        email_layout.setSpacing(10)
        
        # Email Settings
        self.email_enabled_check = QCheckBox("Enable email notifications")
        self.email_enabled_check.setChecked(True)
        email_layout.addWidget(self.email_enabled_check)
        
        # Email Address
        self.notification_email_input = QLineEdit()
        self.notification_email_input.setPlaceholderText("Notification email address")
        email_layout.addWidget(QLabel("Email Address:"))
        email_layout.addWidget(self.notification_email_input)
        
        # Notification Types
        email_layout.addWidget(QLabel("Notify me about:"))
        
        self.pump_alerts_check = QCheckBox("Pump status changes and alerts")
        self.pump_alerts_check.setChecked(True)
        email_layout.addWidget(self.pump_alerts_check)
        
        self.maintenance_alerts_check = QCheckBox("Maintenance schedule reminders")
        self.maintenance_alerts_check.setChecked(True)
        email_layout.addWidget(self.maintenance_alerts_check)
        
        self.inventory_alerts_check = QCheckBox("Low inventory alerts")
        self.inventory_alerts_check.setChecked(True)
        email_layout.addWidget(self.inventory_alerts_check)
        
        self.system_alerts_check = QCheckBox("System errors and warnings")
        self.system_alerts_check.setChecked(True)
        email_layout.addWidget(self.system_alerts_check)
        
        email_group.setLayout(email_layout)
        notifications_layout.addWidget(email_group)
        
        # Dashboard Notifications
        dashboard_group = QGroupBox("Dashboard Notifications")
        dashboard_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
            }
        """)
        
        dashboard_layout = QVBoxLayout()
        dashboard_layout.setSpacing(10)
        
        self.dashboard_alerts_check = QCheckBox("Show alerts on dashboard")
        self.dashboard_alerts_check.setChecked(True)
        dashboard_layout.addWidget(self.dashboard_alerts_check)
        
        self.sound_alerts_check = QCheckBox("Play sound for critical alerts")
        self.sound_alerts_check.setChecked(True)
        dashboard_layout.addWidget(self.sound_alerts_check)
        
        # Alert Frequency
        self.alert_frequency_combo = QComboBox()
        self.alert_frequency_combo.addItems([
            "Immediate", "Every 5 minutes", "Every 15 minutes", 
            "Every 30 minutes", "Hourly"
        ])
        self.alert_frequency_combo.setCurrentText("Immediate")
        dashboard_layout.addWidget(QLabel("Alert Frequency:"))
        dashboard_layout.addWidget(self.alert_frequency_combo)
        
        dashboard_group.setLayout(dashboard_layout)
        notifications_layout.addWidget(dashboard_group)
        
        # Save Notification Settings Button
        save_notifications_btn = QPushButton("🔔 Save Notification Settings")
        save_notifications_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        save_notifications_btn.clicked.connect(self.save_notification_settings)
        notifications_layout.addWidget(save_notifications_btn)
        
        notifications_widget.setLayout(notifications_layout)
        self.tab_widget.addTab(notifications_widget, "🔔 Notifications")
    
    def load_user_settings(self):
        """Load current user settings"""
        try:
            if db.connect():
                # Load user data
                query = "SELECT * FROM users WHERE id = %s"
                user_data = db.execute_query(query, (self.user_data['id'],))
                
                if user_data:
                    user = user_data[0]
                    self.name_input.setText(user.get('name', ''))
                    self.job_id_label.setText(user.get('job_id', ''))
                    self.email_input.setText(user.get('email', ''))
                    
                    # Set department
                    department = user.get('department', '')
                    index = self.department_combo.findText(department)
                    if index >= 0:
                        self.department_combo.setCurrentIndex(index)
                    else:
                        self.department_combo.setCurrentText(department)
                    
                    # Set job type
                    job_type = user.get('job_type', '')
                    index = self.job_type_combo.findText(job_type)
                    if index >= 0:
                        self.job_type_combo.setCurrentIndex(index)
                    else:
                        self.job_type_combo.setCurrentText(job_type)
                
                db.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user settings: {str(e)}")
    
    def save_profile(self):
        """Save profile changes"""
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        department = self.department_combo.currentText().strip()
        job_type = self.job_type_combo.currentText().strip()
        
        if not name or not email or not department or not job_type:
            QMessageBox.warning(self, "Warning", "Please fill in all required fields.")
            return
        
        try:
            if db.connect():
                query = """
                    UPDATE users 
                    SET name = %s, email = %s, department = %s, job_type = %s
                    WHERE id = %s
                """
                params = (name, email, department, job_type, self.user_data['id'])
                
                if db.execute_update(query, params):
                    # Handle password change if provided
                    current_password = self.current_password.text()
                    new_password = self.new_password.text()
                    confirm_password = self.confirm_password.text()
                    
                    if current_password and new_password and confirm_password:
                        if new_password != confirm_password:
                            QMessageBox.warning(self, "Warning", "New passwords do not match.")
                            db.close()
                            return
                        
                        # Update password (simplified - in production, verify current password first)
                        password_query = "UPDATE users SET password = %s WHERE id = %s"
                        db.execute_update(password_query, (new_password, self.user_data['id']))
                        
                        # Clear password fields
                        self.current_password.clear()
                        self.new_password.clear()
                        self.confirm_password.clear()
                    
                    # Log the action
                    log_query = """
                        INSERT INTO system_logs (user_id, action, details, severity)
                        VALUES (%s, %s, %s, %s)
                    """
                    db.execute_update(log_query, 
                                    (self.user_data['id'], 'update_profile',
                                     f"Updated profile for user: {name}", 'info'))
                    
                    QMessageBox.information(self, "Success", "Profile updated successfully!")
                    self.settings_changed.emit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update profile.")
                
                db.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update profile: {str(e)}")
    
    def apply_theme(self):
        """Apply selected theme"""
        if self.theme_group.button(0).isChecked():
            theme = 'light'
        else:
            theme = 'dark'
        
        self.current_theme = theme
        self.theme_changed.emit(theme)
        
        QMessageBox.information(self, "Theme Applied", f"{theme.title()} theme has been applied.")
    
    def save_system_settings(self):
        """Save system settings"""
        try:
            if db.connect():
                # In a real application, these settings would be saved to a configuration table
                settings = {
                    'refresh_interval': self.refresh_interval_combo.currentText(),
                    'log_refresh': self.log_refresh_combo.currentText(),
                    'session_timeout': self.session_timeout_combo.currentText(),
                    'auto_save': self.auto_save_check.isChecked(),
                    'connection_timeout': self.connection_timeout_combo.currentText(),
                    'auto_backup': self.auto_backup_check.isChecked()
                }
                
                # Log the action
                log_query = """
                    INSERT INTO system_logs (user_id, action, details, severity)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute_update(log_query, 
                                (self.user_data['id'], 'update_system_settings',
                                 "Updated system configuration settings", 'info'))
                
                QMessageBox.information(self, "Success", "System settings saved successfully!")
                db.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save system settings: {str(e)}")
    
    def save_notification_settings(self):
        """Save notification settings"""
        try:
            if db.connect():
                # In a real application, these settings would be saved to user preferences
                settings = {
                    'email_enabled': self.email_enabled_check.isChecked(),
                    'notification_email': self.notification_email_input.text(),
                    'pump_alerts': self.pump_alerts_check.isChecked(),
                    'maintenance_alerts': self.maintenance_alerts_check.isChecked(),
                    'inventory_alerts': self.inventory_alerts_check.isChecked(),
                    'system_alerts': self.system_alerts_check.isChecked(),
                    'dashboard_alerts': self.dashboard_alerts_check.isChecked(),
                    'sound_alerts': self.sound_alerts_check.isChecked(),
                    'alert_frequency': self.alert_frequency_combo.currentText()
                }
                
                # Log the action
                log_query = """
                    INSERT INTO system_logs (user_id, action, details, severity)
                    VALUES (%s, %s, %s, %s)
                """
                db.execute_update(log_query, 
                                (self.user_data['id'], 'update_notification_settings',
                                 "Updated notification preferences", 'info'))
                
                QMessageBox.information(self, "Success", "Notification settings saved successfully!")
                db.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save notification settings: {str(e)}")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Initialize database
    db.init_database()
    
    # Demo user data
    demo_user = {
        'id': 1,
        'name': 'Demo User',
        'job_id': 'TECH001'
    }
    
    settings = SettingsWidget(demo_user)
    settings.show()
    
    sys.exit(app.exec())