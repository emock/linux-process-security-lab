
busctl --system list: Show current bus participants

bus-monitor --system | tee ~/dbus_monitor.log 

to log the current traffic 

Start the dbus_listener



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




## Binding a service name

Copy com.custom.logger.conf 

to /etc/dbus-1/system.d

then run

sudo systemctl restart dbus

The service VsendMessage is now available on dbus.

send a message to the SErvice:

gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vsendMessage 42


Observe the result


Update the policy file






