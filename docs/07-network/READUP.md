
| Command                              | Comment                                                                          |
|--------------------------------------|----------------------------------------------------------------------------------|
| ip netns list                        |                                                                                  |
| sudo ip netns exec ns_client ip addr |                                                                                  |
|tcpdump -Xlni veth-server udp port 5000| -X: ASCII and hex, -l buffer output stdout , -i interface, -n no name resolution |



dev@dev:~$ sudo ip netns exec ns_client ip addr
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
dev@dev:~$ sudo ip netns exec ns_server ip addr
1: lo: <LOOPBACK> mtu 65536 qdisc noop state DOWN group default qlen 1000
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00




Setup

Client and server are directly connected. 

10.10.0.1/24 <---- veth ----> 10.10.0.2/24



MITM Setup


ns_client           ns_mitm             ns_server
10.10.1.2    <-->  Router/MITM   <-->  10.10.2.2


sudo ip netns exec ns_server ss -lunp | grep 5000

Erwartung:

UNCONN 0 0 0.0:5000 0.0.0:*

Auf dem normalen Host kann Folgendes dagegen leer sein:

ss -lunp | grep 5000

Der Socket befindet sich schließlich in der Socket- beziehungsweise Netzwerkumgebung von ns_server.

Das ist bereits ein wichtiges Learning:

Derselbe Port kann in unterschiedlichen Network Namespaces unabhängig verwendet werden.







1. Loopback (127.0.0.1) ist tatsächlich ein Sonderfall

Wenn ein Prozess mit

sock.bind(("127.0.0.1", 5000))

lauscht und ein anderer Prozess auf demselben Host verbindet:

sock.connect(("127.0.0.1", 5000))

dann bleibt der gesamte Datenverkehr innerhalb des lokalen Netzwerk-Stacks.

Der Kernel stellt die Daten intern zu. Es gibt:

kein physisches Interface
keinen Switch
keinen Router
keinen externen Kommunikationspfad

Ein Network On-Path Attacker existiert daher nicht.






Observing Traffic

dev@dev:~$ sudo ip netns exec ns_server tcpdump -Xlni veth-server udp port 5000

Das demonstriert zunächst noch keinen MITM. Du beobachtest den Traffic direkt an einem Endpunkt.




Local unprivileged attacker and remote attacker

Sending of requests / Access to API

| Scenario        | Source    | Destination |                                                            |
|-----------------|-----------|-------------|------------------------------------------------------------|
| Local@localhost | ns_server | 127.0.0.1   | sudo ip netns exec ns_server python3 $(pwd)/01_attacker.py |
| local@IP         | ns_server | 10.10.0.2   | sudo ip netns exec ns_server python3 $(pwd)/01_attacker.py |
| Remote          | ns_client | 10.10.0.2   | sudo ip netns exec ns_client python3 $(pwd)/01_attacker.py |


Result
```commandline

('127.0.0.1', 43934) b'attacker calling'
('10.10.0.2', 48122) b'attacker calling'
('10.10.0.1', 32828) b'attacker calling'
```


Observing the output 

Given the general STRIDE matrix of a data flow and process, TCP/UDP on localhost for an unprivileged local attacker evaluates as follows:

|                 | S   | T          | R    | I          | D    | E    |
|-----------------|-----|------------|------|------------|------|------|
| Data flow       | no  | yes        | no   | yes        | yes  | no   |
| Process         | yes | yes        | yes  | yes        | yes  | yes  |
| Data flow (UDP) | yes | mitigated  | no   | mitigated  | yes  | no   |
| Process (UDP)   | yes | yes        | yes  | yes        | yes  | yes  |

If the attacker is privileged, the mititgations are no longer applicable. 


For a TCP on the network:

|                 | S   | T   | R    | I   | D    | E    |
|-----------------|-----|-----|------|-----|------|------|
| Data flow (UDP) | yes | yes | no | yes   | yes | no |
| Process (UDP)   | yes | yes | yes | yes | yes | yes |

The different threat scenario is derived from additional nodes (MITM) can intercept the traffic.
