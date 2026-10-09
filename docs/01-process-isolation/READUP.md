
# Overview

This lab focuses on unprivileged local process isolation.
Privileged bypass mechanisms such as ptrace, capabilities, packet sniffing,
or explicit FD passing are documented as future work but are out of scope
for the current threat model.


## Technical Background

Each process stores process information in the path 
`/proc/{pid}/`.
The output has been redacted.

```commandline
/proc/<pid>/
├── attr/ — Linux Security Module attributes, including process security contexts.
├── fd/  — Open file descriptors
├── fdinfo/ — File descriptor metadata
├── cmdline — Command-line arguments
├── environ — Process environment
├── maps — Memory mappings
├── mem — Process memory access
├── status — Process identity, capabilities, security state
├── syscall — Current system call and registers
└── cgroup — Control group membership
```

In this lab we will focus on the file handles as these are the "gateways" to accessing a ressource, such as
a file, a socket or a pipe. These in turn we want to investigate later, how these can be protected using
standard security mechanisms.

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

File-backed handles, such as normal files, deleted files, tmpfs files, device files, FIFOs, some memfd/shared-memory-backed files
stdio redirection may be accessible for a process running under the same user.
This matches with the Linux Security view that same-user processes are within the same Trust Boundary.
>Note: This behavior may be undesirable in hardened environments and can be restricted further 
through MAC systems or procfs hardening.




Kernel-managed IPC resources, such as TCP/UDP sockets, Unix domain sockets, pipes, `eventfd`, and `epoll`, behave
differently from regular files.

Unlike regular files, existing sockets cannot generally be reopened through a filesystem path.

To access an existing socket, a process must hold a valid file descriptor referencing the socket object in its own file
descriptor table.

The Linux kernel manages the underlying socket object, including its receive and send buffers and protocol state. When a
process calls `recv(fd)`, the kernel resolves the descriptor in the calling process's FD table and accesses the
corresponding socket.

Visibility through `/proc/<pid>/fd` does not automatically provide access to the underlying socket.

```commandline
current process
↓
lookup fd=3 in THIS process
↓
resolve socket object
↓
copy bytes from kernel to user space
```


**Summary**

> Access to an existing socket requires a valid file descriptor referencing that socket.

> Visibility of a kernel object does not imply the ability to access or use it.



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

> **Summary** <br>
> Processes from the same user can read out File Descriptors of same-user processes. <br> 
> Processes from other users cannot access the File Descriptors.
