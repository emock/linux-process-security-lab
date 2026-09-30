
with open("/tmp/demo.fifo", "w") as pipe:
    pipe.write("1")
    pipe.write("1")
    pipe.write("hello")
    pipe.write("1")