import serial
import serial.tools.list_ports
import time
import re
from datetime import datetime
import gammu

def scan_modems():
    modems = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.description or "Modem" in port.description:
            modems.append(port.device)
    return modems

def is_modem_port(port):
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        ser.write(b'AT\r')
        time.sleep(0.5)
        response = ser.read_all().decode('utf-8')
        ser.close()
        return 'OK' in response
    except (serial.SerialException, UnicodeDecodeError):
        return False

def extract_sms_pyserial(port):
    messages = []
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=1)
        ser.write(b'AT+CMGF=1\r')
        time.sleep(0.5)
        ser.write(b'AT+CMGL="ALL"\r')
        time.sleep(1)
        response = ser.read_all().decode('utf-8')
        ser.close()
        sms_lines = response.splitlines()
        for i, line in enumerate(sms_lines):
            if re.match(r'\+CMGL: \d+,".*",".*",".*",".*"', line):
                index = line.split(',')[0].split(':')[1].strip()
                status = line.split(',')[1].strip('"')
                number = line.split(',')[2].strip('"')
                date = line.split(',')[-2].strip('"')
                text = sms_lines[i + 1].strip()
                messages.append({
                    'index': index,
                    'status': status,
                    'number': number,
                    'date': date,
                    'text': text
                })
        return messages
    except (serial.SerialException, UnicodeDecodeError) as e:
        print(f"Error on {port}: {e}")
        return []

def extract_sms_gammu(port):
    messages = []
    try:
        sm = gammu.StateMachine()
        sm.SetConfig(0, {'Device': port, 'Connection': 'at'})
        sm.Init()
        sms = sm.GetSMS(0, 'SM')
        for msg in sms:
            messages.append({
                'index': msg['Number'],
                'status': msg['State'],
                'number': msg['Number'],
                'date': str(msg['DateTime']),
                'text': msg['Text']
            })
        sm.Terminate()
        return messages
    except gammu.GSMError as e:
        print(f"Gammu error on {port}: {e}")
        return []

def main():
    print("Scanning for modems...")
    modem_ports = scan_modems()
    if not modem_ports:
        print("No modems found.")
        return
    for port in modem_ports:
        if is_modem_port(port):
            print(f"Modem found on {port}. Extracting SMS...")
            messages = extract_sms_pyserial(port)
            if not messages:
                print(f"Trying Gammu on {port}...")
                messages = extract_sms_gammu(port)
            if messages:
                print(f"\nMessages from {port}:")
                for msg in messages:
                    print(f"Index: {msg['index']}, Status: {msg['status']}, "
                          f"Number: {msg['number']}, Date: {msg['date']}, "
                          f"Text: {msg['text']}")
            else:
                print(f"No messages found on {port}.")
        else:
            print(f"No modem on {port}.")

if __name__ == "__main__":
    main()