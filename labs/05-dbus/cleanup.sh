#!/usr/bin/env bash
set -euo pipefail
set -x


#############################
# Cleanup Directories
#############################

rm -rf /tmp/*.py



#############################
# Cleanup Users
#############################

if id partner_component >/dev/null 2>&1; then
  sudo userdel partner_component
fi

if id third_party >/dev/null 2>&1; then
  sudo userdel third_party
fi


#############################
# Cleanup Group
#############################

if getent group shared_group >/dev/null 2>&1; then
  sudo groupdel shared_group
fi




echo "Lab 05 cleanup complete."
