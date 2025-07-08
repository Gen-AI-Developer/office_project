import serial
import time
import os

def reset_usb_device(port_name):
    """
    Try to reset the USB device using sysfs (Linux only).
    """
    # Find the USB bus and device numbers from /dev/serial/by-id or /sys/class/tty
    try:
        # Get the sysfs path for the device
        tty_path = os.path.realpath(f"/sys/class/tty/{os.path.basename(port_name)}/device")
        usb_path = tty_path
        # Go up until we find a usb device directory
        while usb_path and not os.path.basename(usb_path).startswith("usb"):
            usb_path = os.path.dirname(usb_path)
        if usb_path and os.path.exists(os.path.join(usb_path, "authorized")):
            # Unauthorize and re-authorize the device
            with open(os.path.join(usb_path, "authorized"), "w") as f:
                f.write("0")
            time.sleep(1)
            with open(os.path.join(usb_path, "authorized"), "w") as f:
                f.write("1")
            print(f"Reset USB device at {usb_path}")
            return True
    except Exception as e:
        print(f"Could not reset device: {e}")
    return False

def is_device_active(port_name, timeout=2):
    """
    Check if the serial device is active and responsive to AT commands.
    Returns True if responsive, False otherwise.
    """
    try:
        ser = serial.Serial(port_name, baudrate=9600, timeout=timeout)
        time.sleep(0.5)
        ser.write(b'AT\r')
        time.sleep(0.5)
        response = ser.read_all().decode(errors='ignore')
        ser.close()
        return 'OK' in response
    except Exception:
        return False

def ensure_device_active(port_name, retries=3, delay=2):
    """
    Try to make the device available by pinging and resetting if needed.
    """
    for attempt in range(retries):
        if is_device_active(port_name):
            print(f"{port_name} is active and responding.")
            return True
        print(f"{port_name} not responding. Attempt {attempt+1}/{retries}. Trying to reset...")
        reset_usb_device(port_name)
        time.sleep(delay)
    print(f"{port_name} could not be activated after {retries} attempts.")
    return False

if __name__ == "__main__":
    port = "/dev/ttyUSB0"
    while True:
        ensure_device_active(port)
        time.sleep(3)