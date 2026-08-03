import sys
import os
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                              QPushButton, QLabel, QFrame, QStackedWidget,
                              QMessageBox, QStatusBar, QMenuBar, QMenu,
                              QApplication, QDialog)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from datetime import datetime, timedelta

from login_dialog import LoginDialog
from dashboard import DashboardWidget
from pump_management import PumpManagementWidget
from maintenance import MaintenanceWidget
from inventory import InventoryWidget
from reports import ReportsWidget
from logs import LogsWidget
from settings import SettingsWidget
from database import db
from config import THEMES

class NavigationButton(QPushButton):
    def __init__(self, text, icon=None, parent=None):
        super().__init__(parent)
        self.setText(text)
        if icon:
            self.setText(f"{icon} {text}")

        self.setCheckable(True)
        self.setAutoExclusive(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: #F5F5F5;
                color: #212121;
                border: none;
                padding: 12px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                border-radius: 6px;
                margin: 2px 0px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QPushButton:checked {
                background-color: #1976D2;
                color: white;
                font-weight: bold;
            }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_data = None
        self.current_theme = 'light'
        self.auto_refresh_timer = QTimer()
        self.session_timer = QTimer()
        self.last_activity = datetime.now()

        self.setup_ui()
        self.show_login()

    def setup_ui(self):
        self.setWindowTitle("Water Pump Management System")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main Layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar)

        # Content Area
        self.create_content_area()
        main_layout.addWidget(self.content_area, 1)

        central_widget.setLayout(main_layout)

        # Menu Bar
        self.create_menu_bar()

        # Status Bar
        self.create_status_bar()

        # Apply initial theme
        self.apply_theme(self.current_theme)

    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border-right: 2px solid #E0E0E0;
            }
        """)

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setSpacing(5)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)

        # Logo/Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #1976D2;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 10px;
            }
        """)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        # --- PATH FIX START ---
        # 1. Get the folder where this script (main_window.py) lives (the 'src' folder)
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 2. Go up one level (..), then into 'resources', then 'bwb_logo.png'
        # Final path: water_pump_management/resources/bwb_logo.png
        image_path = os.path.join(base_dir, '..', 'resources', 'bwb_logo.png')

        logo_label = QLabel()
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            # Fallback if image not found: Show text instead of empty space
            print(f"Error: Could not find image at {image_path}")
            logo_label.setText("BWB Logo\n(Missing)")
            logo_label.setStyleSheet("color: white; font-weight: bold;")
        else:
            # Scale image if found
            scaled_pixmap = pixmap.scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)

        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label)
        # --- PATH FIX END ---

        app_name = QLabel("Blantyre Water Board\nWater Pump\nManagement &\nInventory system")
        app_name.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet("color: white;")
        header_layout.addWidget(app_name)

        header_frame.setLayout(header_layout)
        sidebar_layout.addWidget(header_frame)

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "📊", 0),
            ("Pump Management", "🔧", 1),
            ("Maintenance", "🔨", 2),
            ("Inventory", "📦", 3),
            ("Reports", "📈", 4),
            ("System Logs", "📋", 5),
            ("Settings", "⚙️", 6)
        ]

        for text, icon, index in nav_items:
            btn = NavigationButton(text, icon)
            btn.clicked.connect(lambda checked, i=index: self.switch_page(i))
            self.nav_buttons[text] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # User Info
        self.user_info_frame = QFrame()
        self.user_info_frame.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px;
            }
        """)

        user_info_layout = QVBoxLayout()
        user_info_layout.setSpacing(5)

        self.user_name_label = QLabel("Not Logged In")
        self.user_name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        user_info_layout.addWidget(self.user_name_label)

        self.user_role_label = QLabel("")
        self.user_role_label.setFont(QFont("Arial", 9))
        self.user_role_label.setStyleSheet("color: #757575;")
        user_info_layout.addWidget(self.user_role_label)

        self.user_info_frame.setLayout(user_info_layout)
        sidebar_layout.addWidget(self.user_info_frame)

        # Logout Button
        self.logout_btn = NavigationButton("Logout", "🚪")
        self.logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(self.logout_btn)

        self.sidebar.setLayout(sidebar_layout)

    def create_content_area(self):
        """Create main content area"""
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: #FFFFFF;
            }
        """)

        # Initialize all pages (will be populated after login)
        self.pages = {}

    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu("View")

        # Theme Submenu
        theme_menu = view_menu.addMenu("Theme")

        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(lambda: self.apply_theme('light'))
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(lambda: self.apply_theme('dark'))
        theme_menu.addAction(dark_theme_action)

        # Tools Menu
        tools_menu = menubar.addMenu("Tools")

        refresh_action = QAction("Refresh Data", self)
        refresh_action.triggered.connect(self.refresh_current_page)
        tools_menu.addAction(refresh_action)

        tools_menu.addSeparator()

        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        tools_menu.addAction(backup_action)

        # Help Menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        user_guide_action = QAction("User Guide", self)
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)

    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status bar widgets
        self.connection_status = QLabel("● Database: Connected")
        self.connection_status.setStyleSheet("color: #4CAF50;")
        self.status_bar.addWidget(self.connection_status)

        self.status_bar.addPermanentWidget(QLabel("|"))

        self.current_time = QLabel(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.status_bar.addPermanentWidget(self.current_time)

        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

    def show_login(self):
        """Show login dialog"""
        login = LoginDialog(self)
        login.login_successful.connect(self.on_login_successful)

        if login.exec() != QDialog.DialogCode.Accepted:
            self.close()
            return False

        return True

    def on_login_successful(self, user_data):
        """Handle successful login"""
        self.user_data = user_data
        self.setup_pages()
        self.update_user_info()
        self.switch_page(0)  # Go to dashboard
        self.start_session_timer()

        # Welcome message
        QMessageBox.information(self, "Welcome",
                              f"Welcome to Water Pump Management System, {user_data['name']}!")

    def setup_pages(self):
        """Initialize all application pages"""
        # Clear existing pages
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if widget:
                widget.deleteLater()

        self.pages = {}

        # Dashboard
        self.dashboard = DashboardWidget(self.user_data)
        self.dashboard.shutdown_requested.connect(self.handle_pump_shutdown)
        self.content_area.addWidget(self.dashboard)
        self.pages['dashboard'] = self.dashboard

        # Pump Management
        self.pump_mgmt = PumpManagementWidget(self.user_data)
        self.pump_mgmt.pump_updated.connect(self.on_data_updated)
        self.content_area.addWidget(self.pump_mgmt)
        self.pages['pump_mgmt'] = self.pump_mgmt

        # Maintenance
        self.maintenance = MaintenanceWidget(self.user_data)
        self.maintenance.maintenance_updated.connect(self.on_data_updated)
        self.content_area.addWidget(self.maintenance)
        self.pages['maintenance'] = self.maintenance

        # Inventory
        self.inventory = InventoryWidget(self.user_data)
        self.inventory.inventory_updated.connect(self.on_data_updated)
        self.content_area.addWidget(self.inventory)
        self.pages['inventory'] = self.inventory

        # Reports
        self.reports = ReportsWidget(self.user_data)
        self.content_area.addWidget(self.reports)
        self.pages['reports'] = self.reports

        # Logs
        self.logs = LogsWidget(self.user_data)
        self.content_area.addWidget(self.logs)
        self.pages['logs'] = self.logs

        # Settings
        self.settings = SettingsWidget(self.user_data)
        self.settings.settings_changed.connect(self.on_data_updated)
        self.settings.theme_changed.connect(self.apply_theme)
        self.content_area.addWidget(self.settings)
        self.pages['settings'] = self.settings

    def update_user_info(self):
        """Update user information in sidebar"""
        if self.user_data:
            self.user_name_label.setText(self.user_data['name'])
            self.user_role_label.setText(f"{self.user_data.get('job_type', 'Technician')}"
                                       f" • {self.user_data.get('department', 'Operations')}")

    def switch_page(self, index):
        """Switch to different page"""
        self.content_area.setCurrentIndex(index)

        # Update navigation button states
        for i, (text, btn) in enumerate(self.nav_buttons.items()):
            btn.setChecked(i == index)

        # Update status bar
        page_names = [
            "Dashboard", "Pump Management", "Maintenance",
            "Inventory", "Reports", "System Logs", "Settings"
        ]
        if index < len(page_names):
            self.status_bar.showMessage(f"Switched to {page_names[index]}", 2000)

    def handle_pump_shutdown(self, pump_id):
        """Handle pump shutdown signal"""
        if pump_id == -1:  # Emergency shutdown
            self.status_bar.showMessage("⚠️ Emergency shutdown activated!", 5000)
        else:
            self.status_bar.showMessage(f"Pump {pump_id} has been shut down", 3000)

        # Refresh dashboard
        if hasattr(self, 'dashboard'):
            self.dashboard.refresh_data()

    def on_data_updated(self):
        """Handle data updates from various widgets"""
        # Refresh dashboard to show updated information
        if hasattr(self, 'dashboard'):
            self.dashboard.refresh_data()

    def refresh_current_page(self):
        """Refresh current page data"""
        current_index = self.content_area.currentIndex()
        page_names = ['dashboard', 'pump_mgmt', 'maintenance', 'inventory', 'reports', 'logs', 'settings']

        if current_index < len(page_names):
            page_name = page_names[current_index]
            if page_name in self.pages and hasattr(self.pages[page_name], 'load_data'):
                self.pages[page_name].load_data()
                self.status_bar.showMessage(f"Refreshed {page_names[current_index].replace('_', ' ').title()}", 2000)

    def apply_theme(self, theme_name):
        """Apply theme to application"""
        self.current_theme = theme_name
        theme = THEMES.get(theme_name, THEMES['light'])

        # Apply theme to main window
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(theme['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme['text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme['surface']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme['surface']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(theme['background']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(theme['text']))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme['surface']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme['text']))
        palette.setColor(QPalette.ColorRole.Link, QColor(theme['primary']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme['primary']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))

        self.setPalette(palette)

        # Update sidebar theme
        sidebar_style = f"""
            QFrame {{
                background-color: {theme['surface']};
                border-right: 2px solid {theme['primary']};
            }}
        """
        self.sidebar.setStyleSheet(sidebar_style)

        # Update status bar theme
        status_style = f"""
            QStatusBar {{
                background-color: {theme['surface']};
                color: {theme['text']};
                border-top: 1px solid {theme['primary']};
            }}
        """
        self.status_bar.setStyleSheet(status_style)

        self.status_bar.showMessage(f"Applied {theme_name.title()} theme", 2000)

    def start_session_timer(self):
        """Start session timeout timer"""
        self.session_timer.timeout.connect(self.check_session_timeout)
        self.session_timer.start(60000)  # Check every minute

        # Track user activity
        self.installEventFilter(self)

    def check_session_timeout(self):
        """Check if session has timed out"""
        if (datetime.now() - self.last_activity).total_seconds() > 1800:  # 30 minutes
            self.logout()
            QMessageBox.warning(self, "Session Timeout", "Your session has expired due to inactivity.")

    def eventFilter(self, obj, event):
        """Track user activity"""
        if event.type() in [event.Type.MouseButtonPress, event.Type.KeyPress]:
            self.last_activity = datetime.now()
        return super().eventFilter(obj, event)

    def update_time(self):
        """Update status bar time"""
        self.current_time.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def logout(self):
        """Handle logout"""
        reply = QMessageBox.question(self, "Confirm Logout",
                                   "Are you sure you want to logout?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if db.connect():
                    # Log logout action
                    log_query = """
                        INSERT INTO system_logs (user_id, action, details, severity)
                        VALUES (%s, %s, %s, %s)
                    """
                    db.execute_update(log_query,
                                    (self.user_data['id'], 'logout',
                                     f"User logged out: {self.user_data['name']}", 'info'))
                    db.close()
            except Exception as e:
                print(f"Failed to log logout: {e}")

            # Reset user data
            self.user_data = None
            self.user_name_label.setText("Not Logged In")
            self.user_role_label.setText("")

            # Clear pages
            self.content_area.clear()
            self.pages = {}

            # Show login again
            self.show_login()

    def backup_database(self):
        """Backup database"""
        QMessageBox.information(self, "Backup", "Database backup functionality would be implemented with database administration tools.")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Water Pump Management System</h2>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Description:</strong></p>
        <p>A comprehensive desktop application for monitoring and managing water pump systems, 
        maintenance schedules, inventory, and generating reports.</p>
        <p><strong>Features:</strong></p>
        <ul>
            <li>Real-time pump monitoring</li>
            <li>Maintenance scheduling and tracking</li>
            <li>Inventory management with alerts</li>
            <li>Comprehensive reporting system</li>
            <li>User management and security</li>
            <li>System logging and auditing</li>
        </ul>
        <p><strong>Technology:</strong> Python, PySide6, MySQL</p>
        """

        QMessageBox.about(self, "About Water Pump Management System", about_text)

    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
        <h2>User Guide</h2>
        
        <h3>Getting Started</h3>
        <p>1. Login with your job ID and password</p>
        <p>2. Use the navigation sidebar to access different sections</p>
        
        <h3>Dashboard</h3>
        <p>Monitor real-time pump status and view maintenance calendar</p>
        
        <h3>Pump Management</h3>
        <p>Add, edit, and monitor water pumps</p>
        
        <h3>Maintenance</h3>
        <p>Schedule and track maintenance activities</p>
        
        <h3>Inventory</h3>
        <p>Manage spare parts and receive low stock alerts</p>
        
        <h3>Reports</h3>
        <p>Generate and export various system reports</p>
        
        <h3>Settings</h3>
        <p>Customize application appearance and behavior</p>
        """

        QMessageBox.information(self, "User Guide", guide_text)

    def closeEvent(self, event):
        """Handle application close event"""
        if self.user_data:
            reply = QMessageBox.question(self, "Confirm Exit",
                                       "Are you sure you want to exit the application?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No)

            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

            # Log application exit
            try:
                if db.connect():
                    log_query = """
                        INSERT INTO system_logs (user_id, action, details, severity)
                        VALUES (%s, %s, %s, %s)
                    """
                    db.execute_update(log_query,
                                    (self.user_data['id'], 'application_exit',
                                     "User exited the application", 'info'))
                    db.close()
            except Exception as e:
                print(f"Failed to log application exit: {e}")

        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle('Fusion')

    # Initialize database
    db.init_database()

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())