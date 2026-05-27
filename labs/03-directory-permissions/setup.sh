#!/usr/bin/env bash
set -euo pipefail
set -x

#rwx
TARGET_DIR1="/tmp/lab-03-s1-700"
#rw-
TARGET_DIR2="/tmp/lab-03-s2-600"
#r-x
TARGET_DIR3="/tmp/lab-03-s3-500"
#r--
TARGET_DIR4="/tmp/lab-03-s4-400"
#-wx
TARGET_DIR5="/tmp/lab-03-s5-300"
#-w-
TARGET_DIR6="/tmp/lab-03-s6-200"
#--x
TARGET_DIR7="/tmp/lab-03-s7-100"
#---
TARGET_DIR8="/tmp/lab-03-s8-000"


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi



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

mkdir -p "$TARGET_DIR7"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR7/config.json"

mkdir -p "$TARGET_DIR8"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR8/config.json"



sudo chown -R dev:shared_group /tmp/lab-03-s*


#############################
# Setting permissions
#############################

#rwx
chmod u=,g=,o= "$TARGET_DIR1/config.json"
chmod u=rwx,g=,o= $TARGET_DIR1

#rw-
chmod u=,g=,o= "$TARGET_DIR2/config.json"
chmod u=rw,g=,o= $TARGET_DIR2

#r-x
chmod u=,g=,o= "$TARGET_DIR3/config.json"
chmod u=rx,g=,o= $TARGET_DIR3

#r--
chmod u=,g=,o= "$TARGET_DIR4/config.json"
chmod u=r,g=,o= $TARGET_DIR4

#-wx
chmod u=,g=,o= "$TARGET_DIR5/config.json"
chmod u=wx,g=,o= $TARGET_DIR5

#-w-
chmod u=,g=,o= "$TARGET_DIR6/config.json"
chmod u=w,g=,o= $TARGET_DIR6

#--x
chmod u=,g=,o= "$TARGET_DIR7/config.json"
chmod u=x,g=,o= $TARGET_DIR7

#---
chmod u=,g=,o= "$TARGET_DIR8/config.json"
chmod u=,g=,o= $TARGET_DIR8


echo "Lab 03 setup complete."


