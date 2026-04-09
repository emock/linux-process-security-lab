#!/usr/bin/env bash
set -euo pipefail
set -x


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi

#############################
# Setup the Users and Groups
#############################

# this is a shared group between dev and partner component
sudo groupadd -f shared_group

# does not have a home but access to shell
id partner_component &>/dev/null || sudo useradd -M -s /bin/bash partner_component
id third_party &>/dev/null || sudo useradd -M -s /bin/bash third_party



# Add dev to the group
sudo usermod -aG shared_group dev

#only is additionally member of labgroup, no other groups
sudo usermod -G shared_group partner_component


# Final Check
id partner_component
groups partner_component


id third_party
groups third_party


#############################
# Setup the Directories and Files
#############################

cp "$SCRIPT_DIR/dbus_listener.py" "/tmp/"
cp "$SCRIPT_DIR/dbus_client.py" "/tmp/"


echo "Lab 05 setup complete."