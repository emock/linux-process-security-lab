import socket

# HOST = "0.0.0.0"
# PORT = 5000
#
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
#     s.bind((HOST, PORT))
#
#     while True:
#         data, addr = s.recvfrom(1024)
#         print(addr, data)

    sock.bind(("0.0.0.0", 5000))

    while True:
        data, addr = sock.recvfrom(1024)
        print(addr, data)