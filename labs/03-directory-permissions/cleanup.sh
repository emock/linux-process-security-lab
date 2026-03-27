#!/usr/bin/env bash
set -euo pipefail
set -x

#rwxrwxrwx
TARGET_DIR1="/tmp/lab-03-s1-700"
#r-xr-xr-x
TARGET_DIR2="/tmp/lab-03-s2-500"
#-wx-wx-wx
TARGET_DIR3="/tmp/lab-03-s3-300"
#-w--w--w-
TARGET_DIR4="/tmp/lab-03-s4-200"
#--x--x--x
TARGET_DIR5="/tmp/lab-03-s5-100"
#---------
TARGET_DIR6="/tmp/lab-03-s6-000"


#############################
# Cleanup Directories
#############################

rm -rf /tmp/lab-03*
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

echo "Lab 03 cleanup complete."
