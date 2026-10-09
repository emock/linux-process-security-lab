

# Scenario 1: Reading out File Descriptors 

1. Run script ./setup: This installs the .py files in /tmp
2. Run nc -l 127.0.0.1 8080
3. Run /tmp/fd_visibility: the program opens a file handle to a file, 
keeps it open and then sends data to the TCP socket.
4. Wait until the script starts sending data to the nc listener
5. Run `python3 /tmp/attacker.py "$victim_pid"` within this time window as user dev
6. Run `sudo -u partner2 python3 /tmp/attacker.py "$victim_pid"` within this time window

















