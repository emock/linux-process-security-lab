#
#
# attacker_mitm.py
#
# Hier musst du unterscheiden:
#
# MITM-Position herstellen: Namespace-, Routing- und Interface-Konfiguration
# MITM-Fähigkeiten ausüben: sniffen, droppen, verändern oder weiterleiten
#
# Daher wäre eine saubere Aufteilung:
#
# setup_mitm.sh
# attacker_mitm.py
#
# setup_mitm.sh erzeugt:
#
# client <──> mitm <──> server
#
# attacker_mitm.py demonstriert anschließend Beobachtung oder Manipulation.