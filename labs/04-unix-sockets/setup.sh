#!/usr/bin/env bash
set -euo pipefail
set -x


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi

sudo mkdir -p /run/ipc_test/
sudo chown dev:shared_group /run/ipc_test/

cp "$SCRIPT_DIR/uds_server.py" "/tmp/"
cp "$SCRIPT_DIR/uds_client.py" "/tmp/"




echo "Lab 04 setup complete."


