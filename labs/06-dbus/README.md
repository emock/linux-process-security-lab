
# Useful Commands

| Command                                        | Note                                                                                                                    |      
|:-----------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| busctl --system list                           | Show current bus participants                                                                                           |
| bus-monitor --system \| tee ~/dbus_monitor.log | to log the current traffic                                                                                              
| dbus-monitor --system                               | Messages being sent on the bus can be inspected using:                                                                  | 
|Sending messages | dbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vSendMessage 42 |




# Scenario 01: DBUS Basics - Connecting to DBUS

Familiarize with DBUS and see who is currently on the bus:
```
busctl --system list 
```

TODO




# Scenario 2: DBUS Basics - Binding to a service Name

- Run script: ./02_bind.sh


## Scenario 03: Spoofing a service

- Monitor the traffic:  sudo dbus-monitor --system 
- Run script: ./03_spoofing.sh

## Scenario 04: Overbroad Interfaces

- Run script: ./04_overbroad_interfaces.sh
- sudo -u partner2 gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method
com.custom.logger.vWriteLog "hello.log;id| tee /tmp/overbroad_logs/POC" "contents test test"









# Scenario Observing Communication

Observing communication

- Start the listener
- start the client
- dbus-monitor --system
  - observe
- sudo dbus-monitor --system
  - observe



This will show the traffic

Information Disclosure

Create a file eavesdrop.conf as root and put it into

dev@dev:/etc/dbus-1/system.d$ ls -al
total 16
drwxr-xr-x 2 root root 4096 Apr 9 09:04 .
drwxr-xr-x 4 root root 4096 Feb 10 00:26 ..
-rw-r--r-- 1 root root 662 Jul 2 2025 com.ubuntu.SoftwareProperties.conf
-rw-r--r-- 1 root root 243 Apr 9 09:04 eavesdrop.conf


then restart the system bus

sudo systemctl restart dbus

and observe again.














