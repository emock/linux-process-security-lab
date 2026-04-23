#!/usr/bin/env bash
set -euo pipefail
set -x


./setup.sh

echo "Setting up DBUS config and restarting DBUS"
sudo cp 03_spoofing.conf /etc/dbus-1/system.d/
sudo systemctl restart dbus


sudo -u dev python3 /tmp/dbus_listener.py &

sleep 2

sudo -u partner_component python3 /tmp/dbus_client.py &

sleep 2


sudo -u partner_component python3 /tmp/dbus_listener.py &

echo "Collecting Data for 10 seconds"
sleep 10

sudo pkill -u dev -f dbus_listener.py

echo "Collecting Data for 10 seconds"
sleep 10

sudo pkill -u partner_component -f dbus_listener.py
sudo pkill -u partner_component -f dbus_client.py

wait


sudo rm -rf /etc/dbus-1/system.d/03_spoofing.conf
sudo systemctl restart dbus

./cleanup.sh