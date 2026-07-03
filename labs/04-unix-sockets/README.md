

1. Run ./setup.sh

## Spoofing

1. Run `python3 server.py`
2. Connect to the Socket using `socat - UNIX-CONNECT:/run/ipc_test/demo.sock` and send message
{"method":"uregister", "name":"Client1", "endpoint":"endpoint1"}
3. Run `python3 client.py` and observe the output in server and client terminal



## SO_PEERCRED

1. Run `python3 server.py`
2. Connect to the Socket using `socat - UNIX-CONNECT:/run/ipc_test/demo.sock` and send message
   {"method":"register", "endpoint":"endpoint1"}
3. Run `python3 client.py` and observe the output in server and client terminal


## Bonus: Insecure Server State Handling 

1. Run `python3 server.py`
2. Run `python3 client.py`
3. Connect to the Socket using `socat - UNIX-CONNECT:/run/ipc_test/demo.sock` and send message
{"method":"send", "data":"attackerdata"} and observe the output in server terminal