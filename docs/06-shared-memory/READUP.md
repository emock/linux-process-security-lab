POSIX Shared Memory

+--------------------------------------+
| Applikationsprotokoll |
| command, flags, payload, version |
+--------------------------------------+
| Synchronisationsprotokoll |
| producer, consumer, ready, lock |
+--------------------------------------+
| Shared Memory |
| gemeinsame Bytes |
+--------------------------------------+


Datenformat: 

struct Message {

    uint32_t command;

    uint32_t length;

    uint8_t payload[4096];

};



Synchronisation über

Semaphore
Ringpuffer
Ready flags






APIs

shm_open()
ftruncate()
mmap()


These are created in /dev/shm/


From a security POV this is strongly related to a file-like DAC permission




System-V Shared Memory

APIs

shmget
shmat
shmdt
shmctl

Show IPCs

ipcs -m




Attack Surface

length = shared->length;
memcpy(local_buffer, shared->data, length);

Wenn length manipuliert werden kann und nicht validiert wird:

Shared-Memory-Tampering
→ Buffer Overflow
→ Memory Corruption
→ eventuell Code Execution


Weitere gefährliche Inhalte wären:

Funktionspointer
absolute Pointer
Offsets
Objektgrößen
Indizes
Statusflags
Dateipfade
Routing-Informationen



L'ngenfelder:

struct Message {
uint32_t length;
char payload[4096];
};

memcpy(buf, msg->payload, msg->length);