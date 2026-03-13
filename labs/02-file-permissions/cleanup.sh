#!/usr/bin/env bash
set -euo pipefail
set -x

TARGET_DIR1="/tmp/lab-02-s1-open"
TARGET_DIR2="/tmp/lab-02-s2-group-access"
TARGET_DIR3="/tmp/lab-02-s3-owner-only"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi

#############################
# Cleanup Directories
#############################

rm -rf "$TARGET_DIR1" "$TARGET_DIR2" "$TARGET_DIR3"

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

echo "Lab 02 cleanup complete."
