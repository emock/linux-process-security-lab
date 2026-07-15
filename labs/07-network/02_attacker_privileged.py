

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