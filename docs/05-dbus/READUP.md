# DBUS

## Technical Background

The system bus is typically exposed via the Unix Domain Socket:
/run/dbus/system_bus_socket (/var/run/dbus/system_bus_socket is often a symlink)







Sequence

1. Connect to the Bus


## Useful commands

DBUS participants can be inspected using

```
busctl --system list
```

Messages being sent on the bus can be inspected using:

```angular2html
dbus-monitor --system
```

## Connecting to DBUS



First inspect the current bus participants using busctl:


``` 
NAME PID PROCESS USER CONNECTION UNIT SESSION DESCRIPTION
:1.124 20623 polkitd polkitd          :1.124 polkit.service - -
:1.126 20665 ModemManager root             :1.126 ModemManager.service - -
:1.219 1 systemd root             :1.219 init.scope - -
:1.222 31474 systemd-network systemd-network  :1.222 systemd-networkd.service - -
:1.224 31490 udisksd root             :1.224 udisks2.service - -
:1.225 31482 systemd-timesyn systemd-timesync :1.225 systemd-timesyncd.service - -
:1.226 31475 systemd-resolve systemd-resolve  :1.226 systemd-resolved.service - -
:1.227 31491 upowerd root             :1.227 upower.service - -
:1.251 32820 systemd dev              :1.251 user@1000.service - -
:1.269 33414 dbus-monitor dev              :1.269 session-166.scope 166 -
:1.280 33486 busctl dev              :1.280 session-155.scope 155 -
:1.6 745 systemd-logind root             :1.6 systemd-logind.service - -
:1.8 801 unattended-upgr root             :1.8 unattended-upgrades.service - -
com.ubuntu.SoftwareProperties - - -                (activatable) - - -
io.netplan.Netplan - - -                (activatable) - - -
org.freedesktop.DBus 1 systemd root - init.scope - -
org.freedesktop.ModemManager1 20665 ModemManager root             :1.126 ModemManager.service - -
org.freedesktop.PackageKit - - -                (activatable) - - -
org.freedesktop.PolicyKit1 20623 polkitd polkitd          :1.124 polkit.service - -
org.freedesktop.UDisks2 31490 udisksd root             :1.224 udisks2.service - -
org.freedesktop.UPower 31491 upowerd root             :1.227 upower.service - -
org.freedesktop.bolt - - -                (activatable) - - -
org.freedesktop.fwupd - - -                (activatable) - - -
org.freedesktop.hostname1 - - -                (activatable) - - -
org.freedesktop.locale1 - - -                (activatable) - - -
org.freedesktop.login1 745 systemd-logind root             :1.6 systemd-logind.service - -
org.freedesktop.network1 31474 systemd-network systemd-network  :1.222 systemd-networkd.service - -
org.freedesktop.resolve1 31475 systemd-resolve systemd-resolve  :1.226 systemd-resolved.service - -
org.freedesktop.systemd1 1 systemd root             :1.219 init.scope - -
org.freedesktop.thermald - - -                (activatable) - - -
org.freedesktop.timedate1 - - -                (activatable) - - -
org.freedesktop.timesync1 31482 systemd-timesyn systemd-timesync :1.225 systemd-timesyncd.service - -


```

When a client connects to the system bus:

```angular2html

bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
```

we can observe a NameOwnerChanged message in dbus-monitor:

signal time=1775722702.656383 sender=org.freedesktop.DBus -> destination=(null destination) serial=316
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.282"
string ""
string ":1.282"


At connection time, the bus daemon can obtain the peer's UID, GID and PID from the kernel via SO_PEERCRED.

UID/PID spoofing at the socket layer is prevented by design.






We can verify that this is out python listener by checking busctl:

```angular2html
:1.282 33495 python dev              :1.282 session-163.scope 163 -
```

Full Log:
```angular2html
NAME PID PROCESS USER CONNECTION UNIT SESSION DESCRIPTION
:1.124 20623 polkitd polkitd          :1.124 polkit.service - -
:1.126 20665 ModemManager root             :1.126 ModemManager.service - -
:1.219 1 systemd root             :1.219 init.scope - -
:1.222 31474 systemd-network systemd-network  :1.222 systemd-networkd.service - -
:1.224 31490 udisksd root             :1.224 udisks2.service - -
:1.225 31482 systemd-timesyn systemd-timesync :1.225 systemd-timesyncd.service - -
:1.226 31475 systemd-resolve systemd-resolve  :1.226 systemd-resolved.service - -
:1.227 31491 upowerd root             :1.227 upower.service - -
:1.251 32820 systemd dev              :1.251 user@1000.service - -
:1.281 33488 dbus-monitor dev              :1.281 session-166.scope 166 -
:1.282 33495 python dev              :1.282 session-163.scope 163 -
:1.283 33496 busctl dev              :1.283 session-155.scope 155 -
:1.6 745 systemd-logind root             :1.6 systemd-logind.service - -
:1.8 801 unattended-upgr root             :1.8 unattended-upgrades.service - -
com.ubuntu.SoftwareProperties - - -                (activatable) - - -
io.netplan.Netplan - - -                (activatable) - - -
org.freedesktop.DBus 1 systemd root - init.scope - -
org.freedesktop.ModemManager1 20665 ModemManager root             :1.126 ModemManager.service - -
org.freedesktop.PackageKit - - -                (activatable) - - -
org.freedesktop.PolicyKit1 20623 polkitd polkitd          :1.124 polkit.service - -
org.freedesktop.UDisks2 31490 udisksd root             :1.224 udisks2.service - -
org.freedesktop.UPower 31491 upowerd root             :1.227 upower.service - -
org.freedesktop.bolt - - -                (activatable) - - -
org.freedesktop.fwupd - - -                (activatable) - - -
org.freedesktop.hostname1 - - -                (activatable) - - -
org.freedesktop.locale1 - - -                (activatable) - - -
org.freedesktop.login1 745 systemd-logind root             :1.6 systemd-logind.service - -
org.freedesktop.network1 31474 systemd-network systemd-network  :1.222 systemd-networkd.service - -
org.freedesktop.resolve1 31475 systemd-resolve systemd-resolve  :1.226 systemd-resolved.service - -
org.freedesktop.systemd1 1 systemd root             :1.219 init.scope - -
org.freedesktop.thermald - - -                (activatable) - - -
org.freedesktop.timedate1 - - -                (activatable) - - -
org.freedesktop.timesync1 31482 systemd-timesyn systemd-timesync :1.225 systemd-timesyncd.service - -


```


busctl --system list briefly connects to the system bus as a normal client, performs method calls to query the current
state, and disconnects immediately afterwards

```angular2html
signal time=1775722708.090243 sender=org.freedesktop.DBus -> destination=(null destination) serial=317
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.283"
string ""
string ":1.283"
signal time=1775722708.100702 sender=org.freedesktop.DBus -> destination=(null destination) serial=318
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.283"
string ":1.283"
string ""

```

This entity 1.283 is also visible in the current snapshot of busctl

```angular2html
:1.283 33496 busctl dev              :1.283 session-155.scope 155 -
```

When we stop our listener this issues a new message NameOwnerChanged to the system bus indicating
a deregistration:

```angular2html

signal time=1775722714.404157 sender=org.freedesktop.DBus -> destination=(null destination) serial=319
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.282"
string ":1.282"
string ""


```


### Security mechanisms

- Transport access: connect to socket
- Authentication / identity binding: peer credentials via kernel
- Authorization: bus policy: own/send/receive/eavesdrop
- Service-side security: the target service must still validate the caller and input correctly

Connecting to the bus is intentionally easy; authorization is enforced later when attempting to own names, send method
calls, receive certain messages, or monitor traffic.

DAC on the system bus.

```angular2html
dev@dev:/var/run/dbus$ ls -al
total 0
drwxr-xr-x 3 root root 80 Mar 12 15:02 .
drwxr-xr-x 29 root root 960 Apr 9 08:18 ..
drwxr-xr-x 2 messagebus root 40 Mar 12 15:02 containers
srw-rw-rw- 1 root root 0 Mar 12 15:02 system_bus_socket

```
This might differ for session busses as here a predefined group 
might only be permitted to read and write according to DAC.


A second security mechanism for DBUS:
System bus policy is typically defined through XML files under /etc/dbus-1/system.d/ and /usr/share/dbus-1/system.d/.


However not for connecting to the bus but rather which user
is allowed to send or receive which messages.

Only if

<allow eavesdrop="true"/>

is set
Information Disclosure/Sniffing
is possible for any participant who can only connect to the bus.

Otherwise a participant will only see messages that are adressed to its address 
or signals (broadcasts).


When connecting to the bus an entity needs to authenticate by providing
the UID, GID and PID to the kernel.
Therefore Spoofing is not possible by design.


In order to conduct these changes, root privileges are needed:

```angular2html
dev@dev:/etc/dbus-1/system.d$ ls -al
total 16
drwxr-xr-x 2 root root 4096 Apr 9 09:04 .
drwxr-xr-x 4 root root 4096 Feb 10 00:26 ..
-rw-r--r-- 1 root root 662 Jul 2 2025 com.ubuntu.SoftwareProperties.conf
-rw-r--r-- 1 root root 243 Apr 9 09:04 eavesdrop.conf

```

eavesdrop.conf
```angular2html
<!DOCTYPE busconfig PUBLIC
 "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">

<busconfig>
  <policy context="default">
    <allow eavesdrop="true"/>
  </policy>
</busconfig>


```


Hinweis:
Denn „Spoofing“ kann je nach Kontext auch heißen:

Well-known name übernehmen
Service-Impersonation
confused deputy
Trust in sender name statt in UID