# DBUS

## Result

| Scenario            | /etc/dbus-1/system.d      \<allow/\> Primitives | dev | partner | third_party |
|:--------------------|:------------------------------------------------|:----|:--------|:------------|
| 01 Connect          | none (socket reachable)                         | X   | X       | X           |
| 02 Own service name | own="com.custom.logger"                         | X   | N       | N           |
| 02 Send method call | send_destination="com.custom.logger"            | X   | N       | N           |
| Listening           |                                                 | X   | X       | N           |


## Technical Background

The system bus is typically exposed via the Unix Domain Socket:
/run/dbus/system_bus_socket (/var/run/dbus/system_bus_socket is often a symlink)


While the name DBUS indicates an open bus, the messages on the bus are more like Unicasts and only the receiver 
can access those.

A User will get all access rights for the corresponding user and groups he is a member of.
That is:

user dev will get permissions of

User: dev
Group: dev
Group: shared_group

User:Partner_component
Group: partner_component
Group: shared_group





### Sequence

**Service perspective:**

1. Connect to the Bus
2. Export a service 



**Client perspective**
1. Connect to the bus
2. Send a message







----


## Useful commands

| Command                                                                                                          | Description                   | Note                                        |      
|:-----------------------------------------------------------------------------------------------------------------|-------------------------------|:--------------------------------------------|
| dbus-monitor --system "interface='com.custom.logger'" \| tee ~/dbus_monitor.log                                  | Log traffic                   | Prefer dbus-monitor over busctl for logging |
| busctl --system list                                                                                             | Show current bus participants |                                             |                                             |
| busctl --address=unix:path=/tmp/dbus call SERVICE PATH INTERFACE METHOD SIGNATURE VALUES                         | Send                          |                                             |
| busctl introspect com.custom.logger /com/custom/logger                                                           | Introspection                 |                                             |
| busctl --system status com.custom.logger                                                                         | Show service status      |                                             |
| gdbus call --system --dest com.logger --object-path /com/logger --method com.logger.vSendMessage 42 "hello" True | GDBUS Send                    |                                             |
| gdbus introspect --system --dest com.custom.logger --object-path /com/custom/logger                              | GDBUS Introspect              |                                             |
| ssh -NT -L /tmp/dbus:/run/dbus/system_bus_socket SSH_HOST                                                        | SSH Tunnel of Unix Socket     |                                             |
















----

## Scenario 01: Connecting to DBUS

First inspect the current bus participants using busctl:


``` 
NAME PID PROCESS USER CONNECTION UNIT SESSION DESCRIPTION
:1.124 20623 polkitd polkitd          :1.124 polkit.service - -
:1.126 20665 ModemManager root             :1.126 ModemManager.service - -
...
:1.269 33414 dbus-monitor dev              :1.269 session-166.scope 166 -
:1.280 33486 busctl dev              :1.280 session-155.scope 155 -
...
org.freedesktop.timesync1 31482 systemd-timesyn systemd-timesync :1.225 systemd-timesyncd.service - -

```

The full log is available in [busctl_before.txt](01_busctl_before.txt)


When a client connects to the system bus:

```
bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
```

we can observe a NameOwnerChanged message in dbus-monitor:

```
signal time=1775722702.656383 sender=org.freedesktop.DBus -> destination=(null destination) serial=316
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.282"
string ""
string ":1.282"
```



At connection time, the bus daemon can obtain the peer's UID, GID and PID from the kernel via SO_PEERCRED.

UID/PID spoofing at the socket layer is prevented by design.


We can verify that this is our python listener by checking busctl:

```
NAME PID PROCESS USER CONNECTION UNIT SESSION DESCRIPTION
...
:1.281 33488 dbus-monitor dev              :1.281 session-166.scope 166 -
:1.282 33495 python dev              :1.282 session-163.scope 163 -
:1.283 33496 busctl dev              :1.283 session-155.scope 155 -
...

```

The full log is available in [busctl_after.txt](01_busctl_after.txt)



busctl --system list briefly connects to the system bus as a normal client, performs method calls to query the current
state, and disconnects immediately afterwards

```
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

```
:1.283 33496 busctl dev              :1.283 session-155.scope 155 -
```

When we stop our listener this issues a new message NameOwnerChanged to the system bus indicating
a deregistration:

```
signal time=1775722714.404157 sender=org.freedesktop.DBus -> destination=(null destination) serial=319
path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
string ":1.282"
string ":1.282"
string ""
```




----

## Scenario 02: Basic Operations - Name Binding and Sending

We define a very simple Service called Logger.
This service just offers one method vSendMessage and prints it to command line.

We model the interaction on the system as follows:

| Component          | User              |
|:-------------------|:------------------|
| dbus_listener      | dev               |
| dbus_client        | partner_component |


Furthermore for this to work the minimal required permissions on DBUS are documented in [com.custom.logger.conf](/labs/05-dbus/02_com.custom.logger.conf)

```
<busconfig>
  <policy user="dev">
    <allow own="com.custom.logger"/>
  </policy>

  <policy user="partner_component">
      <allow send_destination="com.custom.logger"/>
    </policy>
```

This grants the user dev to bind the name com.custom.logger and user partner_component to send messages to this service.

Without the own primitive the listener would encounter an error when doing 

```
dbus_next.errors.DBusError: Connection ":1.1" is not allowed to own the service "com.custom.Logger" due to security
policies in the configuration file
```

The same goes for sending messages to a service.

When calling the service via

```
dev@dev:~$ gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method
com.custom.logger.vsendMessage 42
```

and no allow primitive set, DBUS replies with an AccessDenied message:

```
Error: GDBus.Error:org.freedesktop.DBus.Error.AccessDenied: Rejected send message, 1 matched rules; type="method_call",
sender=":1.4" (uid=1000 pid=34193 comm="gdbus call --system --dest com.custom.logger --obj" label="unconfined")
interface="com.custom.logger" member="vsendMessage" error name="(unset)" requested_reply="0" destination="
com.custom.logger" (uid=1000 pid=34192 comm="/home/dev/.virtualenvs/linux-process-security-lab/" label="unconfined")

```

Hint:
Granting send_destination to the service’s own bus name is typically redundant in simple setups, but still increases
the process’ ability to actively trigger its own DBus interface.

```angular2html
<policy user="dev">
    <allow send_destination="com.custom.logger"/>
</policy>
```

Adding this policy also allows us to introspect the service and get the method signatures using

**gdbus introspect --system --dest com.custom.logger --object-path /com/custom/logger**

``` 
node /com/custom/logger {
  interface org.freedesktop.DBus.Introspectable {
    methods:
      Introspect(out s data);
    signals:
    properties:
  };
  interface org.freedesktop.DBus.Peer {
    methods:
      GetMachineId(out s machine_uuid);
      Ping();
    signals:
    properties:
  };
  interface org.freedesktop.DBus.Properties {
    methods:
      Get(in  s interface_name,
          in  s property_name,
          out v value);
      Set(in  s interface_name,
          in  s property_name,
          in  v value);
      GetAll(in  s interface_name,
             out a{sv} props);
    signals:
      PropertiesChanged(s interface_name,
                        a{sv} changed_properties,
                        as invalidated_properties);
    properties:
  };
  interface org.freedesktop.DBus.ObjectManager {
    methods:
      GetManagedObjects(out a{oa{sa{sv}}} objpath_interfaces_and_properties);
    signals:
      InterfacesAdded(o object_path,
                      a{sa{sv}} interfaces_and_properties);
      InterfacesRemoved(o object_path,
                        as interfaces);
    properties:
  };
  interface com.custom.logger {
    methods:
      vSendMessage(in  i number);
    signals:
    properties:
  };
};



```

Note that any unauthorized party, such as user third_party, will not be able to interact with the service nor send a message to it.
DBUS will report an AccessDenied Error, e.g.:

```angular2html
Error: GDBus.Error:org.freedesktop.DBus.Error.AccessDenied: Rejected send message, 1 matched rules; 
type="method_call", sender=":1.3" (uid=1002 pid=58132 comm="gdbus introspect --system --dest com.custom.logger" 
label="unconfined") interface="org.freedesktop.DBus.Introspectable" member="Introspect" error name="(unset)" 
requested_reply="0" destination="com.custom.logger" (uid=1000 pid=58123 comm="python3 /tmp/dbus_listener.py" 
label="unconfined")
```


### Scenario 03 : Spoofing

We extend the Bind scenario to demonstrate Name Hijacking or Spoofing misuses on DBUS.

The setup is similar to above:

We model the interaction on the system as follows:

| Component          | User              |
|:-------------------|:------------------|
| dbus_listener      | dev               |
| dbus_client        | partner_component |
| dbus_listener        | partner_component |

Partner_component acts as partly trusted peer, but also maliciously tries to impersonate as dbus_listener.

This is possible if the configuration contains a misconfiguration such as in [Spoofing](/labs/05-dbus/03_spoofing.conf)
```
  <policy user="partner_component">
    <allow own="com.custom.logger"/>
  </policy>

```

Preconditition for the Attack to succeed:
Partner component needs to kill the service offered by dbus_listener, e.g. by causing a crash.

While the first messages are correctly adressed to L1

```angular2html
/home/dev/.virtualenvs/linux-process-security-lab/bin/python
/home/dev/linux-process-security-lab/labs/05-dbus/dbus_listener.py
Connected to system bus
[SERVICE] vSendMessage received: 0 hello-0 True
[SERVICE] vSendMessage received: 1 hello-1 True
[SERVICE] vSendMessage received: 2 hello-2 True
[SERVICE] vSendMessage received: 3 hello-3 True
[SERVICE] vSendMessage received: 4 hello-4 True
[SERVICE] vSendMessage received: 5 hello-5 True
```

after L1 is stopped/crashed the following messages are sent to L2.

``` 

dev@dev:/tmp$ sudo -u partner_component python3 dbus_listener.py
Connected to system bus
[SERVICE] vSendMessage received: 6 hello-6 True
[SERVICE] vSendMessage received: 7 hello-7 True
[SERVICE] vSendMessage received: 8 hello-8 True
[SERVICE] vSendMessage received: 9 hello-9 True
[SERVICE] vSendMessage received: 10 hello-10 True
[SERVICE] vSendMessage received: 11 hello-11 True
[SERVICE] vSendMessage received: 12 hello-12 True

```

This is completely transparent to client C.
See the detailed log [./03_spoofing.log]

This is reflected in the log:

```
method call time=1776775347.079210 sender=:1.13 -> destination=com.custom.logger serial=7 path=/com/custom/logger; interface=com.custom.logger; member=vSendMessage
   int32 5
   string "hello-5"
   boolean true
method return time=1776775347.080082 sender=:1.11 -> destination=:1.13 serial=9 reply_serial=7
signal time=1776775347.428609 sender=org.freedesktop.DBus -> destination=:1.11 serial=5 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameLost
   string "com.custom.logger"
signal time=1776775347.428653 sender=org.freedesktop.DBus -> destination=(null destination) serial=9 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameOwnerChanged
   string "com.custom.logger"
   string ":1.11"
   string ":1.12"
signal time=1776775347.428659 sender=org.freedesktop.DBus -> destination=:1.12 serial=4 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameAcquired
   string "com.custom.logger"
signal time=1776775347.428664 sender=org.freedesktop.DBus -> destination=:1.11 serial=6 path=/org/freedesktop/DBus; interface=org.freedesktop.DBus; member=NameLost
   string ":1.11"

```
We can clearly see that after message hello-5 the bus node 1.11 reports a NameLost.
As another member is on the bus with the same name, the bus switches to NameOwnerChanged and assigns the com.custom.logger to
node 1.12 as the new owner.






## Scenario 04 - Overbroad Interfaces

The listener implements a privileged method, such as vWriteLogs which accepts a filename and logging contents.

The setup is as follows:

| Component           | User              |
|:--------------------|:------------------|
| dbus_listener       | dev               |
| dbus_client         | partner_component |
| privileged_client   | partner_component |
| Unauthorized client | partner2          |


The DBUS policy is intentionally misconfigured so that all members of **shared_group** can access all the methods 
of the logger.

``` 
  <policy group="shared_group">
      <allow send_destination="com.custom.logger"/>
    </policy>
```

partner2 calls the privileged method using:

sudo -u partner2 gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vWriteLog "partner2.log" "I can access this method though I am not privileged"

This results in creation of a log file with the desired contents: 

```
dev@dev:/tmp/overbroad_logs$ ls
log-0  log-1  log-2  partner2.log
dev@dev:/tmp/overbroad_logs$ cat partner2.log
I can access this method though I am not privileged
```

The full log of the listener is attached.

```
[SERVICE] vSendMessage received: 1 hello-1 True
[SERVICE] vSendMessage received: 2 hello-2 True
[SERVICE] vSendMessage received: 3 hello-3 True
[SERVICE] vSendMessage received: 4 hello-4 True
[SERVICE] vWriteLog : partner2.log I can access this method though I am not privileged
[SERVICE] vWriteLog : log-1 hello-1
[SERVICE] vSendMessage received: 5 hello-5 True
[SERVICE] vSendMessage received: 6 hello-6 True
[SERVICE] vSendMessage received: 7 hello-7 True
[SERVICE] vSendMessage received: 8 hello-8 True
[SERVICE] vSendMessage received: 9 hello-9 True
[SERVICE] vWriteLog : log-2 hello-2
[SERVICE] vSendMessage received: 10 hello-10 True

```

Side note:
The implementation of vWriteLogs has intentionally a Command Injection Vulnerability included.





## Scenario: Observing Traffic

- Start the listener
- start the client
- dbus-monitor --system
   - observe
- sudo dbus-monitor --system
   - observe


A listener - even started as the same UID as dev - will not be able to monitor bus traffic directed the 
tuple (PID, UID, GID) which uniquely identifies a process in DBUS.
Therefore even the command 

dbus-monitor --system run as user dev

will not show messages being received by the listener.

### Inspecting Traffic


#### Using root privileges 
One possibility to do so it to observe DBUS Traffic as root

sudo dbus-monitor --system 


```
method call time=1776763208.322221 sender=:1.63 -> destination=com.custom.logger serial=72 path=/com/custom/logger; interface=com.custom.logger; member=vSendMessage
   int32 70
   string "hello-70"
   boolean true
method return time=1776763208.323804 sender=:1.62 -> destination=:1.63 serial=74 reply_serial=72

```

This shows the sent and received messages on the system bus. 


#### Using receive primitive

According to DBUS spec the primitive send_destination and receive_sender can be used

"send_destination and receive_sender rules mean that messages may not be sent to or received from the *owner* of the
given name, not that they may not be sent *to that name*. That is, if a connection owns services A, B, C, and sending to
A is denied, sending to B or C will not work either. As a special case, send_destination="*" matches any message (
whether it has a destination specified or not), and receive_sender="*" similarly matches any message."



Using a A primitive 
<allow receive_sender="com.custom.logger" />

is a no-op.

As a default receiving of messages is allowed.

The exact mechanism and working of receive_sender is unclear at this point.







Observing Traffic

Der entscheidende Punkt ist:

dbus-monitor als normaler User auf dem System Bus sieht fremde Unicast-Method-Calls nicht automatisch, auch dann nicht,
wenn du theoretisch eavesdrop="true" gesetzt hast.
Die D-Bus-Spezifikation beschreibt BecomeMonitor sogar als den bevorzugten Weg zum Monitoring; klassisches Eavesdropping
ist eher ein älterer Mechanismus für Debugging-Tools.

Das erklärt genau dein DEV-Verhalten:

dev startet den Service
dev startet den Client
dev startet dbus-monitor
trotzdem sieht dbus-monitor die Method Calls nicht

Denn aus Sicht des Busses sind das drei verschiedene Connections, und der Monitor ist nur ein dritter, unbeteiligter
Client. Die dbus-monitor-Manpage sagt ausdrücklich, dass die Bus-Konfiguration verhindern kann, dass dbus-monitor alle
Nachrichten sieht, insbesondere als Nicht-Root-User.

Dass Root alles sieht, passt ebenfalls: Das ist praktisch der privilegierte Monitoring-Fall. Die D-Bus-Spezifikation
nennt BecomeMonitor als den besseren Monitoring-Mechanismus, und in der Praxis laufen solche vollständigen
Bus-Mitschnitte typischerweise nur privilegiert.

Kurz gesagt: Nein — nur receive reicht nicht. Und selbst mit eavesdrop wirst du auf dem System Bus als normaler User in
der Praxis meist trotzdem nichts sehen.

Ich räume das einmal sauber auf, weil hier mehrere Ebenen zusammenkommen:

🧠 TL;DR

❌ receive ⇒ kein Mithören
❌ receive + eavesdrop ⇒ theoretisch ja, praktisch oft nein (System Bus)
✔ echtes Mithören ⇒ Monitor Mode (root)

🔍 1. Deine konkrete Frage

Wenn ich receive hinzufüge → sehe ich dann Traffic?

👉 Nein

Warum:

receive = Nachrichten, die an dich gehen

Du bist aber:

Monitor ≠ Ziel der Nachricht
🔥 2. Was du eigentlich brauchst

Für echtes Mithören:

<allow eavesdrop="true"/>

👉 das ist der richtige Mechanismus

⚠️ 3. Warum es trotzdem nicht funktioniert

Das ist der entscheidende Punkt:

❗ Auf dem System Bus wird Eavesdropping in der Praxis stark eingeschränkt

Gründe (realistisch):

1. Moderne Implementierung (dbus-daemon / dbus-broker)
   eavesdrop wird kaum noch effektiv genutzt
   Monitoring läuft über:
   BecomeMonitor
2. dbus-monitor Verhalten

Als normaler User:

→ nutzt Match Rules (AddMatch)
→ KEIN echter Monitor Mode

3. System Bus Design

Der System Bus ist:

„locked down“

→ absichtlich

🧠 4. Warum root funktioniert
sudo dbus-monitor --system

👉 nutzt:

Monitor Connection (privileged)

→ sieht alles

→ ignoriert eavesdrop

## Security Policies

Define Policies for Unix users and groups

Deny by default

Wenn du keine send-Rechte hast:

👉 kannst du NICHT:

Methoden aufrufen
Introspect machen
Properties lesen

👉 aber kannst oft:

sehen, dass der Service existiert
gewisse Signals beobachten

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
