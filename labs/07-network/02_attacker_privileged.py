# ! /usr/bin/env python
from scapy.all import IP, UDP, send, sniff,

def callback(packet, spoofing):

    print(packet.summary())

    spoof = "10.10.0.3"

    if spoofing:
        ip = IP(src=spoof,
                dst=packet[IP].dst)
    else:
        ip = IP(
            src=packet[IP].src,
            dst=packet[IP].dst
        )

    replay = (
         ip
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




spoof = False
# spoof = True

#  use iface=lo to get packet if localhost is used, otherwise packet will not be captured
sniff(iface="lo",prn=lambda packet: callback(packet,spoofing=spoof), filter="udp port 5000", store=0, count=1)
