sudo ip netns delete ns_client
sudo ip netns delete ns_server


ip netns list

sudo setcap -r /usr/bin/python3.12