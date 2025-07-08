import gammu
import serial.tools.list_ports

def list_serial_ports():
    """List all available serial ports (likely to be phones/modems)."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def is_mobile_device(port):
    """
    Try to detect if a mobile device is connected to the port by sending an AT command.
    Returns True if the device responds with 'OK', False otherwise.
    """
    import serial
    try:
        ser = serial.Serial(port, baudrate=9600, timeout=2)
        ser.write(b'AT\r')
        response = ser.read(64).decode(errors='ignore')
        ser.close()
        return 'OK' in response
    except Exception:
        return False

def extract_sms_from_port(port):
    """Try to extract all SMS from a given port using gammu."""
    try:
        sm = gammu.StateMachine()
        # Dynamically set config for this port
        sm.SetConfig(0, {
            'Device': port,
            'Connection': 'at',
        })
        sm.Init()
        sms_list = []
        for folder in [0, 10]:  # 0: Inbox, 10: Outbox
            start = True
            while True:
                try:
                    sms = sm.GetNextSMS(Folder=folder, Start=start)
                    sms_list.extend(sms)
                    start = False
                except gammu.ERR_EMPTY:
                    break
                except gammu.GSMError:
                    break
        return sms_list
    except Exception as e:
        print(f"Could not extract SMS from {port}: {e}")
        return []

def main():
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
        return

    # Detect mobile devices
    mobile_ports = []
    for port in ports:
        print(f"Checking port {port} for mobile device...")
        if is_mobile_device(port):
            print(f"Mobile device detected on {port}.")
            mobile_ports.append(port)
        else:
            print(f"No mobile device detected on {port}.")

    if not mobile_ports:
        print("No mobile devices detected on any port.")
        return

    for port in mobile_ports:
        print(f"\nExtracting SMS from device: {port}")
        sms_list = extract_sms_from_port(port)
        if sms_list:
            for sms in sms_list:
                print(f"Number: {sms.get('Number', '')}")
                print(f"Text: {sms.get('Text', '')}")
                print(f"Date: {sms.get('DateTime', '')}")
                print("-" * 40)
        else:
            print("No SMS found or unable to read from this device.")

if __name__ == "__main__":
    main()