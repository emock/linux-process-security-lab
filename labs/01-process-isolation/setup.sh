#!/usr/bin/env bash
set -euo pipefail
set -x




SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi


#############################
# Setup the Directories and Files
#############################

cp "$SCRIPT_DIR/attacker.py" "/tmp/"
cp "$SCRIPT_DIR/fd_visibility.py" "/tmp/"
