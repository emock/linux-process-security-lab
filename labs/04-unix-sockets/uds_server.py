import os
import socket
import grp
import struct
import json

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

while True:
    conn, _ = s.accept()

    # Linux SO_PEERCRED: pid, uid, gid des verbundenen Peers
    creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize("3i"))
    pid, uid, gid = struct.unpack("3i", creds)



    data = conn.recv(4096)

    request = json.loads(data.decode())

    print("----")
    print(f"peer: pid={pid} uid={uid} gid={gid}")
    print(f"claimed client: {request['client_id']}")
    # print(f"message: {request['message']}")

    #
    # print(f"peer pid={pid} uid={uid} gid={gid} sent={data!r}")


    # data = conn.recv(4096)
    # print("Received", data)
    conn.sendall(b"ok\n")
    conn.close()