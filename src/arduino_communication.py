import serial
import serial.tools.list_ports
import threading
import time
import json
import logging
from datetime import datetime
from config import ARDUINO_CONFIG  # Ensure you have this file or replace with dict


class ArduinoCommunication:
    def __init__(self):
        self.serial_connection = False
        self.is_connected = False
        self.running = False
        self.logger = logging.getLogger(__name__)
        # Store latest data here
        self.last_readings = {
            'pump1': {'pump_id': 1, 'status': 'offline', 'flow_rate': 0.0, 'pressure': 0.0}
        }

    def find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Look for common Arduino names
            if any(x in port.description.lower() for x in ['arduino', 'ch340', 'ftdi', 'usb serial']):
                return port.device
        return 'COM8'  # Windows Default (Change to /dev/ttyUSB0 for Linux/Mac)

    def connect(self):
        try:
            port = self.find_arduino_port()
            print(f"Connecting to {port}...")
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino reset

            self.is_connected = True
            self.running = True

            # Start background reader
            self.read_thread = threading.Thread(target=self.read_from_arduino, daemon=True)
            self.read_thread.start()

            print("✅ Arduino Connected!")
            return True
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        self.running = False
        self.is_connected = False
        if self.serial_connection:
            self.serial_connection.close()

    def read_from_arduino(self):
        """Modified to print all incoming data for debugging"""
        while self.running and self.is_connected:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Read the raw line
                    raw_line = self.serial_connection.readline()

                    # Decode and clean it
                    line = raw_line.decode('utf-8', errors='ignore').strip()

                    # PRINT EVERYTHING RECEIVED (This is the debug line)
                    print(f"DEBUG RX: {line}")

                    if line.startswith('{') and line.endswith('}'):
                        try:
                            data = json.loads(line)
                            self.process_data(data)
                            print(" -> JSON Valid: Data Updated")
                        except json.JSONDecodeError:
                            print(" -> JSON Error: Could not parse")

            except Exception as e:
                print(f"Read Error: {e}")
                self.is_connected = False
                break

    def process_data(self, data):
        # Update local cache
        p_id = data.get('pump_id', 1)
        self.last_readings[f'pump{p_id}'] = data

        # Optional: Here you would insert into Database (db.execute_update...)

    def control_pump(self, pump_id, action):
        """ action: 'ON' or 'OFF' """
        cmd = f"PUMP{pump_id}:{action}"
        self.send_command(cmd)

    def shutdown_all_pumps(self):
        """Urgent stop for all pumps"""
        self.send_command("PUMP1:OFF")
        self.send_command("PUMP2:OFF")

    def send_command(self, command):
        if self.is_connected:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                print(f"Sent: {command}")
            except Exception as e:
                print(f"Write Error: {e}")

    def get_last_readings(self, pump_id):
        return self.last_readings.get(f'pump{pump_id}', {})


# Global instance
arduino = ArduinoCommunication()