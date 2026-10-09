#!/usr/bin/env bash
#set -euo pipefail
#set -x


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi


#############################
# Setup the Directories and Files
#############################

cp "$SCRIPT_DIR/dbus_listener.py" "/tmp/"
cp "$SCRIPT_DIR/dbus_client.py" "/tmp/"


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

echo "#################################################################"
echo "Killing the DBUS_Listener of dev"
echo "#################################################################"

sudo pkill -u dev -f dbus_listener.py

echo "Collecting Data for 10 seconds"
sleep 10

sudo pkill -u partner_component -f dbus_listener.py
sudo pkill -u partner_component -f dbus_client.py

wait





#############################
# Cleanup Directories
#############################

rm -rf /tmp/*.py

sudo rm -rf /etc/dbus-1/system.d/03_spoofing.conf
sudo systemctl restart dbus

