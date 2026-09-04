# Setup
Before doing any lab:
- Run script ./01_setup.sh to setup the lab environment

# Scenario 1: Unprivileged local attacker

- Start the server process using: ./runner.sh ns_server server.py
- Start a client using: sudo ip netns exec ns_server nc -u 127.0.0.1 5000
  - Type messages in the client shell; these will appear in the server console 
- Start the attacker using: ./runner.sh ns_server 01_attacker_unprivileged.py   

# Scenario 2: Unprivileged local attacker

- Run script 02_setup_mitm.sh: This grants the CAP_NET_RAW capability
- Start the server process using: ./runner.sh ns_server server.py
- Start the attacker using: ./runner.sh ns_server 02_attacker.py
- Start a client using: sudo ip netns exec ns_server nc -u 10.10.0.2 5000
  - Type messages in the client shell; these will appear in the server console



# Cleanup
- Run ./cleanup.sh to reverse any changes made in the lab environment

