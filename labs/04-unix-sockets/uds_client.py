# client.py
import socket
import time

SOCK = "/run/ipc_test/demo.sock"



while True:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK)
    s.sendall(b"{\"client_id\":\"Client_1\"}")
    print(s.recv(4096))
    s.close()
    time.sleep(5)

