import subprocess
import re
import xml.etree.ElementTree as ET

def check_connected_devices():
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        output = result.stdout
        devices = []
        for line in output.splitlines():
            if '\tdevice' in line:
                serial = line.split('\t')[0]
                devices.append(serial)
        return devices
    except FileNotFoundError:
        print("ADB not found. Ensure Android Debug Bridge is installed.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def get_device_info(serial):
    """Extract device info, IMEI, IMSI, and messages using adb shell commands."""
    info = {}
    try:
        # Get general device info
        result = subprocess.run(['adb', '-s', serial, 'shell', 'getprop'], capture_output=True, text=True)
        info['getprop'] = result.stdout

        # Try to get IMEI
        result_imei = subprocess.run(['adb', '-s', serial, 'shell', 'service', 'call', 'iphonesubinfo', '1'], capture_output=True, text=True)
        imei_match = re.findall(r"\'(.*?)\'", result_imei.stdout.replace('.', '').replace(' ', ''))
        imei = ''.join(imei_match)
        info['IMEI'] = imei if imei else "Not available"

        # Try to get IMSI
        result_imsi = subprocess.run(['adb', '-s', serial, 'shell', 'service', 'call', 'iphonesubinfo', '7'], capture_output=True, text=True)
        imsi_match = re.findall(r"\'(.*?)\'", result_imsi.stdout.replace('.', '').replace(' ', ''))
        imsi = ''.join(imsi_match)
        info['IMSI'] = imsi if imsi else "Not available"

        # Try to get 10 SMS messages
        result_sms = subprocess.run(['adb', '-s', serial, 'shell', 'content', 'query', '--uri', 'content://sms/inbox', '--projection', 'address,date,body', '--limit', '10'], capture_output=True, text=True)
        messages = []
        if result_sms.stdout:
            lines = result_sms.stdout.splitlines()
            for line in lines:
                if line.strip():
                    parts = line.split(',')
                    msg = {}
                    for part in parts:
                        if 'address=' in part:
                            msg['sender'] = part.split('=')[1].strip()
                        elif 'date=' in part:
                            msg['date'] = part.split('=')[1].strip()
                        elif 'body=' in part:
                            msg['body'] = part.split('body=')[1].strip()
                    if msg:
                        messages.append(msg)
        info['messages'] = messages if messages else "No messages retrieved"

    except Exception as e:
        info['error'] = str(e)
    return info

def main():
    devices = check_connected_devices()
    if devices:
        print("Connected mobile devices:")
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device}")
            info = get_device_info(device)
            print("Device Info (getprop):")
            print(info.get('getprop', 'N/A'))
            print(f"IMEI: {info.get('IMEI', 'N/A')}")
            print(f"IMSI: {info.get('IMSI', 'N/A')}")
            print("Messages (up to 10):")
            if isinstance(info.get('messages'), list):
                for msg in info['messages']:
                    print(f"Sender: {msg.get('sender', 'N/A')}")
                    print(f"Date: {msg.get('date', 'N/A')}")
                    print(f"Body: {msg.get('body', 'N/A')}")
                    print("-" * 20)
            else:
                print(info.get('messages', 'N/A'))
            if 'error' in info:
                print(f"Error: {info['error']}")
            print("-" * 40)
    else:
        print("No mobile devices connected.")

if __name__ == "__main__":
    main()