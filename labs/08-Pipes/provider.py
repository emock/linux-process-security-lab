
with open("/tmp/demo.fifo", "w") as pipe:
    pipe.write("hello from Provider")