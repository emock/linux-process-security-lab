import os
import socket
import grp
import struct
import json
import pwd

SOCK = "/run/ipc_test/demo.sock"

try:
    os.unlink(SOCK)
except:
    pass

pid = os.getpid()
print(pid, flush=True)

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.bind(SOCK)

gid = grp.getgrnam("shared_group").gr_gid
os.chown(SOCK, os.getuid(), gid)
# For read and write on Sockets only write is needed
os.chmod(SOCK, 0o220)

s.listen(5)
print(f"Listening on {SOCK}")

clients = {}

while True:
    conn, _ = s.accept()

    # Linux SO_PEERCRED: pid, uid, gid des verbundenen Peers
    creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    pid, uid, gid = struct.unpack("3i", creds)
    
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name

    data = conn.recv(4096)
    request = json.loads(data.decode())




    if request["method"] == "uregister":

        clientid = request["name"]

        print(f"Registering Client {clientid}")



        if clientid in clients.keys():
            print(f"Client already registered")
            conn.sendall(b"Denied\n")
            conn.close()
            continue

        clients[clientid] = request["endpoint"]
        conn.sendall(b"ok\n")

    elif request["method"] == "register":
        print(f"Registering Client {pid, uid, gid}")

        if uid in clients.keys():
            print(f"Client already registered")
            conn.sendall(b"Denied\n")
            conn.close()
            continue

        clients[uid] = request["endpoint"]
        conn.sendall(b"ok\n")


    elif request["method"] == "send":

        if uid in clients.keys() or clientid in clients.keys():
            print(f"Sending to destination")
            print(f"data: {request["data"]}")
            conn.sendall(b"Sending\n")
            conn.close()
    else:
        print(f"Unknown request {request}")


    print("----")
    print("Listing all connected clients")
    # print(f"peer: pid={pid} uid={uid} gid={gid}")

    for c,v in clients.items():
        print(c,v)


    # if user != "partner_component":
    #     conn.sendall(b"Denied\n")
    #     conn.close()
    #     continue



    # print(f"claimed client: {request['client_id']}")

    # print("Received", data)
    # conn.sendall(b"ok\n")
    # conn.close()