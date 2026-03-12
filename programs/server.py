import socket
import threading

HOST = "0.0.0.0"
PORT = 9000


def handle_client(conn, addr):
    print(f"Connected: {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                print(f"Disconnected: {addr}")
                break
            print(f"Received from {addr}: {data!r}")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()