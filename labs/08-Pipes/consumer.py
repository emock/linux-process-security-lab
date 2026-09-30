
while True:
    with open("/tmp/demo.fifo", "r") as pipe:

        data = pipe.read()
        print(data)