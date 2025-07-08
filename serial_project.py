import serial
import serial.tools.list_ports
import time
import re

def get_device_ids(port_name):
    """Try to get IMSI and IMEI using AT commands."""
    ids = {'IMSI': None, 'IMEI': None}
    try:
        ser = serial.Serial(port_name, baudrate=9600, timeout=2)
        time.sleep(0.5)
        # Get IMEI
        ser.write(b'AT+CGSN\r')
        time.sleep(0.5)
        imei_resp = ser.read_all().decode(errors='ignore')
        imei_match = re.search(r'(\d{14,17})', imei_resp)
        if imei_match:
            ids['IMEI'] = imei_match.group(1)
        ser.reset_input_buffer()
        # Get IMSI
        ser.write(b'AT+CIMI\r')
        time.sleep(0.5)
        imsi_resp = ser.read_all().decode(errors='ignore')
        imsi_match = re.search(r'(\d{14,16})', imsi_resp)
        if imsi_match:
            ids['IMSI'] = imsi_match.group(1)
        ser.close()
    except Exception:
        pass
    return ids

def get_serial_devices():
    ports = serial.tools.list_ports.comports()
    devices = []
    for port in ports:
        ids = get_device_ids(port.device)
        device_info = {
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'vid': port.vid,
            'pid': port.pid,
            'serial_number': port.serial_number,
            'manufacturer': port.manufacturer,
            'product': port.product,
            'interface': port.interface,
            'IMEI': ids['IMEI'],
            'IMSI': ids['IMSI']
        }
        devices.append(device_info)
    return devices

def try_at_commands(port_name):
    try:
        ser = serial.Serial(port_name, baudrate=9600, timeout=2)
        time.sleep(0.5)
        ser.write(b'AT\r')
        time.sleep(0.5)
        response = ser.read_all().decode(errors='ignore')
        ser.close()
        return response.strip()
    except Exception as e:
        return f"Error: {e}"

def main():
    devices = get_serial_devices()
    if not devices:
        print("No serial devices found.")
        return

    for dev in devices:
        # Only show devices with both IMEI and IMSI present
        if dev['IMEI'] and dev['IMSI']:
            print(f"Device: {dev['device']}")
            print(f"  Description: {dev['description']}")
            print(f"  HWID: {dev['hwid']}")
            print(f"  VID: {dev['vid']}")
            print(f"  PID: {dev['pid']}")
            print(f"  Serial Number: {dev['serial_number']}")
            print(f"  Manufacturer: {dev['manufacturer']}")
            print(f"  Product: {dev['product']}")
            print(f"  Interface: {dev['interface']}")
            print(f"  IMEI: {dev['IMEI']}")
            print(f"  IMSI: {dev['IMSI']}")
            print("  Trying AT command...")
            at_response = try_at_commands(dev['device'])
            print(f"  AT Response: {at_response}")
            print("-" * 40)

if __name__ == "__main__":
    main()