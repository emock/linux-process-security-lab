# ! /usr/bin/env python
from scapy.all import IP, UDP, Raw, send, sniff, sendp


def callback(packet):



    # print(
    #     f"Captured: {packet[IP].src}:{packet[UDP].sport} "
    #     f"-> {packet[IP].dst}:{packet[UDP].dport}"
    # )

    # if Raw in packet:
    #     print(f"Payload: {packet[Raw].load!r}")

    replay = (
            IP(
                # src="10.10.0.3",
                src = packet[IP].src,
                dst=packet[IP].dst,
            )
            / UDP(
        sport=packet[UDP].sport,
        dport=packet[UDP].dport,
    )
            / bytes(packet[UDP].payload)
    )

    replay.show()

    # Checksums and lengths should be recalculated by Scapy.
    # replay[IP].chksum = None
    # replay[UDP].chksum = None

    print("Replaying packet...")
    send(replay, verbose=False)



sniff(prn=callback, filter="udp port 5000", store=0, count=1)


#
# Dieses Programm sollte bewusst andere Kernel-Schnittstellen verwenden, zum Beispiel:
#
# AF_PACKET
# SOCK_RAW
#
# Mögliche Modi:
#
# python3 attacker_privileged.py sniff
# python3 attacker_privileged.py spoof
# python3 attacker_privileged.py inject
#
# Dann demonstriert die Datei wirklich die zusätzlichen Fähigkeiten durch CAP_NET_RAW.
#
# Für CAP_NET_ADMIN würde ich eher ein eigenes Setup-Skript verwenden:
#
# setup_mitm.sh
#
# Denn Routingtabellen, Interfaces, Forwarding und Netfilter sind Systemkonfiguration und nicht bloß das Verhalten eines einzelnen Python-Prozesses.




# 2. UDP Source-IP-Spoofing
#
# Du sendest:
#
# src = 10.10.0.1
# dst = 10.10.0.2
#
# obwohl das Paket vom Angreifer stammt.
#
# Wenn der Server die Source-IP als Identität verwendet, ist das ein schönes Security-Learning.
#
# 3. Replay
#
# Du sniffst ein UDP-Datagramm und sendest denselben Payload erneut.
#
# Das demonstriert Replay ohne MITM.