#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/home/dev/lab-02-config"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(id -un)" != "dev" ]]; then
  echo "Please run this script as user 'dev'."
  exit 1
fi

mkdir -p "$TARGET_DIR"
cp "$SCRIPT_DIR/config.json" "$TARGET_DIR/config.json"

echo "Lab 02 setup complete."
echo "Config deployed to: $TARGET_DIR/config.json"