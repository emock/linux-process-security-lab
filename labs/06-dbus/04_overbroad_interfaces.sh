#!/usr/bin/env bash
set -euo pipefail
set -x

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi

#############################
# Setup the Directories and Files
#############################

mkdir -p /tmp/overbroad_logs



cp "$SCRIPT_DIR/dbus_listener.py" "/tmp/"
cp "$SCRIPT_DIR/dbus_client.py" "/tmp/"
cp "$SCRIPT_DIR/privileged_client.py" "/tmp/"


echo "Setting up DBUS config and restarting DBUS"
sudo cp 04_overbroad_interfaces.conf /etc/dbus-1/system.d/
sudo systemctl restart dbus


sudo -u dev python3 /tmp/dbus_listener.py &

sleep 2

sudo -u partner_component python3 /tmp/dbus_client.py &
sudo -u partner_component python3 /tmp/privileged_client.py &

sleep 2

echo "Collecting Data for 20 seconds"
echo "Manually calling methods from partner2"
sleep 20


sudo pkill -u dev -f dbus_listener.py
sudo pkill -u partner_component -f dbus_client.py
sudo pkill -u partner_component -f privileged_client.py

wait





#############################
# Cleanup Directories
#############################

rm -rf /tmp/*.py

#rm -rf /tmp/overbroad_logs/

sudo rm -rf /etc/dbus-1/system.d/04_overbroad_interfaces.conf
sudo systemctl restart dbus
