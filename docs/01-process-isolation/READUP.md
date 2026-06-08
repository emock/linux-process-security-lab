
# Overview
Local attacker on same host

✓ Kann anderer User /proc lesen?
✓ Kann same-user /proc lesen?
✓ Kann er fremde FDs sehen?
✓ Kann er fremde Dateien lesen?
✓ Kann er fremde Socket Streams lesen?
✓ Was ändert root?
✓ Was ändern Capabilities?



- UID/GID
- DAC
- /proc visibility
- FD ownership
   - file-backed FD
   - socket-backed FD
  
- ptrace
- signals
- process execution
- root/capability bypasses

## Technical Background

Each process stores process information in the path 
`/proc/{pid}/`

```commandline
dev@dev:/proc/87952$ ls -al
total 0
dr-xr-xr-x   9 dev  dev  0 Jun  2 08:59 .
dr-xr-xr-x 210 root root 0 Mar 12 15:02 ..
-r--r--r--   1 dev  dev  0 Jun  2 09:11 arch_status
dr-xr-xr-x   2 dev  dev  0 Jun  2 09:02 attr
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 autogroup
-r--------   1 dev  dev  0 Jun  2 09:11 auxv
-r--r--r--   1 dev  dev  0 Jun  2 09:11 cgroup
--w-------   1 dev  dev  0 Jun  2 09:11 clear_refs
-r--r--r--   1 dev  dev  0 Jun  2 09:11 cmdline
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 comm
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 coredump_filter
-r--r--r--   1 dev  dev  0 Jun  2 09:11 cpu_resctrl_groups
-r--r--r--   1 dev  dev  0 Jun  2 09:11 cpuset
lrwxrwxrwx   1 dev  dev  0 Jun  2 09:11 cwd -> /tmp
-r--------   1 dev  dev  0 Jun  2 09:11 environ
lrwxrwxrwx   1 dev  dev  0 Jun  2 09:11 exe -> /usr/bin/python3.12
dr-x------   2 dev  dev  5 Jun  2 08:59 fd
dr-xr-xr-x   2 dev  dev  0 Jun  2 09:11 fdinfo
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 gid_map
-r--------   1 dev  dev  0 Jun  2 09:11 io
-r--------   1 dev  dev  0 Jun  2 09:11 ksm_merging_pages
-r--------   1 dev  dev  0 Jun  2 09:11 ksm_stat
-r--r--r--   1 dev  dev  0 Jun  2 09:11 latency
-r--r--r--   1 dev  dev  0 Jun  2 09:11 limits
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 loginuid
dr-x------   2 dev  dev  0 Jun  2 09:11 map_files
-r--r--r--   1 dev  dev  0 Jun  2 09:11 maps
-rw-------   1 dev  dev  0 Jun  2 09:11 mem
-r--r--r--   1 dev  dev  0 Jun  2 09:11 mountinfo
-r--r--r--   1 dev  dev  0 Jun  2 09:11 mounts
-r--------   1 dev  dev  0 Jun  2 09:11 mountstats
dr-xr-xr-x  55 dev  dev  0 Jun  2 09:11 net
dr-x--x--x   2 dev  dev  0 Jun  2 09:11 ns
-r--r--r--   1 dev  dev  0 Jun  2 09:11 numa_maps
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 oom_adj
-r--r--r--   1 dev  dev  0 Jun  2 09:11 oom_score
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 oom_score_adj
-r--------   1 dev  dev  0 Jun  2 09:11 pagemap
-r--------   1 dev  dev  0 Jun  2 09:11 patch_state
-r--------   1 dev  dev  0 Jun  2 09:11 personality
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 projid_map
lrwxrwxrwx   1 dev  dev  0 Jun  2 09:11 root -> /
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 sched
-r--r--r--   1 dev  dev  0 Jun  2 09:11 schedstat
-r--r--r--   1 dev  dev  0 Jun  2 09:11 sessionid
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 setgroups
-r--r--r--   1 dev  dev  0 Jun  2 09:11 smaps
-r--r--r--   1 dev  dev  0 Jun  2 09:11 smaps_rollup
-r--------   1 dev  dev  0 Jun  2 09:11 stack
-r--r--r--   1 dev  dev  0 Jun  2 09:02 stat
-r--r--r--   1 dev  dev  0 Jun  2 09:11 statm
-r--r--r--   1 dev  dev  0 Jun  2 09:11 status
-r--------   1 dev  dev  0 Jun  2 09:11 syscall
dr-xr-xr-x   3 dev  dev  0 Jun  2 09:11 task
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 timens_offsets
-r--r--r--   1 dev  dev  0 Jun  2 09:11 timers
-rw-rw-rw-   1 dev  dev  0 Jun  2 09:11 timerslack_ns
-rw-r--r--   1 dev  dev  0 Jun  2 09:11 uid_map
-r--r--r--   1 dev  dev  0 Jun  2 09:11 wchan

```

The above shows an extract from process fd_visibility.

We can see in directory /proc/{PID}/fd the currently used File Descriptors which 
the process is using.

```commandline
dev@dev:/proc/87952/fd$ ls -al
total 0
dr-x------ 2 dev dev  5 Jun  2 08:59 .
dr-xr-xr-x 9 dev dev  0 Jun  2 08:59 ..
lrwx------ 1 dev dev 64 Jun  2 08:59 0 -> /dev/pts/4
lrwx------ 1 dev dev 64 Jun  2 08:59 1 -> /dev/pts/4
lrwx------ 1 dev dev 64 Jun  2 08:59 2 -> /dev/pts/4
lr-x------ 1 dev dev 64 Jun  2 08:59 3 -> /tmp/secret
lrwx------ 1 dev dev 64 Jun  2 08:59 4 -> 'socket:[756699]'
```
While the entries 0,1,2 are standard entries and point to STDIN, STDOUT, STDERR,
consecutive entries point to used files and resources, such as a file or a socket.

Access to /proc/{pid}/fd is governed by procfs permissions and Linux process access checks. 
Same-user access is typically allowed, while other users are blocked unless 
elevated privileges are present (e.g. root or ptrace-like permissions).

[//]: # (root kann drüber)
[//]: # (ptrace restrictions &#40;Yama&#41; spielen mit rein)
[//]: # (Distribution-Hardening kann Verhalten ändern)


While there is the common principle `Everything in Linux is a file`
Linux does distinguish between these handles:
File backend handles and kernel-managed IPC handles.

For File backed handles only the DAC permissions of the process are evaluated and relevant.


```commandline

open("/tmp/x")
↓
DAC check
↓
Kernel returns fd=3 
↓
Handle-basiert
```

File-backed handles:
- normal files
- deleted files
- tmpfs files
- device files
- FIFOs
- some memfd/shared-memory-backed files
- stdio redirection

This can be risky if a second process from the same user tries to access 
the /proc entries of another PID.
This matches with the Linux Security view that same-user processes are within the same Trust Boundary.

>Note: This behavior may be undesirable in hardened environments and can be restricted further 
through MAC systems or procfs hardening.

Kernel-managed IPC handles, such as

- TCP sockets
- UDP sockets
- UDS
- pipes
- epoll
- eventfd

are working differently.

While the DAC permissions are still a prerequisite to access information 
about the existence of this socket, it is not sufficient to read out the contents.

The process needs to proof ownership of the "File Handle".
The Linux kernel opens a socket object for each TCP socket with a 
- recv queue
- send queue
- TCP State
- Buffers

In order to access this socket from user-space a process needs to proof ownership of the 
file descriptor pointing to the socket object using the API `recv(fd)`.

```commandline
current process
↓
lookup fd=3 in THIS process
↓
resolve socket object
↓
copy bytes from kernel to user space
```


Specifically, as e.g. TCP Sockets are defined by a unique Tuple 
(IP_DEST, IP_SRC, PORT_DEST, PORT_SRC) and each port can only be used
by a single process, this makes a file handle to a TCP socket exclusively.
So no other process than the creating process can access the TCP socket.

Summary
> Sockets add another security layer to DAC: Handle Ownership



Bypass:

Das geht mit:

SCM_RIGHTS (bewusstes FD sharing)
pidfd_getfd() (privilegiert)
ptrace-artige Mechanismen



DAC: ja (gleicher User)

"PID 86647 besitzt ein Auto mit Fahrgestellnummer 752737"

Linux hat hier eine zweite Schicht neben DAC:

Object Capability / Handle Ownership

Das Prinzip:

Nur wer einen gültigen Handle (FD) besitzt, darf die Ressource benutzen.

Bei Files:

open("/tmp/x")
↓
DAC check
↓
Kernel gibt fd=3 zurück
↓
ab jetzt Handle-basiert

Nach dem open() ist DAC weitgehend vorbei.

Ungesichert gegenüber wem?

Ungesichert heißt:

Jeder, der die Pakete beobachten kann.

Nicht:

Jeder lokale Prozess.

Die beiden Modelle:

Prozessmodell
local process
↓
braucht FD ownership

Netzwerkmodell
packet observer
↓
braucht network visibility

Da ist der große Unterschied.




Wie würdest du wirklich „auf 752737 hören“?

Es gibt nur wenige Wege:

1. Kernel privileges

Root oder:

CAP_SYS_PTRACE

Dann:

fd dup
pidfd_getfd
ptrace

möglich.

2. FD weiterreichen

Victim:

SCM_RIGHTS

Dann bekommst du echtes FD:

attacker fd 5
-> socket 752737

Jetzt klappt:

recv(5)

3. Sniffing

Nicht Socket nehmen.

Sondern:

network interface

abhören.

Mit:

CAP_NET_RAW
root

Dann siehst du:

TOP_SECRET

ohne FD.





## Results Reading out File Descriptors

Our process reports the following file handles:
```commandline
Opening Socket to 127.0.0.1
0 -> /dev/pts/4
1 -> /dev/pts/4
2 -> /dev/pts/4
3 -> /tmp/secret
4 -> socket:[756699]
5 -> already closed
```

When starting the attacker.py as the same user:

```commandline
dev@dev:/tmp$ python3 attacker.py 87952
Attacker pid: 87953
Opening FD of foreign Process 87952
0 -> /dev/pts/4
1 -> /dev/pts/4
2 -> /dev/pts/4
3 -> /tmp/secret
SUPER_SECRET

4 -> socket:[756699]
Exception: FD 4 : No such file or directory
```

We can observe that the same user can access /proc/{PID}/fd and resolve the 
symlinks.
Additionally, when the symlink points to a file and the DAC permissions are 
set accordingly, the contents can be read out.
This is different with the TCP socket.
Here we encounter a FileException.

TODO Why?

It is not possible for another user to access the File Descriptors of a process:

```commandline
dev@dev:/tmp$ sudo -u partner2 python3 /tmp/attacker.py 87952
Attacker pid: 87972
Opening FD of foreign Process 87952
Permission Denied
```

> Summary
>> Processes from the same user can read out File Descriptors of same-user processes. <br>
>> Processes from other users cannot access the File Descriptors.










Outlook: 

dev@dev:~$ sudo tcpdump -i any port 8080 -X

```commandline
12:44:59.739850 lo In IP ubuntu-24.04-server-testing.shared.33348 > ubuntu-24.04-server-testing.shared.http-alt:
Flags [P.], seq 12:23, ack 1, win 512, options [nop,nop,TS val 3020704275 ecr 3020694273], length 11: HTTP
0x0000:  4500 003f 8253 4000 4006 347e 0ad3 3721 E..?.S@.@.4~..7!
0x0010:  0ad3 3721 8244 1f90 babc 8a66 206d 39a1 ..7!.D.....f.m9.
0x0020:  8018 0200 8419 0000 0101 080a b40c 4a13 ..............J.
0x0030:  b40c 2301 544f 505f 5345 4352 4554 0a ..#.TOP_SECRET.
```
