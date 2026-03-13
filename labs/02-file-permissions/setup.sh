#!/usr/bin/env bash
set -euo pipefail
set -x


#rwxrwxrwx
TARGET_DIR1="/tmp/lab-02-s1-open"
#rwxrwx---
TARGET_DIR2="/tmp/lab-02-s2-group-access"
#rwx------
TARGET_DIR3="/tmp/lab-02-s3-owner-only"


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

cp "$SCRIPT_DIR/file_access_tester.py" "/tmp/"




mkdir -p "$TARGET_DIR1"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR1/config1_open.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR1/config2_group.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR1/config3_owner.json"


mkdir -p "$TARGET_DIR2"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR2/config1_open.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR2/config2_group.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR2/config3_owner.json"


mkdir -p "$TARGET_DIR3"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR3/config1_open.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR3/config2_group.json"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR3/config3_owner.json"



#############################
# TARGET_DIR1
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files
sudo chown dev:shared_group "$TARGET_DIR1"
sudo chown dev:shared_group "$TARGET_DIR1"/config*.json

chmod u=rwx,g=rwx,o=rwx $TARGET_DIR1
chmod u=rw,g=rw,o=rw "$TARGET_DIR1/config1_open.json"
chmod u=rw,g=rw,o= "$TARGET_DIR1/config2_group.json"
chmod u=rw,g=,o= "$TARGET_DIR1/config3_owner.json"


#############################
# TARGET_DIR2
#############################

#Setup the POSIX Permission Bits/DAC of Directories and Files
sudo chown dev:shared_group "$TARGET_DIR2"
sudo chown dev:shared_group "$TARGET_DIR2"/config*.json


chmod u=rwx,g=rwx,o= $TARGET_DIR2
chmod u=rw,g=rw,o=rw "$TARGET_DIR2/config1_open.json"
chmod u=rw,g=rw,o= "$TARGET_DIR2/config2_group.json"
chmod u=rw,g=,o= "$TARGET_DIR2/config3_owner.json"

#############################
# TARGET_DIR3
#############################

sudo chown dev:shared_group "$TARGET_DIR3"

#Setup the POSIX Permission Bits/DAC of Directories and Files
chmod u=rwx,g=,o= $TARGET_DIR3
chmod u=rw,g=rw,o=rw "$TARGET_DIR3/config1_open.json"
chmod u=rw,g=rw,o= "$TARGET_DIR3/config2_group.json"
chmod u=rw,g=,o= "$TARGET_DIR3/config3_owner.json"




#for d in "$TARGET_DIR1" "$TARGET_DIR2" "$TARGET_DIR3"; do
#  mkdir -p "$d"
#  cp "$SCRIPT_DIR/config.json" "$d"
#done



echo "Lab 02 setup complete."