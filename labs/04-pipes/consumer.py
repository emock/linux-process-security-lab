from time import sleep

with open("/tmp/demo.fifo", "r") as pipe:
    while True:
        data = pipe.read(1)
        print(data)
        sleep(1)