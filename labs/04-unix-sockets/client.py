# client.py
import socket
import time

SOCK = "/run/ipc_test/demo.sock"


def request(msg):

    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK)
    s.sendall(msg)
    print(s.recv(4096))
    s.close()


CMD="secure"

# --------------------------------------------------------
#  Clients using secure register function for registration
# --------------------------------------------------------
if CMD in "secure":
    request(b"{\"method\":\"register\", \"endpoint\": \"endpoint1\"}")
    request (b"{\"method\":\"send\", \"data\": \"testing\"}")

# --------------------------------------------------------
#  Clients using insecure uregister function for registration
# --------------------------------------------------------
else:
    request(b"{\"method\":\"uregister\",\"name\": \"Client1\" ,\"endpoint\": \"endpoint1\"}")
    request(b"{\"method\":\"usend\", \"data\": \"testing\"}")



