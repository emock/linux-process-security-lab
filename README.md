# Lab Overview

These labs demonstrate several linux fondamentals with a focus on security.
We will cover topics such as how DAC applies for different resources as well as
additional security mechanisms which might be available for the corresponding interface, such as
DBUS send policy or SO_PEERCRED for UDS.

Mandatory Access Control (MAC) is out of scope for this lab, as this a 
broad and complex topic on its own.

The following provides an overview of the labs and correlation to DAC:

| Lab | Resource              | DAC relevance | Other mechanisms |
|-----|-----------------------|---------------|------------------|
| 01  | Processes (/proc)     | Partial       | ptrace checks    |
| 02  | Files                 | Primary       | ACLs             |
| 03  | Directories           | Primary       | ACLs             |
| 04  | Named pipes           | Primary       | none             |
| 05  | Unix sockets          | Primary       | SO_PEERCRED      |
| 06  | DBUS                  | Indirect      | Bus policy       |
| 07  | Network sockets (UDP) | None          | capabilities     |

---

# Future Extensions

Possible advanced labs:

- Linux capabilities
- Network namespaces
- Containers and cgroups
- AppArmor / SELinux policies
- Seccomp syscall filtering
- Packet injection and MITM
- Signals
- Shared memory (POSIX) 
- Shared memory (SysV)  

[//]: # ()
[//]: # (## 05 – Signals Between Processes)

[//]: # ()
[//]: # (**Concept**)

[//]: # ()
[//]: # (Process signaling and control.)

[//]: # ()
[//]: # (**Demonstrates**)

[//]: # ()
[//]: # (- `SIGTERM`)

[//]: # (- `SIGKILL`)

[//]: # (- Same-UID signal behavior)

[//]: # ()
[//]: # (**Security implication**)

[//]: # ()
[//]: # (Processes with the same UID can affect availability of other processes.)
