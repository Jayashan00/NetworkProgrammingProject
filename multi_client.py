import socket
import json
import threading
import sys

# IMPORTANT: Change 'localhost' to the server's IP if running on a different machine
SERVER_IP = 'localhost'
SERVER_PORT = 5050

def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if not msg:
                break
            reply = json.loads(msg.strip())
            print(f"\n[SERVER ACK]: {reply.get('server_msg')}")
            print("\nSelect Device: [1] AC Unit  [2] Main Server  [3] Exhaust Fan")
            print("Choice (1-3) or 'q' to quit: ", end="")
            sys.stdout.flush()
        except:
            break

def start_multi_interactive():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
        print(f"[CONNECTED] Master Control Node online.")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    # Threading requirement
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    devices = {
        "1": "Smart_AC_Unit",
        "2": "Main_DB_Server",
        "3": "Exhaust_Fan_RPM"
    }

    while True:
        print("\nSelect Device: [1] AC Unit  [2] Main Server  [3] Exhaust Fan")
        dev_choice = input("Choice (1-3) or 'q' to quit: ")

        if dev_choice.lower() == 'q':
            break

        if dev_choice not in devices:
            print("Invalid choice. Try again.")
            continue

        device_name = devices[dev_choice]
        val = input(f"Enter payload for {device_name} (e.g., '22C', '9000 RPM'): ")

        is_crit = input("Is this a critical alert? (y/n): ").lower()
        status = "CRITICAL" if is_crit == 'y' else "OK"

        data = {
            "device_name": device_name,
            "status": status,
            "value": val
        }

        try:
            client.send((json.dumps(data) + "\n").encode('utf-8'))
        except:
            print("Connection lost.")
            break

    client.close()

if __name__ == "__main__":
    start_multi_interactive()