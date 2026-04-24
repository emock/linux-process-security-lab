#!/usr/bin/env bash
#set -uo pipefail
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
sudo cp 02_com.custom.logger.conf /etc/dbus-1/system.d/
sudo systemctl restart dbus

sudo -u dev python3 /tmp/dbus_listener.py &

sleep 2

sudo -u partner_component python3 /tmp/dbus_client.py &

sleep 2

echo "Collecting Data for 10 seconds"
sleep 10

echo "#################################################################"
echo "Trying to introspect the service as an unauthorized third party "
echo "#################################################################"
sudo -u third_party gdbus introspect --system --dest com.custom.logger --object-path /com/custom/logger

echo "#################################################################"
echo "Trying to send a message to the service as an unauthorized third party "
echo "#################################################################"
sudo -u third_party  gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vSendMessage 42 "hello" true

sleep 5

sudo pkill -u dev -f dbus_listener.py
sudo pkill -u partner_component -f dbus_client.py

wait


#############################
# Cleanup Directories
#############################

rm -rf /tmp/*.py

sudo rm -rf /etc/dbus-1/system.d/02_com.custom.logger.conf
sudo systemctl restart dbus

