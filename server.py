import socket
import threading
import json

# --- CONFIGURATION ---
SERVER_IP = '0.0.0.0'  # Listens on all available network interfaces
SERVER_PORT = 5050
HEADER = 1024

def handle_device(conn, addr):
    """
    This function runs in a separate THREAD for each device.
    It listens for data from that specific device.
    """
    print(f"[NEW CONNECTION] Device connected from {addr}")

    connected = True
    while connected:
        try:
            # Receive message
            msg = conn.recv(HEADER).decode('utf-8')
            if not msg:
                break

            # Parse JSON data
            data = json.loads(msg)

            # --- ALERT SYSTEM LOGIC ---
            device_name = data.get("device_name")
            status = data.get("status")
            value = data.get("value")

            # Check for critical status
            if status == "CRITICAL" or status == "ERROR":
                print(f"⚠️  [ALERT] {device_name} is reporting an ERROR! (Value: {value})")
            else:
                print(f"✅  [INFO] {device_name}: Status {status} | Value: {value}")

        except Exception as e:
            print(f"[ERROR] Connection lost with {addr}")
            connected = False

    conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()

    print(f"[STARTING] Smart Office Server is listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        # Wait for a new connection
        conn, addr = server.accept()

        # KEY REQUIREMENT: Create a new thread for the new device
        thread = threading.Thread(target=handle_device, args=(conn, addr))
        thread.start()

        # Print active threads (to prove multi-threading in the Viva)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()