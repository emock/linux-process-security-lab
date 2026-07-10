# Unix Domain Sockets 

## Overview of useful commands

|                                              |
|----------------------------------------------|
| nc -U /run/ipc_test/demo.sock                |
| socat - UNIX-CONNECT:/run/ipc_test/demo.sock |


## Technical Background

Access to a Unix Domain Socket requires write privileges (010) to the socket object:
`s-w--w----  1 dev  shared_group   0 Jul  3 11:51 demo.sock
`
Neither read nor execute is needed.
Although this does not have a direct security impact, it may indicate an inaccurate understanding 
of UDS or simply reflect the use of a default permission template. 

The socket file descriptor is private to the owning process unless explicitly shared (e.g., SCM_RIGHTS).

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
As elaborated in more detail in lab-01, other local unprivileged processes can not access this resource.
Once a connection has been established, all message routing is performed inside the kernel. 
Consequently, unprivileged user processes cannot observe, inject or modify messages exchanged between peers.

These security guarantees break if a process gains root privileges or any of the following Capabilities:

| Capability            | Description                                                   |
|-----------------------|---------------------------------------------------------------|
| CAP_SYS_PTRACE        | allows strace, gdb attach, ptrace                             |
| CAP_SYS_ADMIN         | root-like                                                     |
| CAP_BPF + CAP_PERFMON | eBPF uprobes/kprobes, syscall tracing, socket instrumentation |
| Ptrace Rules          | cat /proc/sys/kernel/yama/ptrace_scope                        |


To shortly demonstrate, below is a log using `sudo strace -p {PID} -e read,recvmsg,write,sendmsg`

```commandline
dev@dev:/run$ sudo strace -p 106031 -e read,recvmsg,write,sendmsg
strace: Process 106031 attached
write(1, "Received b'SECRET\\n'\n", 21) = 21


```

## Security guarantees of UDS and residual risks

| Property                   | Provided |
|----------------------------|----------|
| Authentication             | optional   |
| Authorization              | no       |
| Connection integrity       | yes      |
| Connection confidentiality | yes      |
| Replay protection          | no       |
| Auditing                   | no       |
| Availability               | no       |


Given the general STRIDE matrix of a data flow and process, UDS evaluates as follows:

|                 | S                     | T          | R    | I          | D    | E    |
|-----------------|-----------------------|------------|------|------------|------|------|
| Data flow       | no                    | yes        | no   | yes        | yes  | no   |
| Process         | yes                   | yes        | yes  | yes        | yes  | yes  |
| Data flow (UDS) | no                    | mitigated  | no   | mitigated  | yes  | no   |
| Process (UDS)   | depends (SO_PEERCRED) | yes        | yes  | yes        | yes  | yes  |

Regarding Data flow threats, both tampering and information disclosure have already been described in the previous section.
The remaining threat of DoS is applicable, as UDS does not offer any sender side limits configuration (as opposed to DBUS).
This needs to be addressed by the application.
For UDS Process threats, we will investigate Spoofing.
The remaining threats are stack-agnostic and therefore out of scope. 

## Spoofing of Sender Process

We set up a server, running as user dev, offering the methods uregister, register, usend, send.
Both uregister and usend are viable to Spoofing, as the application evaluates a client-provided ID to assess the sender-identity. 
The IPC is accessible to members of group `shared_group`.
A legitimate client partner_component (uid=1001, gid=1002) periodically sends messages, identifying as `Client_1`.
Another user of the group partner2 (uid 1002, gid=1003) spoofs the identity of `Client_1`.

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

The server prints the peer credentials to showcase the Spoofing use-case.
User partner2 (uid=1002) successfully spoofed the identity Client_1 of partner_component.


Observing the same issue with the offered methods uregister:

```commandline
partner2@dev:/home/dev$ socat - UNIX-CONNECT:/run/ipc_test/demo.sock 
{"method":"uregister", "name":"Client1", "endpoint":"endpoint1"}
ok

```

When the legitimate clients partner_component tries to call the `register` method it receives an error message:

```commandline
Registering Client Client1
Client already registered
```


### SO_PERCREED

Linux exposes the peer credentials (PID, UID, GID) of a connected process via SO_PEERCRED per connection.


```commandline
dev@dev:/run$ id partner2
uid=1002(partner2) gid=1003(partner2) groups=1003(partner2),1001(shared_group)

peer pid=106224 uid=1002 gid=1003 sent=b'adfasdfadf\n'


```
Note that  only the main GID is transmitted, not supplementary groups.
Depending on the scenario a check on group membership might yield unexpected results.

In contrast to the insecure implementation which was susceptible to Spoofing, the server implements 
two additional methods register and send, which rely on the SO_PEERCRED for authenticating the attached clients.
These credentials are obtained from the kernel rather than supplied by the client application thereby preventing application-level spoofing.

> Security guarantees apply to the transport only.
While UDS provides transport confidentiality and integrity and may support peer authentication (SO_PEERCRED), these
guarantees can be *negated by insecure application protocols*. 
>> For example, deriving the sender identity from client-controlled message fields instead of kernel-provided peer 
>> credentials reintroduces application-level spoofing.


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

Limitation:
The other process can still register the same endpoint, as this is not the focus of this scenario.
By extending the implementation to check for predefined endpoints for certain users the server implementation could be further
hardened.
As an alternative the server could also rely on Trust On First Use, i.e. the first client to register is assumed to be 
the legitimate client.








## Open Points and Future Work

SCM_RIGHTS has not been considered so far but could be an interesting extension for future work to demonstrate how 
file handles can be passed from a parent to a child process without further access checks.

Implementing request authorization is an interesting learning field, however is independent of UDS and needs to be 
handled by the application. 

Extending the `client <--> server` implementation to an IPC Broker `client <--> server <--> client` could demonstrate the 
common pitfalls (S,T,I,E) of such a custom design.