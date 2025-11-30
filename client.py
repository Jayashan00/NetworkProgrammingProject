import socket
import time
import json
import random

# --- CONFIGURATION ---
# REPLACE THIS with the IP address of the computer running server.py
# If testing on ONE computer, use 'localhost'.
# If using TWO computers, find the Server's IP (e.g., '192.168.1.5')
SERVER_IP = 'localhost'
SERVER_PORT = 5050

# Device Configuration (Change these for different clients)
DEVICE_NAME = "Smart_AC_Unit_1"

def start_device():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_IP, SERVER_PORT))
        print(f"[CONNECTED] {DEVICE_NAME} connected to server.")
    except:
        print("[ERROR] Could not connect to server. Is it running?")
        return

    while True:
        # Simulate sensor data
        temp = random.randint(20, 35)

        # Simulate status logic
        status = "OK"
        if temp > 30:
            status = "CRITICAL" # This triggers the alert on the server

        # Create message packet
        data = {
            "device_name": DEVICE_NAME,
            "status": status,
            "value": f"{temp}°C"
        }

        # Send data
        json_data = json.dumps(data)
        client.send(json_data.encode('utf-8'))

        # Wait 2 seconds before sending next update (Real-time simulation)
        time.sleep(2)

if __name__ == "__main__":
    start_device()