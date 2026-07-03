# client.py
import socket
import time

SOCK = "/run/ipc_test/demo.sock"

# while True:


#  Clients using secure register function for registration
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(SOCK)
s.sendall(b"{\"method\":\"register\", \"endpoint\": \"endpoint1\"}")
print(s.recv(4096))
s.close()

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(SOCK)
s.sendall(b"{\"method\":\"send\", \"data\": \"testing\"}")
print(s.recv(4096))
s.close()


#  Clients using insecure uregister function for registration
# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# s.connect(SOCK)
# s.sendall(b"{\"method\":\"uregister\",\"name\": \"Client1\" ,\"endpoint\": \"endpoint1\"}")
# print(s.recv(4096))
# s.close()
#
# s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
# s.connect(SOCK)
# s.sendall(b"{\"method\":\"send\", \"data\": \"testing\"}")
# print(s.recv(4096))
# s.close()


