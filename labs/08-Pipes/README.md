Ja, das passt sehr gut in dieses Lab. Ich würde sogar den Scope etwas weiter fassen als nur **Named Pipes/FIFOs**.
Gerade wenn dein Ziel Linux Security ist, ist es sinnvoll, zuerst das mentale Modell hinter Shell-Pipes sauber
aufzubauen und danach FIFOs als persistente, benannte Variante einzuführen.

Ich würde `08` ungefähr so strukturieren:

```text
08-pipes/
├── README.md
├── 01_anonymous_pipe.sh
├── 02_pipe_fd_demo.py
├── 03_named_pipe_basic.sh
├── 04_named_pipe_python.py
├── 05_fifo_permissions.sh
└── 06_fifo_attack.py
```

## 1. Erst das mentale Modell: stdin, stdout, stderr

Bevor wir `|` behandeln, würde ich genau hier anfangen:

```text
Process
 ├── fd 0  stdin
 ├── fd 1  stdout
 └── fd 2  stderr
```

Das erklärt anschließend einen Großteil der vermeintlich kryptischen Bash-Syntax.

Zum Beispiel:

```bash
echo "hello" > file.txt
```

ist konzeptionell:

```text
echo
 fd 1 ────────────> file.txt
```

und:

```bash
cat < file.txt
```

ist:

```text
file.txt ─────────> fd 0
                       cat
```

Dann wird auch das hier verständlicher:

```bash
command 2> error.log
command > output.log 2> error.log
command > everything.log 2>&1
```

Gerade `2>&1` würde ich nicht als Bash-Voodoo erklären, sondern wörtlich:

> Verändere fd 2 so, dass er auf dasselbe Ziel zeigt wie fd 1.

Das ist für Security später ziemlich wichtig.

---

## 2. Anonymous Pipes und `|`

Danach:

```bash
ps aux | grep nginx
```

Mental:

```text
ps aux                         grep nginx

stdout (fd 1) ── PIPE ──> stdin (fd 0)
```

Wichtig wäre mir hier die Erkenntnis:

**`|` übergibt nicht einfach "Text von einem Befehl an einen anderen".**

Die Shell:

1. erzeugt eine Pipe,
2. startet Prozesse,
3. verdrahtet deren File Descriptors,
4. `stdout` des linken Prozesses landet im Write-End,
5. `stdin` des rechten Prozesses kommt vom Read-End.

Damit kannst du dann auch schön zeigen:

```bash
printf "hello\nworld\n" | grep world
```

und später in Python/C nachvollziehen, was die Shell eigentlich für uns erledigt.

### Security-relevanter Nebenaspekt

Hier würde ich bereits Dinge wie diese aufnehmen:

```bash
cat untrusted.txt | grep ...
```

vs. Command Substitution:

```bash
result=$(command)
```

vs.

```bash
command1 | command2
```

Denn syntaktisch sehen Shell-Konstrukte schnell ähnlich aus, haben aber fundamental andere Semantik.

---

## 3. Redirection gehört unbedingt dazu

Das wäre für mich dein "related work"-Block:

```bash
cmd > file
cmd >> file
cmd < file
cmd 2> file
cmd 2>&1
cmd >/dev/null 2>&1
cmd1 | cmd2
cmd1 |& cmd2
```

Und insbesondere die Reihenfolge:

```bash
cmd >file 2>&1
```

ist **nicht dasselbe** wie:

```bash
cmd 2>&1 >file
```

Das ist ein hervorragendes kleines Experiment, weil man dabei lernt, dass die Shell Redirections **von links nach rechts
** verarbeitet.

Das ist eines dieser Themen, bei denen Bash plötzlich viel weniger unintuitiv wird, sobald man nicht mehr versucht, sich
die Syntax zu merken, sondern sich vorstellt:

```text
Wo zeigt fd 0 hin?
Wo zeigt fd 1 hin?
Wo zeigt fd 2 hin?
```

---

# 4. Danach: Named Pipes / FIFOs

Erst jetzt:

```bash
mkfifo /tmp/demo.fifo
```

Terminal 1:

```bash
cat /tmp/demo.fifo
```

Terminal 2:

```bash
echo "secret message" > /tmp/demo.fifo
```

Das Schöne daran: Jetzt kannst du den Unterschied direkt zeigen.

Anonymous Pipe:

```text
process A ─── PIPE ───> process B
             ^
       kein Dateiname
```

FIFO:

```text
process A ──> /tmp/demo.fifo ──> process B
                    ^
              Filesystem object
```

Dabei würde ich aber früh einen wichtigen Punkt herausstellen:

> Der Inhalt der FIFO liegt nicht als normale Datei im Filesystem.

Der Filesystem-Eintrag dient als **benannter IPC-Endpunkt**.

Das sieht man schön mit:

```bash
ls -l /tmp/demo.fifo
```

beispielsweise:

```text
prw-r--r-- 1 user user 0 Sep 7 09:00 /tmp/demo.fifo
^
FIFO
```

---

# 5. Blocking-Verhalten untersuchen

Das sollte meiner Meinung nach ein eigenes Experiment sein.

```bash
mkfifo demo
echo "hello" > demo
```

Und dann passiert scheinbar: **nichts.**

Warum?

Weil noch kein Reader vorhanden ist.

In einem zweiten Terminal:

```bash
cat demo
```

Jetzt laufen beide weiter.

Das vermittelt sehr schön, dass eine FIFO kein Briefkasten ist:

```text
WRITER                 FIFO                 READER

open()  ───────────────┐
                       │ wartet
                       │
                       │        <────────── open()
                       │
write() ───────────────┼───────────────> read()
```

Damit kannst du später auch über Deadlocks, DoS und Prozess-Synchronisation sprechen.

---

# 6. Security-Lab: Permissions

Dann kommen wir zum eigentlichen Security-Thema.

Unsicher:

```bash
mkfifo /tmp/app.fifo
chmod 666 /tmp/app.fifo
```

Damit können andere Prozesse je nach Situation:

* Daten hineinschreiben,
* Daten lesen,
* legitime Kommunikation stören,
* einen erwarteten Kommunikationspartner imitieren,
* Prozesse durch das FIFO-Verhalten blockieren.

Beispielsweise:

```text
              legitimate client
                    │
                    ▼
              /tmp/app.fifo
                    │
                    ▼
                  server


              attacker
                 │
                 └──────────> /tmp/app.fifo
```

Damit wird aus dem simplen `mkfifo`-Experiment tatsächlich ein kleines **IPC-Security-Lab**.

---

## 7. Interessanter Angriff: falscher Reader

Ich würde nicht nur "Attacker schreibt Müll hinein" demonstrieren.

Interessanter ist beispielsweise:

```bash
mkfifo /tmp/service.fifo
chmod 666 /tmp/service.fifo
```

Ein Prozess erwartet:

```bash
echo "API_TOKEN=secret" > /tmp/service.fifo
```

Aber statt des legitimen Empfängers startet der Angreifer:

```bash
cat /tmp/service.fifo
```

Dann kannst du untersuchen, **wer die Daten tatsächlich bekommt**.

Das führt zu einer wichtigen Security-Erkenntnis:

> Filesystem permissions regeln, wer eine FIFO öffnen darf. Sie authentifizieren aber nicht automatisch den
Kommunikationspartner.

Das ist wesentlich interessanter als nur "world writable = bad".

---

# 8. `/tmp` und Object-Creation-Angriffe

Danach würde ich das Ganze mit dem Filesystem-Security-Thema verbinden:

```bash
/tmp/myapp.fifo
```

Was passiert, wenn ein privilegierter Prozess erwartet, dass dieser Pfad nicht existiert?

Ein Angreifer könnte vorher selbst etwas unter diesem Namen erzeugen.

Damit kommst du zu Themen wie:

```text
predictable pathname
       │
       ▼
 /tmp/app.fifo
       ▲
       │
 attacker creates object first
```

und damit zu:

* ownership
* `umask`
* sticky bit auf `/tmp`
* sichere Runtime-Verzeichnisse
* Race Conditions
* TOCTOU
* `lstat()` / `open()`-Problematiken
* Symlink-/Filesystem-Angriffen

Nicht alles davon muss in diesem Lab vollständig behandelt werden. Aber die FIFO ist ein hervorragender Aufhänger dafür.

---

## Mein vorgeschlagener README-Outline

Deinen ursprünglichen Outline würde ich deshalb erweitern:

```markdown
# 08 – Linux Pipes and FIFOs

## Concept

Linux pipes provide byte-stream based inter-process communication.

This lab covers both anonymous pipes commonly used by shells
and named pipes (FIFOs) exposed through the filesystem.

## Part 1 – Shell I/O fundamentals

- stdin, stdout, stderr
- file descriptors 0, 1, 2
- input/output redirection
- `>`, `>>`, `<`
- `2>`, `2>&1`
- redirection order

## Part 2 – Anonymous Pipes

- `|`
- connecting stdout to stdin
- pipe lifecycle
- blocking behavior
- shell-created pipes

## Part 3 – Named Pipes (FIFO)

- `mkfifo`
- filesystem representation
- reader/writer behavior
- blocking semantics
- permissions and ownership

## Security implications

- unintended readers
- unintended writers
- weak FIFO permissions
- predictable FIFO paths
- insecure use of `/tmp`
- IPC peer authentication
- denial of service through blocking
```

Ich halte diese Reihenfolge gerade für dein Projekt für besser als direkt mit `mkfifo` anzufangen. *
*`|`, `<`, `>`, `2>`, `2>&1` und FIFOs sind keine zufällige Sammlung seltsamer Bash-Syntax.** Darunter steckt fast
überall dasselbe Unix-Modell aus **Prozess + File Descriptors + offenen Dateien/Pipes**.

Wenn dieses Modell einmal sitzt, wird ein ziemlich großer Teil der Bash-Syntax plötzlich ableitbar statt auswendig zu
lernen.
