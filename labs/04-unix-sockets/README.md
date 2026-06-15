

1. Run ./setup.sh

## Spoofing

1. Run `python3 uds_server.py`
2. Run `python3 uds_client.py`
3. Connect to the Socket using `socat - UNIX-CONNECT:/run/ipc_test/demo.sock` and send message
{"client_id":"Client_1"} 
