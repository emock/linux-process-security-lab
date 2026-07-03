| Thema                    | Priorität | Warum                |
| ------------------------ | --------: | -------------------- |
| DAC / connect boundary   |      High | Grundschutz          |
| Information Disclosure   |      High | schnell abschließbar |
| Tampering                |      High | schnell abschließbar |
| `SO_PEERCRED` / Spoofing | Very High | PROD-relevant        |
| Routing / proxy abuse    | Very High | direkt euer CGW-Case |
| Request Authorization    | Very High | Kernrisiko           |
| DoS                      |    Medium | nice-to-have         |
| `SCM_RIGHTS`             |    Medium | novelty              |
| Same-user ptrace         |       Low | bereits Lab 01       |

## Technical Background

Access to the socket.
As elaborated in lab 01-process-isolation the socket object is only
accessible to the owning process.

```
dev@dev:/proc/106031/fd$ ls -al
total 0
dr-x------ 2 dev dev  5 Jun 15 11:20 .
dr-xr-xr-x 9 dev dev  0 Jun 15 11:17 ..
lrwx------ 1 dev dev 64 Jun 15 11:20 0 -> /dev/pts/4
lrwx------ 1 dev dev 64 Jun 15 11:20 1 -> /dev/pts/4
lrwx------ 1 dev dev 64 Jun 15 11:20 2 -> /dev/pts/4
lrwx------ 1 dev dev 64 Jun 15 11:20 3 -> 'socket:[807998]'
```

This implies that eavesdropping is not possible for another process,
as the socket handle is only accessible to the owning process.
The same is true for Tampering.


Though what is possible, if an attacker has gained root privileges
Eavesdropping using strace `sudo strace -p {PID} -e read,recvmsg,write,sendmsg`

```commandline
dev@dev:/run$ sudo strace -p 106031 -e read,recvmsg,write,sendmsg
strace: Process 106031 attached
write(1, "Received b'SECRET\\n'\n", 21) = 21


```




Capabilities:
CAP_SYS_PTRACE: allows strace, gdb attach, ptrace
CAP_SYS_ADMIN: root-like
CAP_BPF + CAP_PERFMON: eBPF uprobes/kprobes, syscall tracing, socket instrumentation
Same-UID + ptrace-Regeln:

Check using `cat /proc/sys/kernel/yama/ptrace_scope`

| Wert | Bedeutung                 |
| ---- | ------------------------- |
| `0`  | gleiche UID darf attachen |
| `1`  | nur Parent/Child          |
| `2`  | nur `CAP_SYS_PTRACE`      |
| `3`  | komplett disabled         |




### Security properties of UDS

UDS selbst

Ein Unix Domain Socket garantiert bereits:

zuverlässige Zustellung (SOCK_STREAM)
Reihenfolge der Bytes
keine Veränderung der Daten durch andere Prozesse
keine Einspeisung in bestehende Verbindungen durch Dritte
Kernel-vermittelte Endpunktkommunikation

Ein lokaler Prozess kann nicht einfach:

Pakete mitschneiden,
Bytes verändern,
Nachrichten injizieren,



### Manually connecting to a socket

nc -U /run/ipc_test/demo.sock


socat - UNIX-CONNECT:/run/ipc_test/demo.sock




SO_PEERCRED

dev@dev:/run$ id partner2
uid=1002(partner2) gid=1003(partner2) groups=1003(partner2),1001(shared_group)


peer pid=106224 uid=1002 gid=1003 sent=b'adfasdfadf\n'

ONly the main GID is transmitted, not supplementary groups.
A check for group membership is probably not the best solution.




## Spoofing

The server runs as user dev.
The IPC is accessible to members of group `shared_group`.
A legitimate client partner_component (uid=1001, gid=1002) periodically sends messages, identifying as Client_1.
Another user of the group partner2 (uid 1002, gid=1003) spoofs the identity of Client_1.

```commandline
----
peer: pid=132208 uid=1001 gid=1002
claimed client: Client_1
----
peer: pid=132211 uid=1002 gid=1003
claimed client: Client_1
----
peer: pid=132208 uid=1001 gid=1002
claimed client: Client_1
----
```

partner2 successfully spoofed the identity Client_1 of partner_component.


Extending the server Code:

```commandline
partner2@dev:/home/dev$ socat - UNIX-CONNECT:/run/ipc_test/demo.sock 
{"method":"uregister", "name":"Client1", "endpoint":"endpoint1"}
ok

```


When the legitimate clients tries to register:

```commandline
Registering Client Client1
Client already registered
```


### SO_PERCREED

The scenario extends the server to evaluate the uid and gid.

```commandline
Listening on /run/ipc_test/demo.sock
Registering Client (134716, 1000, 1000)
----
Listing all connected clients
1000 endpoint1
Sending to destination
data: testing
----

...

Registering Client (134717, 1002, 1003)
----
Listing all connected clients
1000 endpoint1
1002 endpoint1
```

Based on the UIDs the server can distinguish, which client is currently interacting, effectively preventing Spoofing.

Limitation:
The other process can still register the same endpoint, as this is not the focus of this scenario.
By extending the implementation to check for predefined endpoints for certain users the server implementation could be further
hardened.
As an alternative the server could also rely on Trust On First Use, i.e. the first client to register is assumed to be 
the legitimate client.



