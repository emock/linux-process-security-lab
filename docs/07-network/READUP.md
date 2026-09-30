# Linux Network Security

## Scope

This lab focuses on the capabilities of a local unprivileged and privileged attacker mainly targeting services exposed on
the localhost interface. 
A classic network attacker, e.g. modifying network routing is out of scope. 

As a remark: 
> I originally setup the lab using two namespaces, but then decided to limit the scope intentionally.
Therefore only the namespace ns_server is used. 
You can ignore the namespace ns_client.
I decided to keep it as it nicely shows usage and setup of namespaces in Linux, which might be useful in the future.


## Overview of useful commands

| Command                                 | Comment                                                                          |
|-----------------------------------------|----------------------------------------------------------------------------------|
| ip netns list                           |                                                                                  |
| sudo ip netns exec ns_client ip addr    | Checking network view                                                                                  |
| tcpdump -Xlni veth-server udp port 5000 | -X: ASCII and hex, -l buffer output stdout , -i interface, -n no name resolution |



## Technical Background

The lab makes use of linux network namespaces.



### Linux Network Namespaces


```commandline

    ns_client                       ns_server
┌─────────────────┐           ┌─────────────────┐
│ 10.10.0.1/24    │           │ 10.10.0.2/24    │
│ veth-client     │───────────│ veth-server     │
│                 │ veth      │                 │
│ UDP-Client      │           │ UDP-Server      │
└─────────────────┘           └─────────────────┘
```

Each Linux Network namespace is an isolated network view running on the same linux kernel and 
has its own network interface, IP address, routing tables, firewall rules and loopback.

```commandline
normal Host-Namespace
├── eth0
├── lo
├── Routingtable
└── open Ports

ns_client
├── veth-client
├── lo
├── Routingtable
└── open Ports

ns_server
├── veth-server
├── lo
├── Routingtable
└── open Ports
```

A network namespace is one layer of isolation. While the underlying kernel, filesystem and program 
are the same, the network view is different.

In the lab a veth pairing is used.
As analogy this can be best considered as a virtual network cable connecting two entities directly.

After successful setup inspecting the network namespace ns_client shows: 

```commandline
dev@dev:~/linux-process-security-lab/labs/07-network$ sudo ip netns exec ns_client ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
inet 127.0.0.1/8 scope host lo
valid_lft forever preferred_lft forever
inet6 ::1/128 scope host
valid_lft forever preferred_lft forever
4: veth-client@if3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
link/ether 4a:f9:5c:c7:57:fb brd ff:ff:ff:ff:ff:ff link-netns ns_server
inet 10.10.0.1/24 scope global veth-client
valid_lft forever preferred_lft forever
inet6 fe80::48f9:5cff:fec7:57fb/64 scope link
valid_lft forever preferred_lft forever

```

```commandline
dev@dev:~/linux-process-security-lab/labs/07-network$ sudo ip netns exec ns_server ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
3: veth-server@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 42:c3:91:76:47:3e brd ff:ff:ff:ff:ff:ff link-netns ns_client
    inet 10.10.0.2/24 scope global veth-server
       valid_lft forever preferred_lft forever
    inet6 fe80::40c3:91ff:fe76:473e/64 scope link 
       valid_lft forever preferred_lft forever


```

As described above, note that when querying network information inside the corresponding namespace it only shows 
what is visible *within* this network namespace, i.e. ns_client respectively.


### The Loopback interface

When a process binds on localhost using 

```python
sock.bind(("127.0.0.1", 5000))
```

and a different process on the same host connects to this socket using

```python
sock.connect(("127.0.0.1", 5000))
```

traffic is processed and locally delivered by the Linux kernel network stack via the loopback interface.


```commandline
Process A
    │
    │ socket
    v
┌──────────────────── Linux Kernel ───────────────────┐
│                                                     │
│ TCP/UDP → IP → local routing → lo → local delivery │
│                                                     │
└─────────────────────────────────────────────────────┘
    │
    │ socket
    v
Process B


```

Consequently for such a localhost connection there is no Man in the Middle on network layer possible.

#### Understanding Linux Networking

##### What addresses are available on the host?

```commandline
dev@dev:~$ ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: enp0s5: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 00:1c:42:ce:75:4d brd ff:ff:ff:ff:ff:ff
    inet 10.211.55.33/24 metric 100 brd 10.211.55.255 scope global dynamic enp0s5
       valid_lft 934sec preferred_lft 934sec
    inet6 fdb2:2c26:f4e4:0:21c:42ff:fece:754d/64 scope global dynamic mngtmpaddr noprefixroute 
       valid_lft 2591244sec preferred_lft 604044sec
    inet6 fe80::21c:42ff:fece:754d/64 scope link 
       valid_lft forever preferred_lft forever



```

##### Where to search for routing information? 

```commandline
dev@dev:~$ ip rule list
0:    from all lookup local
32766:    from all lookup main
32767:    from all lookup default
```

The details of the above tables can be inspected using:

```commandline
dev@dev:~$ ip route show table local
local 10.211.55.33 dev enp0s5 proto kernel scope host src 10.211.55.33 
broadcast 10.211.55.255 dev enp0s5 proto kernel scope link src 10.211.55.33 
local 127.0.0.0/8 dev lo proto kernel scope host src 127.0.0.1 
local 127.0.0.1 dev lo proto kernel scope host src 127.0.0.1 
broadcast 127.255.255.255 dev lo proto kernel scope link src 127.0.0.1

dev@dev:~$ ip route show table main
default via 10.211.55.1 dev enp0s5 proto dhcp src 10.211.55.33 metric 100 
10.211.55.0/24 dev enp0s5 proto kernel scope link src 10.211.55.33 metric 100 
10.211.55.1 dev enp0s5 proto dhcp scope link src 10.211.55.33 metric 100 
```

Each row consists of the following fields:

| TYPE  | DESTINATION | dev INTERFACE | proto ORIGIN | scope SCOPE | src PREFERRED_SOURCE |
|-------|-------------|---------------|--------------|-------------|----------------------|
| local | 127.0.0.1 | dev lo        | proto kernel | scope host  | src 127.0.0.1        |

Reference:
https://man7.org/linux/man-pages/man8/ip-route.8.html?utm_source=chatgpt.com



*Putting it together: How is the IP target address routed?*

```commandline
dev@dev:~$ ip route get 127.0.0.1
local 127.0.0.1 dev lo src 127.0.0.1 uid 1000 
    cache <local> 

dev@dev:~$ ip route get 10.211.55.33
local 10.211.55.33 dev lo src 10.211.55.33 uid 1000
cache <local>

dev@dev:~$ ip route get 10.211.55.1
10.211.55.1 dev enp0s5 src 10.211.55.33 uid 1000
cache

dev@dev:~$ ip route get 8.8.8.8
8.8.8.8 via 10.211.55.1 dev enp0s5 src 10.211.55.33 uid 1000 
    cache 

```

The entries reveal the following information for the first output above.

| Part            | Explanation                                                                                                   |
|-----------------|---------------------------------------------------------------------------------------------------------------|
| `local`         | The target is address is owned by the host and is delivered locally. Does not need to be sent to another host |
| `127.0.0.1`     | Target-IP                                                                                                     |
| `dev lo`        | The used Interface, here **Loopback-Interface `lo`**                                                          |
| `src 127.0.0.1` | Source address - here: 127.0.0.1                                                                              |
| `uid 1000`      | Routing path was calculated for UID `1000`                                                                    |
| `cache <local>` | Indicates a local route in the route lookup result                                                            |

| Part                 | Explanation                                                                                                   |
|----------------------|---------------------------------------------------------------------------------------------------------------|
| `local`              | The target is address is owned by the host and is delivered locally. Does not need to be sent to another host |
| `10.211.55.33`       | Target-IP                                                                                                     |
| `dev lo`             | The used Interface                                                                                            |
| `src `10.211.55.33`  | Source address                                                                                                |
| `uid 1000`           | Routing path was calculated for UID `1000`                                                                    |
| `cache <local>`      | Indicates a local route in the route lookup result                                                            |


If the `local` keyword is present the destination address is assigned to the local host
and the packet is delivered locally.
As shown above, this also applies to the IP address `10.211.55.33`: 
although the address is assigned to `enp0s5`, the route
lookup results in a local route and the packet is delivered locally.


## Unprivileged local attacker

The local attacker accesses the API directly on localhost.
The local unprivileged attacker has the following capabilities:
He have access to the API and can send requests.


| Scenario        | Source    | Destination |                                                            |
|-----------------|-----------|-------------|------------------------------------------------------------|
| Local@localhost | ns_server | 127.0.0.1   | sudo ip netns exec ns_server python3 $(pwd)/01_attacker.py |
| local@IP         | ns_server | 10.10.0.2   | sudo ip netns exec ns_server python3 $(pwd)/01_attacker.py |


The following result show calling the API from a local attacker using localhost and the network interface.

```commandline

('127.0.0.1', 43934) b'attacker calling'
('10.10.0.2', 48122) b'attacker calling'
```

While the result seems obvious, it serves as a reminder to not consider localhost as a trusted environment for networking.
Any rogue application having access to the listening socket can interact with a service. 

### Privileged local attacker

The attacker has the capability `CAP_NET_RAW` and intercepts traffic on UDP Port 5000 on the
sender side ns_client.
We assigned the capability to the python process
`sudo setcap cap_net_raw+ep /usr/bin/python3.12`

This allows him to 
- passively intercept traffic (sniffing)
- craft own messages
- replay packets

It does not enable him to tamper with traffic on the wire, such dropping packets or modifying packet content.

Below is 

```commandline
###[ Ethernet ]###
  dst       = 42:c3:91:76:47:3e
  src       = 4a:f9:5c:c7:57:fb
  type      = IPv4
###[ IP ]###
     version   = 4
     ihl       = 5
     tos       = 0x0
     len       = 46
     id        = 31108
     flags     = DF
     frag      = 0
     ttl       = 64
     proto     = udp
     chksum    = 0xad24
     src       = 10.10.0.1
     dst       = 10.10.0.2
     \options   \
###[ UDP ]###
        sport     = 52679
        dport     = 5000
        len       = 26
        chksum    = 0x1442
###[ Raw ]###
           load      = b'testing intercept\n'

```

This mimicks the capabilities of using `tcpdump`

```commandline
dev@dev:~$ sudo ip netns exec ns_server tcpdump -Xlni veth-server udp port 5000
```

Note that this is not a network MITM scenario as the traffic is observed on one of the endpoints.
Though, this scenario is only possible for a *privileged attacker*.





## Security Properties 

Given the general STRIDE matrix of a data flow and process, 
TCP/UDP on localhost for an unprivileged local attacker evaluates as follows:

|                 | S   | T          | R    | I          | D    | E    |
|-----------------|-----|------------|------|------------|------|------|
| Data flow       | no  | yes        | no   | yes        | yes  | no   |
| Data flow (UDP) | no  | mitigated  | no   | mitigated  | yes  | no   |
| Process         | yes | yes        | yes  | yes        | yes  | yes  |
| Process (UDP)   | yes | yes        | yes  | yes        | yes  | yes  |

If the attacker is privileged, the mititgations are no longer applicable. 



[//]: # (TODO Move to different project)
[//]: # (For a MITM attacker on the network:)

[//]: # ()
[//]: # (|                  | S     | T    | R    | I    | D    | E    |)

[//]: # (|------------------|-------|------|------|------|------|------|)

[//]: # (| Data flow &#40;UDP&#41;  | no    | yes  | no   | yes  | yes  | no   |)

[//]: # (| Process &#40;UDP&#41;    | yes   | yes  | yes  | yes  | yes  | yes  |)

[//]: # ()
[//]: # (The different threat scenario is derived from additional nodes &#40;MITM&#41; can intercept the traffic.)



