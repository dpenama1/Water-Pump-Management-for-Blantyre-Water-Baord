import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QFrame, QPushButton, QCalendarWidget,
                               QTextEdit, QScrollArea, QGroupBox, QProgressBar,
                               QTableWidget, QTableWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QDate, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QIcon
from datetime import datetime
import random
from database import db

# --- IMPORTS FOR HARDWARE & EMAIL ---
from arduino_communication import arduino
from email_manager import email_notifier


# ------------------------------------

class PumpStatusCard(QFrame):
    def __init__(self, pump_data, parent=None):
        super().__init__(parent)
        self.pump_data = pump_data
        self.setFrameStyle(QFrame.Shape.Box)

        # Stylesheet logic
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px solid #E0E0E0;
                border-radius: 12px;
                padding: 15px;
            }
            QFrame[status="online"] {
                border-color: #4CAF50;
                background-color: #E8F5E8;
            }
            QFrame[status="offline"] {
                border-color: #F44336;
                background-color: #FFEBEE;
            }
            QFrame[status="maintenance"] {
                border-color: #FF9800;
                background-color: #FFF3E0;
            }
        """)

        # Set status property for styling
        self.setProperty("status", pump_data.get('status', 'offline'))
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # --- HEADER ---
        header_layout = QHBoxLayout()

        # Pump Name
        p_name = self.pump_data.get('pump_name') or f"Pump #{self.pump_data.get('pump_id', '?')}"
        pump_name = QLabel(p_name)
        pump_name.setFont(QFont("Arial", 14, QFont.Weight.Bold))

        # Status Label
        status_text = self.pump_data.get('status', 'Unknown').upper()
        status_label = QLabel(status_text)
        status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        status_colors = {
            'online': '#4CAF50',
            'offline': '#F44336',
            'maintenance': '#FF9800'
        }
        status_label.setStyleSheet(f"color: {status_colors.get(self.pump_data.get('status', 'offline'), '#757575')}")

        header_layout.addWidget(pump_name)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)

        # Location
        location = QLabel(f"📍 {self.pump_data.get('location', 'Main Station')}")
        location.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(location)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #E0E0E0;")
        layout.addWidget(divider)

        # --- METRICS (Simplified) ---
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)

        # Flow Rate (Now at 0,0)
        flow_label = QLabel("Flow Rate:")
        f_val = self.pump_data.get('flow_rate')
        flow_text = f"{float(f_val):.1f} GPM" if f_val is not None else "0.0 GPM"
        flow_value = QLabel(flow_text)
        flow_value.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # Slightly larger

        # Operating Hours (Now at 0,2)
        hours_label = QLabel("Op. Hours:")
        h_val = self.pump_data.get('operating_hours')
        hours_text = f"{float(h_val):.1f} hrs" if h_val is not None else "0.0 hrs"
        hours_value = QLabel(hours_text)
        hours_value.setFont(QFont("Arial", 12, QFont.Weight.Bold))  # Slightly larger

        # Add to Grid
        metrics_layout.addWidget(flow_label, 0, 0)
        metrics_layout.addWidget(flow_value, 0, 1)
        metrics_layout.addWidget(hours_label, 0, 2)
        metrics_layout.addWidget(hours_value, 0, 3)

        layout.addLayout(metrics_layout)

        # --- PROGRESS BAR ---
        if self.pump_data.get('status') == 'online':
            progress = QProgressBar()
            progress.setRange(0, 25)
            # Simple efficiency calculation based on flow (assuming 100 GPM is max)
            current_flow = float(self.pump_data.get('flow_rate', 0.0))
            efficiency = min(int(current_flow), 25)

            progress.setValue(efficiency)
            progress.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #E0E0E0;
                    border-radius: 4px;
                    text-align: center;
                    height: 15px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
            layout.addWidget(progress)

        # Last updated footer
        last_updated = QLabel(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        last_updated.setStyleSheet("color: #757575; font-size: 10px;")
        last_updated.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(last_updated)

        self.setLayout(layout)


class DashboardWidget(QWidget):
    shutdown_requested = Signal(int)

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.pumps = []
        self.notifications = []

        # Initialize Arduino
        if not arduino.is_connected:
            arduino.connect()
            # Force wake up
            if arduino.is_connected:
                arduino.send_command("PING")

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)

        self.setup_ui()
        self.load_data()
        self.refresh_timer.start(2000)  # Refresh every 2 seconds

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Left Panel - Pump Status
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        header_label = QLabel("Pump Status Monitor")
        header_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #1976D2;")
        left_panel.addWidget(header_label)

        self.pump_container = QVBoxLayout()
        self.pump_container.setSpacing(10)

        pumps_scroll = QScrollArea()
        pumps_scroll.setWidgetResizable(True)
        pumps_scroll.setStyleSheet(
            "QScrollArea { border: 1px solid #E0E0E0; border-radius: 8px; background-color: #FAFAFA; }")

        pumps_widget = QWidget()
        pumps_widget.setLayout(self.pump_container)
        pumps_scroll.setWidget(pumps_widget)
        left_panel.addWidget(pumps_scroll)

        # Control Buttons
        control_layout = QHBoxLayout()

        # Added Start Button for convenience
        self.start_btn = QPushButton("▶ Start Pump")
        self.start_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold;")
        self.start_btn.clicked.connect(self.start_pump)

        self.shutdown_btn = QPushButton("🛑 Emergency Shutdown")
        self.shutdown_btn.setStyleSheet(
            "background-color: #F44336; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold;")
        self.shutdown_btn.clicked.connect(self.emergency_shutdown)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.shutdown_btn)
        control_layout.addStretch()
        left_panel.addLayout(control_layout)

        # Right Panel (Notifications & Logs)
        right_panel = QVBoxLayout()
        notifications_group = QGroupBox("System Notifications")
        notif_layout = QVBoxLayout()
        self.notifications_text = QTextEdit()
        self.notifications_text.setReadOnly(True)
        notif_layout.addWidget(self.notifications_text)
        notifications_group.setLayout(notif_layout)
        right_panel.addWidget(notifications_group)

        main_layout.addWidget(QWidget(), 0)  # Spacer
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

        self.setLayout(main_layout)

    def load_data(self):
        # Get real data from Arduino
        real_readings = arduino.get_last_readings(1)

        # Create a "Complete" data object so the Card doesn't look empty
        # We merge defaults with real data
        pump_data = {
            'pump_id': 1,
            'pump_name': 'Primary Pump Station',
            'location': 'Sector 7 - Intake',
            'status': real_readings.get('status', 'offline'),
            'flow_rate': real_readings.get('flow_rate', 0.0),
            'pressure': real_readings.get('pressure', 0.0),
            'temperature': real_readings.get('temperature', 72.5),  # Default/Simulated
            'operating_hours': 1240.5  # Default/Simulated
        }

        self.pumps = [pump_data]
        self.update_pump_display()

    def update_pump_display(self):
        while self.pump_container.count():
            child = self.pump_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for pump in self.pumps:
            card = PumpStatusCard(pump)
            self.pump_container.addWidget(card)

    def start_pump(self):
        if arduino.is_connected:
            arduino.control_pump(1, 'ON')
            self.notifications_text.append(f"[{datetime.now().strftime('%H:%M')}] Start command sent.")
        else:
            QMessageBox.warning(self, "Error", "Arduino not connected")

    def emergency_shutdown(self):
        reply = QMessageBox.question(self, "Emergency", "Shutdown all pumps and notify supervisors?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Hardware
            if arduino.is_connected:
                arduino.shutdown_all_pumps()
                self.notifications_text.append("🛑 HARDWARE STOPPED")

            # Database
            try:
                if db.connect():
                    db.execute_update("UPDATE water_pumps SET status = 'offline'")
                    db.close()
            except:
                pass

            # Email
            email_notifier.send_shutdown_alert(self.user_data['name'])
            self.notifications_text.append("📧 Emails sent to supervisors")

            QMessageBox.information(self, "Shutdown", "System Shutdown Complete")

    def refresh_data(self):
        self.load_data()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DashboardWidget({'id': 1, 'name': 'Admin', 'job_id': '001'})
    window.show()
    sys.exit(app.exec())