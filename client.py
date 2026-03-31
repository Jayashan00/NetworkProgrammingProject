import socket
import json
import threading
import sys

# IMPORTANT: To communicate between two hosts, change 'localhost' to the Server's actual IP!
SERVER_IP = 'localhost'
SERVER_PORT = 5050
DEVICE_NAME = "Interactive_Terminal_1"

def receive_messages(client):
    """Threading Requirement: Listens for server replies while you type"""
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break

            # Parse server reply and print it above the input prompt
            reply = json.loads(msg.strip())
            print(f"\n[SERVER ACK]: {reply.get('server_msg')}")
            print("Enter value to send (or 'quit'): ", end="")
            sys.stdout.flush()
        except:
            print("\n[DISCONNECTED] Server closed the connection.")
            break

def start_interactive_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((SERVER_IP, SERVER_PORT))
        print(f"[CONNECTED] Connected to Server at {SERVER_IP}:{SERVER_PORT}")
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return

    # Start the background thread to listen for server replies
    recv_thread = threading.Thread(target=receive_messages, args=(client,), daemon=True)
    recv_thread.start()

    print("\n" + "="*40)
    print(f" DEVICE CONTROL: {DEVICE_NAME}")
    print("="*40)
    print("Type a value (e.g., '45C', 'System Overheat') to send it to the dashboard.")
    print("Tip: Include the word 'crit' or 'alert' in your message to trigger a red alert on the dashboard.\n")

    while True:
        # Chatbot-style input
        user_input = input("Enter value to send (or 'quit'): ")

        if user_input.lower() == 'quit':
            break

        # Determine status automatically based on what you typed
        if "crit" in user_input.lower() or "alert" in user_input.lower() or "high" in user_input.lower():
            status = "CRITICAL"
        else:
            status = "OK"

        data = {
            "device_name": DEVICE_NAME,
            "status": status,
            "value": user_input
        }

        json_data = json.dumps(data) + "\n"

        try:
            client.send(json_data.encode('utf-8'))
        except Exception as e:
            print(f"[DISCONNECTED] Lost connection: {e}")
            break

    client.close()

if __name__ == "__main__":
    start_interactive_client()