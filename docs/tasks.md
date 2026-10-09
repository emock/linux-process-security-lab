
# General

- [ ] common.py is duplicated per directory - this should only be a single
  source

# lab-01-process-isolation

- [ ] Add Capabilities
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

    
# lab-05-dbus
- [ ] Implement signals
- 
- [ ] Scenario eavesdropping: Run Service as dev, listen with shared_group user
- [ ] Receive Rules <allow receive_sender="..."/> <allow receive_interface="..."/> <allow receive_member="..."/>

  



# Networking VM-based 

> Keep the ideas here as a note but implement in different project

Dein Grundgedanke ist gut, aber ich würde die Lab-Struktur nicht primär an Interfaces festmachen, sondern an *
*Angreiferposition, Beobachtbarkeit und Kontrolle über den Kommunikationspfad**.

Ein wichtiger Punkt vorweg:

**Auch localhost-Verkehr läuft durch den TCP/IP-Stack.**
Der Unterschied ist nicht „lokales Routing versus TCP-Stack“, sondern eher:

* Kommunikation bleibt im lokalen Network Namespace
* Pakete verlassen keinen physischen oder virtuellen Link
* ein externer Netzwerkangreifer liegt nicht automatisch auf dem Pfad
* lokale Prozesse können trotzdem je nach Privilegien beobachten, beeinflussen oder eigene Verbindungen aufbauen

## Sinnvolle Angreifermodelle

Ich würde mindestens vier Modelle unterscheiden.

### Remote attacker

Der Angreifer kann den Service über ein erreichbares Netzwerkinterface ansprechen.

Typische Fähigkeiten:

* beliebige Requests senden
* Verbindungen parallel oder wiederholt aufbauen
* fehlerhafte Protokollzustände erzeugen
* Ressourcenverbrauch provozieren
* Quell-IP grundsätzlich nicht vertrauenswürdig machen
* Anwendungsschwächen ausnutzen

Typische Grenzen:

* kein lokaler Prozesszugriff
* kein Zugriff auf lokale Dateien oder Unix-Sockets
* kein direktes Sniffing des Host-internen Verkehrs
* keine Manipulation des Kernels oder der Netzwerkkonfiguration

Das ist primär das Modell für:

* exponierte TCP-Services
* Authentisierung
* Rate Limiting
* Protokollvalidierung
* sichere Parser
* TLS
* Firewalling

---

### Local unprivileged attacker

Das ist deutlich mächtiger als ein normaler Remote-Angreifer.

Der Angreifer kann:

* lokale Verbindungen zu `127.0.0.1` aufbauen
* alle für ihn erreichbaren lokalen Ports ansprechen
* eigene Prozesse starten
* lokale Ressourcen erschöpfen
* Prozess- und Netzwerkinformationen aus `/proc` auslesen, soweit erlaubt
* eventuell dieselben Benutzer- oder Gruppenrechte wie der Dienstclient besitzen
* falsche Annahmen über „localhost ist vertrauenswürdig“ ausnutzen

Das ist für mich eines der wichtigsten Learnings des Labs:

> `localhost` ist keine Vertrauensgrenze.

Ein Service, der nur an `127.0.0.1` gebunden ist, ist zwar nicht remote erreichbar, aber gegenüber lokalem Code trotzdem
exponiert.

Besonders interessant wären hier:

* unauthentisierte localhost APIs
* Vertrauen auf Source-IP `127.0.0.1`
* schwache Token in Kommandozeilenargumenten oder Environment-Variablen
* Port-Races
* DNS-/Proxy-Konfigurationen
* Zugriff auf Admin- oder Debug-Interfaces
* Server-Side Request Forgery auf localhost

---

### Local privileged attacker

Hier solltest du genauer zwischen `root` und einzelnen Capabilities unterscheiden. Sonst wird das Modell schnell zu
grob.

Ein voll privilegierter Angreifer kann praktisch jede hostlokale Netzwerksicherheitsannahme brechen:

* Firewallregeln verändern
* Network Namespaces betreten
* Traffic umleiten
* Interfaces konfigurieren
* Prozesse inspizieren
* Schlüssel oder Tokens lesen
* Binaries austauschen
* eBPF oder Packet Capture verwenden
* Routingtabellen verändern

Daher ist „root attacker“ häufig kein sinnvolles Schutzmodell für einen normalen Dienst.

Spannender ist die Demonstration einzelner Capabilities:

#### `CAP_NET_RAW`

Ermöglicht unter anderem:

* Raw Sockets
* Paketkonstruktion
* bestimmte Formen von IP-Spoofing
* Packet Capture über Packet Sockets

#### `CAP_NET_ADMIN`

Ermöglicht unter anderem:

* Interface-Konfiguration
* Routingänderungen
* Firewall- und Netfilter-Manipulation
* Traffic Control
* Namespace-relevante Netzwerkeingriffe

#### `CAP_NET_BIND_SERVICE`

Erlaubt lediglich das Binden privilegierter Ports unter 1024.

Das ist ein gutes Beispiel dafür, dass „Network Capability“ nicht automatisch umfassende Netzwerkhoheit bedeutet.

#### `CAP_BPF` und eventuell `CAP_PERFMON`

Je nach Kernel und Konfiguration relevant für:

* eBPF-basierte Beobachtung
* Tracepoints
* Netzwerk-Telemetrie
* teilweise tiefen Einblick in den Host

Die zentrale Frage sollte jeweils sein:

> Welche Sicherheitsannahme wird durch genau diese Capability ungültig?

---

### Network MITM attacker

Der MITM-Angreifer ist nicht einfach ein Remote-Angreifer mit mehr Paketen.

Er kann:

* Verkehr beobachten
* Pakete verzögern
* Pakete verwerfen
* Pakete duplizieren
* Pakete verändern
* Verbindungen umleiten
* eigene Antworten einspeisen
* DNS- oder ARP-bezogene Manipulationen versuchen

Aber er kann nicht automatisch:

* TLS brechen
* gültige Zertifikate erzeugen
* Anwendungsnachrichten unbemerkt verändern, wenn Integrität korrekt geschützt ist
* lokale Hostdaten lesen

Damit kannst du sehr gut zeigen:

* Verschlüsselung versus Integrität
* TLS mit und ohne Zertifikatsprüfung
* Klartextprotokolle
* Replay-Schutz
* DNS-Vertrauen
* Reverse Proxy Trust
* manipulierte Header
* Downgrade-Probleme

## Ich würde das Lab in Zonen statt nur Interfaces modellieren

Ein gutes Grundmodell wäre:

```text
[Local process]
      |
      | loopback
      v
[Service on 127.0.0.1]

[Remote client namespace]
      |
      | routed veth link
      v
[Service network interface]

[MITM namespace]
      |
      +---- Client namespace
      |
      +---- Server namespace
```

Dafür brauchst du nicht zwingend mehrere echte VMs. Linux Network Namespaces sind für dieses Lernziel sogar besser, weil
du die Angreiferposition kontrolliert modellieren kannst.

Beispielsweise:

```text
ns_client <----> ns_mitm <----> ns_server
```

Der MITM-Namespace ist dann wirklich im Pfad. Dort kannst du:

* Forwarding aktivieren
* Routing manipulieren
* Pakete mitschneiden
* Pakete verwerfen
* NAT einsetzen
* Verzögerung und Verlust simulieren
* DNS manipulieren

Das ist didaktisch sauberer als mehrere Interfaces im gleichen Namespace. Mehrere Interfaces allein erzeugen noch keinen
MITM-Angreifer.

## IP-Spoofing würde ich vorsichtig einordnen

IP-Spoofing ist zwar demonstrierbar, aber häufig missverständlich.

Bei verbindungsorientiertem TCP ist simples Source-IP-Spoofing nicht besonders nützlich, weil der Angreifer den
Rückverkehr und die TCP-Sequenznummern beherrschen muss.

Ein gutes Lab sollte deshalb unterscheiden:

### UDP-Spoofing

Relativ einfach:

* gefälschte Quell-IP
* keine Verbindung
* Rückantwort geht zur gefälschten Adresse
* gut geeignet, um zu zeigen, warum Source-IP keine Authentisierung ist

### TCP-Spoofing

Deutlich schwieriger:

* Three-Way Handshake
* Rückweg muss kontrolliert werden
* Sequenznummern
* SYN-Cookies und Kernelverhalten
* häufig eher Routing-/MITM-Szenario als „einfaches Spoofing“

Für das Learning „IP-Adressen sind keine Identitäten“ ist UDP oft die bessere Demonstration.

Für TCP würde ich stattdessen eher zeigen:

* MITM mit kontrolliertem Routing
* Proxying
* NAT
* manipulierte `X-Forwarded-For`-Header
* falsches Vertrauen in Proxy-Informationen

## Mögliche Security Learnings

Ich würde das Lab so bauen, dass jede Ebene eine falsche Sicherheitsannahme widerlegt.

| Annahme                                           | Demonstration                                          |
| ------------------------------------------------- | ------------------------------------------------------ |
| `localhost` ist vertrauenswürdig                  | unprivilegierter lokaler Prozess ruft Admin-API auf    |
| Nur externe Angreifer sind relevant               | lokaler Prozess umgeht Netzwerkfirewall                |
| Source-IP identifiziert einen Client              | UDP-Spoofing oder Proxy-Header-Manipulation            |
| Netzwerksegmentierung ersetzt Authentisierung     | erlaubter Client im Segment greift fremde Funktion auf |
| Verschlüsselung verhindert Manipulation           | Klartext versus TLS                                    |
| TLS allein reicht                                 | Client prüft Zertifikat nicht                          |
| Root ist der einzige gefährliche lokale Angreifer | `CAP_NET_RAW` oder `CAP_NET_ADMIN` gezielt vergeben    |
| Ein gebundener Port ist sicher                    | Service lauscht versehentlich auf `0.0.0.0`            |
| Firewall bedeutet Dienstschutz                    | erlaubter Pfad erreicht verwundbare Anwendung          |
| Der direkte Peer ist der echte Client             | Reverse Proxy beziehungsweise Load Balancer            |

## Konkreter Lab-Aufbau

Ich würde drei separate Services oder Betriebsmodi nutzen.

### Service A: localhost-only

Bind:

```text
127.0.0.1:8080
```

Tests:

* Remote Namespace kann nicht verbinden
* lokaler unprivilegierter Benutzer kann verbinden
* lokale Admin-Funktion ohne Authentisierung
* optional SSRF von einem extern erreichbaren Service auf diesen Port

Security-Aussage:

> Bind-Adresse begrenzt Erreichbarkeit, aber authentisiert keinen lokalen Client.

### Service B: extern erreichbarer Service

Bind:

```text
0.0.0.0:8081
```

Tests:

* Remote Requests
* Firewall erlaubt oder blockiert den Port
* Service erkennt Source-IP
* Rate Limiting
* Authentisierung
* Input-Validierung

Security-Aussage:

> Netzwerkzugriffskontrolle und Anwendungsauthentisierung sind unterschiedliche Kontrollen.

### Service C: Kommunikation über MITM-Router

Client und Server liegen in getrennten Namespaces.

Tests:

* Klartextmitschnitt
* Paketverlust
* Verzögerung
* DNS-Manipulation
* TLS mit deaktivierter Zertifikatsprüfung
* TLS mit korrekter Prüfung
* eventuell Replay eines einfachen Applikationsprotokolls

Security-Aussage:

> Transporterreichbarkeit sagt nichts über Vertraulichkeit, Integrität oder Peer-Identität aus.

## Was ich nicht vermischen würde

Einige Themen hängen zusammen, sollten aber getrennt demonstriert werden:

* **Reachability:** Kann der Angreifer den Dienst erreichen?
* **Observability:** Kann er den Verkehr beobachten?
* **Manipulation:** Kann er den Verkehr verändern?
* **Impersonation:** Kann er sich als anderer Peer ausgeben?
* **Authorization:** Darf ein authentisierter Peer die Aktion ausführen?
* **Host compromise:** Kann er Sicherheitskontrollen auf dem Host selbst verändern?

Das verhindert etwa die falsche Schlussfolgerung:

> Wer Pakete fälschen kann, kann sich automatisch als beliebiger TCP-Client authentisieren.

Oder:

> Wer lokal ist, kann automatisch jeden Prozessverkehr sniffen.

Beides hängt stark von Privilegien, Namespace, Kernelkonfiguration und Protokoll ab.

## Mein bevorzugtes Gesamtmodell

Ich würde die Matrix aus zwei Dimensionen aufbauen:

### Angreiferposition

* Remote Endpoint
* On-path MITM
* Local unprivileged
* Local capability-enabled
* Local root

### Angreiferfähigkeit

* Connect
* Observe
* Inject
* Modify
* Redirect
* Spoof
* Reconfigure
* Read secrets

Damit wird sichtbar, dass Begriffe wie „local attacker“ allein noch nicht präzise genug sind.

Ein lokaler Benutzer ohne besondere Rechte kann wahrscheinlich einen localhost-Port ansprechen. Er kann aber nicht
zwangsläufig beliebigen Loopback-Traffic mitschneiden oder Routingtabellen verändern. Ein Prozess mit `CAP_NET_RAW` hat
andere Möglichkeiten als einer mit `CAP_NET_ADMIN`.

Der stärkste didaktische Aufbau wäre daher:

```text
Level 1: Remote connectivity
Level 2: Localhost exposure
Level 3: On-path observation and manipulation
Level 4: Capability-based host attacker
Level 5: Full host compromise
```

So zeigst du nicht nur verschiedene Angreifer, sondern auch, **welche Sicherheitskontrolle gegen welche Fähigkeit wirkt
und wann sie wirkungslos wird**.

