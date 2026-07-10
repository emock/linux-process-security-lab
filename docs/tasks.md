
# General

- [ ] common.py is duplicated per directory - this should only be a single
  source

# lab-01-process-isolation

- [ ] Add Capabilities
  
  - [ ] CAP_NET_RAW / sniffing
  - [ ] CAP_SYS_PTRACE: allows strace, gdb attach, ptrace
  - [ ] CAP_SYS_ADMIN: root-like
  - [ ] CAP_BPF + CAP_PERFMON: eBPF uprobes/kprobes, syscall tracing, socket instrumentation
  - [ ]  Same-UID + ptrace-Regeln:
  - Check using `cat /proc/sys/kernel/yama/ptrace_scope`

| Wert | Bedeutung                 |
| ---- | ------------------------- |
| `0`  | gleiche UID darf attachen |
| `1`  | nur Parent/Child          |
| `2`  | nur `CAP_SYS_PTRACE`      |
| `3`  | komplett disabled         |

- [ ] ptrace / gdb
- [ ] pidfd_getfd()
- [ ] SCM_RIGHTS / FD passing
- [x] UDS trust/routing model



    
# lab-05-dbus
- [ ] Implement signals
- 
- [ ] Scenario eavesdropping: Run Service as dev, listen with shared_group user
- [ ] Receive Rules <allow receive_sender="..."/> <allow receive_interface="..."/> <allow receive_member="..."/>

  


# Other

- [ ] TCPDUMP!
- [ ] Add Network Attacker