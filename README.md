# Lab Overview

## 01 – Process Isolation

**Concept**

How Linux isolates process memory and resources.

**Demonstrates**

- Process memory isolation
- `/proc/<pid>` access limitations
- Why one process cannot read another process's memory

**Security implication**

Process isolation prevents arbitrary tampering between processes.

---

## 02 – File Permissions (DAC)

**Concept**

Linux Discretionary Access Control (DAC).

**Demonstrates**

- File ownership
- `chmod`, `chown`
- How processes access shared files

**Security implication**

Improper file permissions allow processes to tamper with each other's data.

| Resource              | DAC Modell      |
| --------------------- | --------------- |
| Files                 | ✔ vollständig   |
| Directories           | ✔ vollständig   |
| Unix sockets          | ✔ vollständig   |
| Named pipes           | ✔ vollständig   |
| Shared memory (POSIX) | ✔ vollständig   |
| Shared memory (SysV)  | ✔ ähnlich       |
| Processes             | ✔ teilweise     |
| Signals               | ✔ teilweise     |
| /proc                 | ✔ teilweise     |
| TCP sockets           | ✖ eher indirekt |

---

## 03 – TCP Socket Ownership

**Concept**

TCP sockets are owned by processes via file descriptors.

**Demonstrates**

- Server-client communication
- Attacker process attempting TCP stream injection
- Kernel enforcement of socket ownership

**Security implication**

Processes cannot inject data into existing TCP streams owned by other processes.

---

## 04 – Unix Domain Sockets

**Concept**

Local IPC through filesystem-based sockets.

**Demonstrates**

- Creation of Unix sockets
- File-based access control
- Process communication boundaries

**Security implication**

Unix socket permissions control which processes can access local services.

---

## 05 – Signals Between Processes

**Concept**

Process signaling and control.

**Demonstrates**

- `SIGTERM`
- `SIGKILL`
- Same-UID signal behavior

**Security implication**

Processes with the same UID can affect availability of other processes.

---

## 06 – `/proc` Filesystem

**Concept**

Kernel exposure of process metadata.

**Demonstrates**

- `/proc/<pid>/fd`
- `/proc/net/tcp`
- Process introspection

**Security implication**

Attackers can learn system state through `/proc`, but cannot directly control resources.

---

## 07 – Shared Memory

**Concept**

Explicit inter-process memory sharing.

**Demonstrates**

- Python shared memory
- Controlled IPC channels

**Security implication**

Shared memory breaks isolation intentionally and must be used carefully.

---

## 08 – Named Pipes (FIFO)

**Concept**

Simple IPC using filesystem pipes.

**Demonstrates**

- `mkfifo`
- Inter-process communication via filesystem

**Security implication**

Improper permissions allow unintended processes to interact.

---

## 09 – Privilege Boundaries

**Concept**

User separation and privilege restrictions.

**Demonstrates**

- Running programs as different users
- `sudo -u`
- Permission boundaries

**Security implication**

Least privilege limits the damage of compromised processes.

---

## 10 – Network Attack Models

**Concept**

Understanding attacker capabilities in network environments.

**Demonstrates**

- Remote attacker
- Local attacker
- Network MITM attacker

**Security implication**

Different attacker models require different security controls.

---

# Learning Goals

After completing these labs you should understand:

- Linux **process isolation**
- File descriptor and **socket ownership**
- **Discretionary access control**
- Local **inter-process communication**
- How Linux enforces **privilege boundaries**
- Practical limits of **local attackers**

---

# Future Extensions

Possible advanced labs:

- Linux capabilities
- Network namespaces
- Containers and cgroups
- AppArmor / SELinux policies
- Seccomp syscall filtering
- Packet injection and MITM

---

# License

Educational use.