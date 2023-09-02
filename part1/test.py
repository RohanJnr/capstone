import time
from multiprocessing import Process


def something(x):
    print("halo")
    time.sleep(5)
    print("done")


p = Process(target=something, args=(10,))
p.start()

print("continue")
