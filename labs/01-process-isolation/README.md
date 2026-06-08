

# Scenario 1: Reading out File Descriptors 

1. Run script ./setup: This installs the .py files in /tmp
2. Run nc -l 127.0.0.1 8080
3. Run /tmp/fd_visibility: the program opens a file handle to a file, 
keeps it open and then sends data to the TCP socket.
4. Wait until the script starts sending data to the nc listener
5. Run `python3 /tmp/attacker.py "$victim_pid"` within this time window as user dev
6. Run `sudo -u partner2 python3 /tmp/attacker.py "$victim_pid"` within this time window























13. 
14. 
15. FD visibility + TCP socket ownership
(warum HTTP nicht mitlesbar ist)
2. /proc leakage
environ
cmdline
fd
3. ptrace
(same UID attacker!)
4. process execution
(eure Shell-Frage)
5. Capabilities
dann als Verstärker:
CAP_NET_RAW
CAP_SYS_PTRACE
CAP_KILL
CAP_NET_BIND_SERVICE

Ja — jetzt wird’s spannend, weil du vom „Linux Permission Modell“ in die **eigentliche Prozess-Isolation** kommst. Und
genau deine Frage zu TCP ist der Kern:

> Warum kann ein lokaler Prozess nicht einfach meinen HTTP-Traffic lesen oder manipulieren?

Das ist letztlich eine Folge von **FD Ownership + Kernel Mediation**.

Ich würde die Themen für dein Security-Modell jetzt so priorisieren:

```text
1. Process Identity
   - UID/GID
   - DAC
   - Capabilities (später)

2. Process Isolation
   - File Descriptor Ownership
   - Process Visibility (/proc)
   - TCP Socket Ownership
   - Localhost trust boundary

3. Process Introspection
   - environ leakage
   - cmdline leakage
   - ptrace

4. Process Execution
   - execve
   - inherited privileges
   - exec restrictions
```

Und zwar genau in der Reihenfolge.

---

# 1. FD Visibility / Ownership (extrem wichtig)

Das ist wirklich die Grundlage.

Linux behandelt fast alles als **File Descriptor**:

```text
File
Socket
Pipe
UDS
epoll
device
```

Alles:

```c
int fd
```

Beispiel:

```c
sock = socket(AF_INET, SOCK_STREAM, 0);
connect(sock, ...);
```

Dann:

```text
process memory
└── fd table
    └── fd 4 → TCP socket object
```

Wichtig:

> Der Socket gehört dem Prozess.

Nicht dem User.

Nicht „allen Prozessen der UID“.

Sondern:

**dem konkreten Prozess via FD table**.

Der Kernel prüft:

```text
Welcher Prozess besitzt dieses FD?
```

bevor:

```c
read(fd)
write(fd)
send()
recv()
```

ausgeführt werden.

---

## Warum kann ein anderer lokaler Prozess nicht HTTP mitlesen?

Beispiel:

```text
App A
 └── TCP connection to backend
```

Angreifer:

```text
App B
```

möchte sniffen.

Er kennt vielleicht sogar:

```text
PID
Port
Destination IP
```

Trotzdem:

Er besitzt **das FD nicht**.

Also:

Das geht nicht:

```c
recv(other_process_socket)
```

Der Kernel blockt das schlicht, weil:

> kein Zugriff auf fremde FD table.

Das ist die eigentliche Isolation.

---

## Analogie

Stell dir vor:

Prozess A hat:

```text
Schlüssel #42
```

für eine Pipe.

Der Schlüssel liegt im Prozessspeicher.

Prozess B sieht vielleicht:

> Ah, da ist eine TCP Verbindung.

Aber:

Er hat den Schlüssel nicht.

---

## Wo sieht man das?

Über `/proc`.

Zum Beispiel:

```bash
ls -l /proc/<pid>/fd
```

Du siehst:

```text
4 -> socket:[183728]
```

Dann:

```bash
cat /proc/net/tcp
```

zeigt:

```text
socket inode 183728
```

Also Mapping:

```text
process
 -> fd
 -> socket inode
 -> tcp connection
```

Und genau hier verbindet sich:

```text
/proc
TCP socket ownership
FD visibility
```

---

# 2. Aber warum kann root sniffen?

Weil root die Isolation umgehen kann.

Zum Beispiel:

```bash
tcpdump
```

oder:

```bash
strace -p PID
```

oder:

```bash
gdb attach
```

oder:

```bash
/proc/<pid>/mem
```

Root bzw. entsprechende Capabilities:

```text
CAP_SYS_PTRACE
CAP_NET_RAW
```

brechen die Isolation.

---

# 3. Was wäre nötig, um Daten doch zu lesen?

Es gibt nur ein paar Wege:

## A) FD erben

Parent startet Child:

```text
Parent
 └── socket fd 5

fork()
exec()
```

Child erbt FD.

Dann kann Child lesen.

Sehr wichtig für Security.

Darum:

```c
FD_CLOEXEC
```

bzw.:

```c
SOCK_CLOEXEC
```

---

## B) FD Passing über UDS

Unix Domain Socket:

```text
SCM_RIGHTS
```

kann Socket explizit übergeben.

Dann:

```text
Process A
 -> gives fd
Process B
```

und plötzlich kann B lesen.

Das ist einer der Gründe, warum UDS security-sensitive ist.

---

## C) ptrace

Debugger-artiger Zugriff.

Dann:

```text
read process memory
```

und man könnte theoretisch:

* HTTP payload lesen
* TLS keys stehlen
* Buffer dumpen

---

## D) Packet Capture

Mit:

```text
CAP_NET_RAW
```

kannst du Netzwerk sniffen.

Dann liest du Traffic **unterhalb des Prozesses**.

Das ist eine andere Ebene:

```text
network interface
```

statt FD.

---

# 4. environ leakage

Das ist ein Klassiker.

Jeder Prozess startet mit:

```text
Environment variables
```

Beispiel:

```bash
API_KEY=secret123 app
```

Im Prozess:

```bash
/proc/<pid>/environ
```

lesbar.

Dann sieht man:

```text
DATABASE_PASSWORD=abc
JWT_SECRET=...
TOKEN=...
```

Das ist **environment leakage**.

Security-Frage:

> Kann ein anderer Prozess meine Secrets lesen?

Historisch oft Ja bei gleicher UID.

Deshalb:

**Nie Secrets in Environment speichern** ist oft die Empfehlung.

Zum Testen:

Terminal 1:

```bash
MY_SECRET=hello sleep 1000
```

PID holen:

```bash
ps aux | grep sleep
```

Dann:

```bash
cat /proc/<pid>/environ | tr '\0' '\n'
```

Super gutes Lab.

---

# 5. cmdline leakage

Ähnliches Problem.

Wenn jemand so startet:

```bash
app --password=secret
```

oder:

```bash
curl -u user:password
```

Dann:

```bash
/proc/<pid>/cmdline
```

zeigt:

```text
--password=secret
```

Oder:

```bash
ps aux
```

zeigt es.

Das ist ein sehr reales Problem.

Manche Embedded-Systeme leaken da Credentials.

Test:

```bash
sleep 1000 foo bar
```

oder:

```bash
python app.py --token=mysecret
```

Dann:

```bash
cat /proc/<pid>/cmdline
```

---

# 6. ptrace (super wichtig)

Das ist:

> „Darf ich einen anderen Prozess debuggen?“

Beispiele:

```bash
strace -p PID
```

```bash
gdb -p PID
```

Technisch:

```c
ptrace()
```

Damit kann man:

* Memory lesen
* Register lesen
* Syscalls beobachten
* Code manipulieren

Also praktisch:

> Process isolation bypass.

Deshalb gibt es:

Yama

Linux hardening:

```bash
cat /proc/sys/kernel/yama/ptrace_scope
```

Typisch:

```text
1
```

heißt:

Nur Parent darf Child ptracen.

Nicht beliebige Same-UID Prozesse.

Das wäre ein extrem gutes Security-Lab für dich.

---

# 7. Process execution

Das ist:

> Was darf ein Prozess überhaupt starten?

Relevant:

```c
execve()
```

Fragen:

* darf Prozess `/bin/sh` starten?
* inherited FDs?
* inherited env?
* setuid?
* AppArmor execute deny?
* PATH abuse?

Bei euch hoch relevant wegen:

> „Warum kann unsere UDCApplication eine Shell starten?“

Das ist exakt dieses Thema.

Denn:

```text
Process isolation
└── process execution
     └── execve permissions
```

AppArmor:

```text
ix
Px
Cx
Ux
deny x
```

entscheidet oft genau das.

---

Für dein Ziel würde ich als Nächstes genau diese Reihenfolge machen:

1. **FD visibility + TCP socket ownership**
   (warum HTTP nicht mitlesbar ist)

2. **/proc leakage**

    * environ
    * cmdline
    * fd

3. **ptrace**
   (same UID attacker!)

4. **process execution**
   (eure Shell-Frage)

5. **Capabilities**
   dann als Verstärker:

    * `CAP_NET_RAW`
    * `CAP_SYS_PTRACE`
    * `CAP_KILL`
    * `CAP_NET_BIND_SERVICE`

Das baut logisch aufeinander auf.
