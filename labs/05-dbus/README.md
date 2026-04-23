
# Useful Commands

| Command                                        | Note                                                                                                                    |      
|:-----------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| busctl --system list                           | Show current bus participants                                                                                           |
| bus-monitor --system \| tee ~/dbus_monitor.log | to log the current traffic                                                                                              
| dbus-monitor --system                               | Messages being sent on the bus can be inspected using:                                                                  | 
|Sending messages | dbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vSendMessage 42 |




# Scenario: DBUS Basics - Connecting to DBUS

Familiarize with DBUS and see who is currently on the bus:
```
busctl --system list 
```






# Scenario: DBUS Basics - Binding to a service Name

First lets start from scratch and run the listener.py using user dev:

Then try call one of the methods using:

```
gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vsendMessage 42
```
This will result in an error as a service needs to make its methods and properties public to the DBUS Daemon
for some other client to call these.

First copy the configuration file **com.custom.logger.conf** to to **/etc/dbus-1/system.d/**

Then execute the command
```
sudo systemctl restart dbus
```
The service VsendMessage from com.custom.logger.conf is now available on dbus.

Verify using: 

```
gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vsendMessage 42
```

Observe the result
TODO

## Scenario: Spoofing a service

- Deploy the config file spoofing.conf and restart DBUS
- Run sudo dbus-monitor --system to monitor the traffic
- run the script spoofing.sh
- Start the listener as user dev
- Start the client as user partner_component







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














