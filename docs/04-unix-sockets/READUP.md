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

### Manually connecting to a socket

nc -U /run/ipc_test/demo.sock


socat - UNIX-CONNECT:/run/ipc_test/demo.sock




PEERCRED

dev@dev:/run$ id partner2
uid=1002(partner2) gid=1003(partner2) groups=1003(partner2),1001(shared_group)


peer pid=106224 uid=1002 gid=1003 sent=b'adfasdfadf\n'

ONly the main GID is transmitted, not supplementary groups.
A check for group membership is probably not the best solution.




Spoofing


```commandline
peer: pid=106355 uid=1000 gid=1000
claimed client: Client_1
----
peer: pid=106356 uid=1000 gid=1000
claimed client: Client_1
----
peer: pid=106355 uid=1000 gid=1000
claimed client: Client_1

```
