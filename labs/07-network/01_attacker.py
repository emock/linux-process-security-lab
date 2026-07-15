#

#  Use setup.sh for this scenario
#  10.10.0.1/24 <---- veth ----> 10.10.0.2/24


# network_remote.py und local_unprivileged_attacker.py können tatsächlich nahezu identisch sein:
#
# send_request(target_ip, target_port, payload)
#
# Der Unterschied liegt nicht in der verwendeten Socket-API, sondern in:
#
# dem Namespace, in dem der Prozess läuft,
# der erreichbaren Zieladresse,
# den verfügbaren lokalen Ressourcen,
# dem daraus abgeleiteten Threat Model.
#
# Daher wäre diese Struktur sauber:
#
# server.py
# client.py
#
# attacker_unprivileged.py
# attacker_privileged.py
# attacker_mitm.py
#
# Und der unprivilegierte Angreifer wird in zwei unterschiedlichen Kontexten gestartet:
#
# # Local unprivileged attacker
# python3 attacker_unprivileged.py 127.0.0.1 5000
# # Remote attacker
# sudo ip netns exec ns_client \
#     python3 attacker_unprivileged.py 10.10.0.2 5000
#
# Damit wird ein wichtiges Learning sichtbar:
#
# Local und remote können exakt denselben Request senden. Die Angreiferposition bestimmt aber, welche Ziele und zusätzlichen Host-Ressourcen erreichbar sind.


import socket


HOST = "127.0.0.1"
HOST = "10.10.0.2"
PORT = 5000



with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"attacker calling")
    # data = s.recv(1024)

