# extract_sms.py

import serial.tools.list_ports

def scan_modems():
    ports = serial.tools.list_ports.comports()
    # Try all ports, or add more keywords as needed
    return [port.device for port in ports]