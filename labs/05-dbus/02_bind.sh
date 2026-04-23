#!/usr/bin/env bash
set -uo pipefail
set -x

./setup.sh

echo "Setting up DBUS config and restarting DBUS"
sudo cp 02_com.custom.logger.conf /etc/dbus-1/system.d/
sudo systemctl restart dbus

sudo -u dev python3 /tmp/dbus_listener.py &

sleep 2

sudo -u partner_component python3 /tmp/dbus_client.py &

sleep 2

echo "Collecting Data for 10 seconds"
sleep 10

echo "Trying to introspect the service as an unauthorized third party "
sudo -u third_party gdbus introspect --system --dest com.custom.logger --object-path /com/custom/logger

echo "Trying to send a message to the service as an unauthorized third party "
sudo -u third_party  gdbus call --system --dest com.custom.logger --object-path /com/custom/logger --method com.custom.logger.vSendMessage 42 "hello" true

sleep 5

sudo pkill -u dev -f dbus_listener.py
sudo pkill -u partner_component -f dbus_client.py

wait

sudo rm -rf /etc/dbus-1/system.d/02_com.custom.logger.conf
sudo systemctl restart dbus


./cleanup.sh