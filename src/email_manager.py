import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import logging
from database import db  # Assumes your database.py is set up

# CONFIGURATION
# ⚠️ Replace with your actual email details.
# If using Gmail, you must generate an "App Password" in your Google Account security settings.
SMTP_CONFIG = {
    'server': 'smtp.gmail.com',
    'port': 587,
    'sender_email': 'dpenama1@gmail.com',
    'password': 'wfkl rgzz wlis rhnk'
}


class EmailManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_supervisors(self):
        """Fetch emails of all supervisors from database"""
        supervisors = []
        try:
            if db.connect():
                # Adjust 'role' or table name based on your actual database schema
                query = "SELECT email FROM users WHERE role = 'supervisor'"
                results = db.execute_query(query)
                supervisors = [row['email'] for row in results if row.get('email')]
                db.close()
        except Exception as e:
            self.logger.error(f"Failed to fetch supervisors: {e}")
            # Fallback for testing if DB fails
            return ['penamadennis@gmail.com']
        return supervisors

    def send_shutdown_alert(self, triggered_by_user):
        """Send email alert in a separate thread to avoid freezing UI"""
        thread = threading.Thread(target=self._send_email_thread, args=(triggered_by_user,))
        thread.start()

    def _send_email_thread(self, triggered_by_user):
        recipients = self.get_supervisors()

        if not recipients:
            self.logger.warning("No supervisors found to email.")
            return

        subject = "URGENT: Water Pump System Emergency Shutdown"
        body = f"""
        <html>
          <body>
            <h2 style="color: red;">🚨 Emergency Shutdown Alert</h2>
            <p>The water pump system has been manually shut down via the dashboard.</p>
            <ul>
                <li><strong>Triggered By:</strong> {triggered_by_user}</li>
                <li><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>Action:</strong> All pumps set to STOP / OFFLINE</li>
            </ul>
            <p>Please inspect the physical system immediately.</p>
          </body>
        </html>
        """

        try:
            msg = MIMEMultipart()
            msg['From'] = SMTP_CONFIG['sender_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(SMTP_CONFIG['server'], SMTP_CONFIG['port'])
            server.starttls()
            server.login(SMTP_CONFIG['sender_email'], SMTP_CONFIG['password'])

            # Send to all supervisors
            # Note: For privacy, you might want to send individually or use BCC
            server.sendmail(SMTP_CONFIG['sender_email'], recipients, msg.as_string())
            server.quit()

            self.logger.info(f"Shutdown alert sent to {len(recipients)} supervisors.")
            print("📧 Email alert sent successfully.")

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            print(f"❌ Email failed: {e}")


# Global instance
email_notifier = EmailManager()