#!/usr/bin/env bash
set -euo pipefail
set -x

#############################
# Cleanup Directories
#############################

sudo rm -rf /run/ipc_test
rm -rf /tmp/*.py


echo "Lab 04 cleanup complete."
