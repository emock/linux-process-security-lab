import os
import time
import socket

def main():

    pid = os.getpid()
    print(pid, flush=True)

    print("Opening FD of pid")
    path = f"/proc/{pid}/fd/"


    # fds = os.listdir(path)
    # print(f"FDs: {fds}")

    with open("/tmp/secret", "r") as f:
        data = f.read()
        print(data)

        print("Holding FD open...")

        # time.sleep(10)

        SERVER_IP = "127.0.0.1"
        print(f"Opening Socket to {SERVER_IP}")

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_IP, 8080))

        for fd in os.listdir(path):
            try:
                print(fd, "->", os.readlink(f"{path}/{fd}"))
            except FileNotFoundError:
                print(fd, "-> already closed")

        while True:
            print("Sending data")
            s.sendall(b"TOP_SECRET\n")
            time.sleep(10)



if __name__ == '__main__':
    main()

    # while True:
    #     time.sleep(60)
    #     print("Running")
