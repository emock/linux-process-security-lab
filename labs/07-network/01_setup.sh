#!/usr/bin/env bash

set -euxo pipefail

# Create the network namespaces
sudo ip netns add ns_client
sudo ip netns add ns_server


sudo ip link add veth-client type veth peer name veth-server


# Move veth-client and veth-server into the corersponding namespaces
#ns_client                     ns_server
#
#veth-client <===============> veth-server
sudo ip link set veth-client netns ns_client
sudo ip link set veth-server netns ns_server



# Assign IP Addresses

sudo ip netns exec ns_client \
    ip addr add 10.10.0.1/24 dev veth-client

sudo ip netns exec ns_server \
    ip addr add 10.10.0.2/24 dev veth-server


# All interfaces are down, activate it

sudo ip netns exec ns_client \
    ip link set veth-client up

sudo ip netns exec ns_server \
    ip link set veth-server up


sudo ip netns exec ns_client ip link set lo up
sudo ip netns exec ns_server ip link set lo up



# Test

sudo ip netns exec ns_client ping -c 3 10.10.0.2
sudo ip netns exec ns_server ping -c 3 10.10.0.1