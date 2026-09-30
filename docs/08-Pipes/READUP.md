

## Technical Background


### Overview

| Syntax                        | Bedeutung                           |
|-------------------------------|-------------------------------------|
| `cmd > file`                  | FD 1 → Datei, truncate              |
| `cmd >> file`                 | FD 1 → Datei, append                |
| `cmd < file`                  | FD 0 ← Datei                        |
| `grep hello <<< "hello world"`  | FD 0 ← String                       |
| `cmd 2> file`                 | FD 2 → Datei                        |
| `cmd 2>&1`                    | FD 2 → aktuelles Ziel von FD 1      |
| `cmd >/dev/null 2>&1`         | FD 1 + FD 2 → `/dev/null`           |
| `A \| B`                      | A:FD 1 → Pipe → B:FD 0              |
| `A \|& B`                     | A:FD 1 **und FD 2** → Pipe → B:FD 0 |

#### TL;DR;
> The operator < connects a File Descriptor with the input source of a process

> The operator > connects a File Descriptor with the output source of a process

> Both < and > connect a process with a file


> The operator | connects the output source of process1 to a pipe **and**
> connects the input source of process2 to the same pipe

> | connects two processes using a Kernel-Pipe

## File Operators

When using `echo hello > file.txt` the underlying file handles of the shell are hard to observe, as
`echo` immediately closes the file handle after writing.
Use `pgrep sleep` to obtain the PID.

We know from lab-01 that 


TODO ich kapier das /dev/pts/0 nicht

```commandline
bash
 │
 ├── fd 0 stdin  ──────> /dev/pts/0
 ├── fd 1 stdout ──────> /dev/pts/0
 └── fd 2 stderr ──────> /dev/pts/0
```

each process has three file handles by default
fd 0 for input
fd 1 for output
fd 2 for error messages


`sleep 1000 < input.log`

```commandline
dev@dev:~$ ls -l /proc/186674/fd
total 0
lr-x------ 1 dev dev 64 Sep 7 08:12 0 -> /home/dev/input.log
lrwx------ 1 dev dev 64 Sep 7 08:12 1 -> /dev/pts/1
lrwx------ 1 dev dev 64 Sep 7 08:12 2 -> /dev/pts/1
```



`sleep 1000 > output.log` to observe the underlying mechanics.

```commandline
dev@dev:~$ ls -l /proc/179356/fd
total 0
lrwx------ 1 dev dev 64 Sep  4 13:17 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  4 13:17 1 -> /home/dev/output.log
lrwx------ 1 dev dev 64 Sep  4 13:17 2 -> /dev/pts/1

```

The standard output has been redirected to the file instead of the default terminal output.

If no number is supplied the shell defaults to FD 1.
This would be equivalent to using 
`sleep 1000 1> output.log`



`sleep 1000 > output.log 2>error.log` redirects error messages to a dedicated error.log file.
The file handles are adapted accordingly.

```commandline
2> error.log
│ │
│ └── redirect
│
└──── FD 2
```


```commandline
dev@dev:~$ ls -l /proc/179922/fd
total 0
lrwx------ 1 dev dev 64 Sep  7 07:12 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  7 07:12 1 -> /home/dev/output.log
l-wx------ 1 dev dev 64 Sep  7 07:12 2 -> /home/dev/error.log
```



`sleep 1000 > output.log 2>&1`

```commandline
dev@dev:~$ ls -l /proc/186580/fd
total 0
lrwx------ 1 dev dev 64 Sep  7 07:32 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  7 07:32 1 -> /home/dev/output.log
l-wx------ 1 dev dev 64 Sep  7 07:32 2 -> /home/dev/output.log
```


```commandline
2 > &1
│   │
│   └── Ziel von FD 1
│
└────── FD 2
```


If we ommit the `&` as in `sleep 1000 > output.log 2>1`, this results in bash interpreting the `1` as a file name

```commandline
dev@dev:~$ ls -l /proc/186593/fd
total 0
lrwx------ 1 dev dev 64 Sep  7 07:34 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  7 07:34 1 -> /home/dev/output.log
l-wx------ 1 dev dev 64 Sep  7 07:34 2 -> /home/dev/1
```




### Bash processing

Redirections for a command are processed from left to right.

`command > everything.log 2>&1`

First both FD 1 and FD 2 default to Terminal

```commandline
FD 1 ──> Terminal
FD 2 ──> Terminal
```

After parsing `> everything.log` this changes to:

```commandline
FD 1 ──> everything.log
FD 2 ──> Terminal
```

After parsing `2>&1` this changes to:

```commandline
FD 1 ──┐
       ├──> everything.log
FD 2 ──┘
```

This is different from `command 2>&1 > everything.log`

In this case at first `2>&1` the error stream is redirected to the output stream, which is the terminal

```commandline
FD 1 ──> Terminal
FD 2 ──> Terminal
```

After parsing `> everything.log` the output stream is changed to the output file

```commandline
FD 1 ──> everything.log
FD 2 ──> Terminal
```





## Pipes
A pipe connects a producer to a consumer using the syntax
`producer | consumer`

```commandline
producer                         consumer
FD 1 ────────> [ PIPE ] ────────> FD 0
```

As can be seen only FD1 of cmd1 and FD0 of cmd2 are affected.
```commandline
 cmd1                              cmd2

 FD 0                              FD 0
                                    ▲
 FD 1 ────────> PIPE ──────────────┘

 FD 2 ────────> Terminal
```


`sleep 1000 | sleep 1000`

results in two PIDs for `sleep`

```commandline
dev@dev:~$ ls -l /proc/186631/fd
total 0
lrwx------ 1 dev dev 64 Sep  7 07:48 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  7 07:48 1 -> 'pipe:[1027611]'
lrwx------ 1 dev dev 64 Sep  7 07:48 2 -> /dev/pts/1
dev@dev:~$ ls -l /proc/186632/fd
total 0
lr-x------ 1 dev dev 64 Sep  7 07:48 0 -> 'pipe:[1027611]'
lrwx------ 1 dev dev 64 Sep  7 07:48 1 -> /dev/pts/1
lrwx------ 1 dev dev 64 Sep  7 07:48 2 -> /dev/pts/1

```
This demonstrates the inner workings of pipes: The output of one process is redirected to the input 
of another process.

By using `cmd1 |& cmd2` both the output and error stream can be redirected to the following process.

Using `sleep 1000 |& sleep 1000`

```commandline
ev@dev:~$ ls -l /proc/186734/fd
total 0
lrwx------ 1 dev dev 64 Sep  7 08:34 0 -> /dev/pts/1
l-wx------ 1 dev dev 64 Sep  7 08:34 1 -> 'pipe:[1028496]'
l-wx------ 1 dev dev 64 Sep  7 08:34 2 -> 'pipe:[1028496]'
dev@dev:~$ ls -l /proc/186735/fd
total 0
lr-x------ 1 dev dev 64 Sep  7 08:34 0 -> 'pipe:[1028496]'
lrwx------ 1 dev dev 64 Sep  7 08:34 1 -> /dev/pts/1
lrwx------ 1 dev dev 64 Sep  7 08:34 2 -> /dev/pts/1

```

```commandline
cmd1

FD 1 ─────┐
          │
          ├────> PIPE ─────> cmd2:FD0
          │
FD 2 ─────┘
```

```commandline
                  ┌── FD1 ──┐
sleep ───────────────┤         ├──> PIPE ──> sleep
                  └── FD2 ──┘
```






### Example with grep

```commandline
grep root < /etc/passwd

file ───────────────> grep:FD0
```

```commandline
cat /etc/passwd | grep root

cat:FD1 ──> PIPE ──> grep:FD0

```

In the first case grep reads directly from a file, while in the second case it reads from the 
read-end of a pipe.


### Learnings

> The operator < connects a File Descriptor with the input source of a process

> The operator > connects a File Descriptor with the output source of a process

> Both < and > connect a process with a file


> The operator | connects the output source of process1 to a pipe **and**
> connects the input source of process2 to the same pipe

> | connects two processes using a Kernel-Pipe


## Names Pipes

Using mkfifo we can create a named pipe in order to connect two processes, which are independently started 
but share a need to exchange information with each other.


The input is received and queued into a first in first out structure. 

```commandline
Process A (Writer)                    Named Pipe / FIFO                    Process B (Reader)
+------------------+                 /tmp/demo.fifo                        +------------------+
|                  |                                                       |                  |
| write("AAA")     | ----->     +------------------+                       |                  |
| write("BBB")     | ----->     | A|A|A|B|B|B|C|C|C| -----> read(1) ------>| receives "A"     |
| write("CCC")     | ----->     +------------------+                       |                  |
|                  |                  FIFO                                 |                  |
+------------------+                                                       +------------------+

```

Note that the FIFO stores the bytes in order but does not ensure that a read retrieves exactly the 
defined message but rather a number of bytes.
For retrieving defined messages an application level protocol needs to be defined, e.g. in the simplest case
using a delimiter or a prefixed length field.

```commandline
dev@dev:~$ mkfifo /tmp/demo.fifo
dev@dev:/tmp$ ls -l demo.fifo 
prw-rw-r-- 1 dev dev 0 Sep  7 11:23 demo.fifo
```

DAC can be used to secure a named pipe and the insight from chapter 02-file-permissions apply accordingly.

Terminal 1:
```commandline
dev@dev:/tmp$ echo "1" > demo.fifo 

```

Terminal 2:


```commandline
dev@dev:/tmp$ echo "2" > demo.fifo 

```

Both Terminal 1 and 2 seem stuck until the content from the pipe is retrieved by a receiver in this setup.

Terminal 3:
```commandline
dev@dev:/tmp$ cat demo.fifo
2
1
```

We encounter the same issue when implementing this in code - the program writes to the pipe but then is stuck
until a consumer retrieves the information from the pipe.

Once data has been written to a pipe, another process cannot modify the bytes already buffered in the pipe. File
descriptors are process-local and cannot simply be accessed by another unprivileged process. However, with a named pipe,
insufficient filesystem permissions may allow another process to open the FIFO independently and inject or consume data.

We will elaborate these scenarios in the following labs.

### Lab 01 Spoofing

Apparently, as the content of a FIFO is just a sequence of bytes, a consumer process cannot verify 
"who" has provided this content.
Also if authentication information would be provided, e.g. as part of a message structure, this is easily
forgeable.
Concluding, the only effective security mechanism is by using DAC and restricting the amount of senders 
in the first place.

Spoofing will be demonstrated in the following.
If a malicious sender has access to a pipe Spoofing is possible.
This can be achieved by submitting a message to the pipe:

```commandline
dev@dev:/tmp$ echo "Attacker:hello from Provider" > demo.fifo 
```


```commandline
/home/dev/.virtualenvs/linux-process-security-lab/bin/python /home/dev/linux-process-security-lab/labs/08-Pipes/consumer.py 
hello from Provider
hello from Provider
Attacker:hello from Provider
```

### Lab 02 Information Disclosure

If a malicious entity can retrieve the content before the legitimate consumer, information disclosure is possible.


```commandline
dev@dev:/tmp$ cat demo.fifo 
hello from Providerdev@dev:/tmp$ 
```



## Security Properties

Given the general STRIDE matrix of a data flow and process,
a named pipe for an unprivileged local attacker evaluates as follows:

|                  | S   | T         | R     | I     | D    | E    |
|------------------|-----|-----------|-------|-------|------|------|
| Data flow        | no  | yes       | no    | yes   | yes  | no   |
| Data flow (PIPE) | no  | mitigated | no    | yes   | yes  | no   |
| Process          | yes | yes       | yes   | yes   | yes  | yes  |
| Process (PIPE)   | yes | yes       | yes   | yes   | yes  | yes  |

If the attacker is privileged, the mititgations are no longer applicable. 

