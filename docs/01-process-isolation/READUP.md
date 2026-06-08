
# Overview

This lab focuses on unprivileged local process isolation.
Privileged bypass mechanisms such as ptrace, capabilities, packet sniffing,
or explicit FD passing are documented as future work but are out of scope
for the current threat model.

## Possible Extensions



### 1. Process Introspection (unpriviliged same user)

- [ ] `/proc` leakage
  - [ ] environ leakage
  - [ ] cmdline leakage
  - [ ] maps / memory layout
  - [ ] mem access restrictions

### 2. Process Lifecycle / Ressource inheritance

- [ ] fork() / execve()
  - [ ] inherited file descriptors
  - [ ] inherited privileges
  - [ ] FD_CLOEXEC
  - [ ] exec restrictions

### 3. IPC / Networking - intentended rocess interaction

- [ ] SCM_RIGHTS / FD passing
- [ ] UDS trust / routing model
- [ ] local routing abuse
- [ ] process-to-process communication

### 4. Privileged Local Attacker

- [ ] Linux Capabilities
  - [ ] CAP_SYS_PTRACE
  - [ ] CAP_NET_RAW / sniffing
  - [ ] CAP_KILL
  - [ ] CAP_NET_BIND_SERVICE
  - [ ] CAP_SYS_ADMIN

- [ ] ptrace / gdb
- [ ] pidfd_getfd()
- [ ] root-based socket introspection

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


While Linux exposes many resources through file-like interfaces,
it distinguishes between file-backed resources and kernel-managed IPC resources.

File-backed handles:
Security is primarily DAC-based.

If a same-user process can access `/proc/<pid>/fd/<n>`
and DAC permits access to the underlying file, the contents may be readable.


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
- pipes (special case)
- epoll
- eventfd

are working differently.

While the DAC permissions are still a prerequisite to access information 
about the existence of this socket, it is not sufficient to read out the contents.
Kernel IPC handles (e.g. sockets) add another boundary:
Handle ownership.

The process needs to hold a valid reference in its own FD table
The Linux kernel opens a socket object for each TCP socket with a 
- recv queue
- send queue
- TCP State
- Buffers

In order to access this socket from user-space a process needs to possess a valid reference
to the file descriptor pointing to the socket object using the API `recv(fd)`.

```commandline
current process
↓
lookup fd=3 in THIS process
↓
resolve socket object
↓
copy bytes from kernel to user space
```

The kernel owns the socket object.
A process only owns a reference (file descriptor) to it.
Access to the socket requires the process to possess a valid FD in its own FD table.
/proc/<pid>/fd exposes visibility, but does not automatically grant ownership or re-opening of kernel IPC objects.

Summary
> Sockets add another security layer to DAC: Handle Ownership

> Visibility of a kernel object does not imply ownership or usability of that object.



## Further Topics

### File Descriptor Sharing

File descriptors are process-local integers, but multiple processes may reference the same kernel object through shared
entries in the open file table.

Ways to share:
```commandline
fork() inheritance
dup()/dup2()
SCM_RIGHTS
```

Security relevance:

File descriptor leakage may unintentionally grant access to privileged resources.

### Additional /proc leakage vectors

Examples:

/proc/pid/environ

may expose:
```commandline
API keys
tokens
credentials

```

/proc/pid/cmdline

may expose:
```commandline
passwords passed via CLI
debug secrets
```

/proc/pid/maps

shows:

``` 
loaded libraries
memory layout
```

/proc/pid/mem

may enable:
```commandline
memory inspection
```
(subject to ptrace permissions)


### Extending the default local Security 

This section elaborates how to get access to a socket object as a local process.

This is possible using:

1. Kernel privileges by getting `root` or `CAP_SYS_PTRACE`
Then one can do

```commandline
fd dup
pidfd_getfd
ptrace
```

2. Forwarding the FD using SCM_RIGHTS 

3. Sniffing on the network interface getting 'root' or 'CAP_NET_RAW'




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




[//]: # (Outlook: )

[//]: # ()
[//]: # (dev@dev:~$ sudo tcpdump -i any port 8080 -X)

[//]: # ()
[//]: # (```commandline)

[//]: # (12:44:59.739850 lo In IP ubuntu-24.04-server-testing.shared.33348 > ubuntu-24.04-server-testing.shared.http-alt:)

[//]: # (Flags [P.], seq 12:23, ack 1, win 512, options [nop,nop,TS val 3020704275 ecr 3020694273], length 11: HTTP)

[//]: # (0x0000:  4500 003f 8253 4000 4006 347e 0ad3 3721 E..?.S@.@.4~..7!)

[//]: # (0x0010:  0ad3 3721 8244 1f90 babc 8a66 206d 39a1 ..7!.D.....f.m9.)

[//]: # (0x0020:  8018 0200 8419 0000 0101 080a b40c 4a13 ..............J.)

[//]: # (0x0030:  b40c 2301 544f 505f 5345 4352 4554 0a ..#.TOP_SECRET.)

[//]: # (```)
