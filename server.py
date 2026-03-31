import socket
import threading
import json
from flask import Flask, render_template
from flask_socketio import SocketIO

# --- Configuration ---
TCP_IP = '0.0.0.0'  # Accept connections from other machines
TCP_PORT = 5050
WEB_PORT = 5000
HEADER = 1024

# --- Web Server Setup ---
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

# --- TCP Socket Server ---
def handle_device(conn, addr):
    print(f"\n[NEW CONNECTION] Device connected from {addr[0]}:{addr[1]}")
    buffer = ""
    connected = True

    while connected:
        try:
            msg = conn.recv(HEADER).decode('utf-8')
            if not msg:
                break

            buffer += msg
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)

                if line.strip():
                    try:
                        data = json.loads(line)
                        device_name = data.get("device_name", "Unknown")
                        status = data.get("status", "OK")
                        value = data.get("value", "")

                        print(f"[{device_name}] sent payload: {value}")

                        # Push data to Web UI (Fix applied here: added namespace)
                        socketio.emit('new_packet', {
                            'device_name': device_name,
                            'status': status,
                            'value': value,
                            'raw_payload': line.strip(),
                            'address': f"{addr[0]}:{addr[1]}"
                        }, namespace='/')

                        # Reply to client
                        reply = {"server_msg": f"Server received '{value}' successfully!"}
                        conn.send((json.dumps(reply) + "\n").encode('utf-8'))

                    except json.JSONDecodeError:
                        print(f"[ERROR] Corrupted JSON from {addr}")

        except Exception as e:
            print(f"[ERROR] Connection lost with {addr}: {e}")
            connected = False

    conn.close()
    print(f"[DISCONNECTED] Device at {addr} disconnected.")


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((TCP_IP, TCP_PORT))
    server.listen()
    print(f"[STARTING] Raw TCP Server listening on Port {TCP_PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_device, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    # Run TCP server in background thread
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()

    # Run Flask-SocketIO server in main thread (Fix applied here: use_reloader=False)
    print(f"[STARTING] Web Dashboard running at http://localhost:{WEB_PORT}")
    socketio.run(app, host='0.0.0.0', port=WEB_PORT, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)