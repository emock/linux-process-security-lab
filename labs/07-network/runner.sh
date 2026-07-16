#!/usr/bin/env bash


DIR="/home/dev/linux-process-security-lab/labs/07-network/"

NS_CLIENT="ns_client"
NS_SERVER="ns_server"

NAMESPACE="${1:?Namespace missing}"
SCRIPT="${2:?script missing}"

PYTHON="/home/dev/.virtualenvs/linux-process-security-lab/bin/python3"

exec sudo ip netns exec "$NAMESPACE" "$PYTHON" "$DIR/$SCRIPT"