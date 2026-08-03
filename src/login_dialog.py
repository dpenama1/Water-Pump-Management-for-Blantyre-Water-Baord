import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap
from database import db
import hashlib


class LoginDialog(QDialog):
    login_successful = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Water Pump Management System - Login")
        # INCREASED HEIGHT to 600 to fit logo and fields comfortably
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.Dialog)

        # Apply modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212121;
                font-size: 14px;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #FAFAFA;
                color: #212121;
            }
            QLineEdit:focus {
                border-color: #1976D2;
                background-color: #FFFFFF;
            }
            QPushButton {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                border: none;
            }
            QPushButton#loginBtn {
                background-color: #1976D2;
                color: white;
            }
            QPushButton#loginBtn:hover {
                background-color: #1565C0;
            }
            QPushButton#loginBtn:pressed {
                background-color: #0D47A1;
            }
            QPushButton#exitBtn {
                background-color: #F5F5F5;
                color: #212121;
            }
            QPushButton#exitBtn:hover {
                background-color: #E0E0E0;
            }
        """)

        self.setup_ui()
        self.attempts = 0
        self.max_attempts = 3

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # Reduced main spacing
        # REDUCED MARGINS from 40 to 30 to give fields more room
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #1976D2; border-radius: 12px;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 20, 15, 20)

        # --- LOGO INSERTION START ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(base_dir, '..', 'resources', 'bwb_logo.png')

        logo_label = QLabel()
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Scale image slightly larger (80px) for better visibility
            scaled_pixmap = pixmap.scaledToWidth(80, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)
        # --- LOGO INSERTION END ---

        title_label = QLabel("Water Pump\nManagement System")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-top: 10px;")

        subtitle_label = QLabel("Technician Login")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #E3F2FD; font-size: 14px;")

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)

        # Login Form
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)  # Better spacing between inputs

        # Job ID
        job_id_label = QLabel("Job ID:")
        job_id_label.setStyleSheet("font-weight: bold;")
        self.job_id_input = QLineEdit()
        self.job_id_input.setPlaceholderText("Enter your job ID")
        self.job_id_input.setMaxLength(20)

        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMaxLength(50)

        form_layout.addWidget(job_id_label)
        form_layout.addWidget(self.job_id_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setObjectName("exitBtn")
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.exit_btn)

        layout.addLayout(button_layout)

        # Version info
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #757575; font-size: 12px;")
        layout.addWidget(version_label)

        self.setLayout(layout)

        # Set focus to job ID input
        self.job_id_input.setFocus()

        # Connect return key
        self.job_id_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self.handle_login)

    def hash_password(self, password):
        """Simple password hashing"""
        return hashlib.sha256(password.encode()).hexdigest()

    def handle_login(self):
        """Handle login authentication"""
        job_id = self.job_id_input.text().strip()
        password = self.password_input.text()

        if not job_id or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both job ID and password.")
            return

        if not db.connect():
            QMessageBox.critical(self, "Database Error", "Cannot connect to database. Please check your connection.")
            return

        try:
            # Query user from database
            query = "SELECT * FROM users WHERE job_id = %s AND is_active = TRUE"
            user_data = db.execute_query(query, (job_id,))

            if user_data and len(user_data) > 0:
                user = user_data[0]
                # For demo purposes, using plain text comparison
                # In production, use hashed passwords
                if user['password'] == password:  # Change to: self.hash_password(password)
                    # Update last login
                    update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
                    db.execute_update(update_query, (user['id'],))

                    # Log successful login
                    self.log_login_attempt(user['id'], 'success')

                    # Emit success signal
                    self.login_successful.emit(user)
                    self.accept()
                    return

            # Failed login
            self.attempts += 1
            remaining = self.max_attempts - self.attempts

            if self.attempts >= self.max_attempts:
                QMessageBox.critical(self, "Login Failed", "Maximum login attempts reached. System will close.")
                self.reject()
            else:
                QMessageBox.warning(self, "Login Failed",
                                    f"Invalid job ID or password. {remaining} attempts remaining.")
                self.password_input.clear()
                self.password_input.setFocus()

            # Log failed attempt
            self.log_login_attempt(None, 'failed', job_id)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during login: {str(e)}")
        finally:
            db.close()

    def log_login_attempt(self, user_id, status, job_id=None):
        """Log login attempts"""
        try:
            if db.connect():
                query = """
                        INSERT INTO system_logs (user_id, action, details, severity, ip_address)
                        VALUES (%s, %s, %s, %s, %s) \
                        """
                details = f"Login attempt from job ID: {job_id}" if job_id else "Login attempt"
                severity = 'info' if status == 'success' else 'warning'

                db.execute_update(query, (user_id, f'login_{status}', details, severity, 'localhost'))
                db.close()
        except Exception as e:
            print(f"Failed to log login attempt: {e}")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Initialize database
    db.init_database()

    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        print("Login successful!")
    else:
        print("Login cancelled.")

    sys.exit(app.exec())