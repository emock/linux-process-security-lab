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

cp "$SCRIPT_DIR/file_rename_tester.py" "/tmp/"
cp "$SCRIPT_DIR/common.py" "/tmp/"




mkdir -p "$TARGET_DIR1"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR1/config.json"

mkdir -p "$TARGET_DIR2"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR2/config.json"

mkdir -p "$TARGET_DIR3"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR3/config.json"

mkdir -p "$TARGET_DIR4"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR4/config.json"

mkdir -p "$TARGET_DIR5"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR5/config.json"

mkdir -p "$TARGET_DIR6"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR6/config.json"



sudo chown -R dev:shared_group /tmp/lab-03-s*








#############################
# TARGET_DIR1
#############################


chmod u=,g=,o= "$TARGET_DIR1/config.json"
chmod u=rwx,g=,o= $TARGET_DIR1






#############################
# TARGET_DIR2
#############################


chmod u=,g=,o= "$TARGET_DIR2/config.json"
chmod u=rx,g=,o= $TARGET_DIR2

#############################
# TARGET_DIR3
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files

chmod u=,g=,o= "$TARGET_DIR3/config.json"
chmod u=wx,g=,o= $TARGET_DIR3

#############################
# TARGET_DIR4
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files

chmod u=,g=,o= "$TARGET_DIR4/config.json"
chmod u=w,g=,o= $TARGET_DIR4

#############################
# TARGET_DIR5
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files

chmod u=,g=,o= "$TARGET_DIR5/config.json"
chmod u=x,g=,o= $TARGET_DIR5


#############################
# TARGET_DIR5
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files

chmod u=,g=,o= "$TARGET_DIR6/config.json"
chmod u=,g=,o= $TARGET_DIR6




echo "Lab 03 setup complete."