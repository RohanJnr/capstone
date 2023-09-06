from multiprocessing import Queue, Value


class Queues:
    frame_buffer = Queue()
    cache = Queue()


class Values:
    prev_prediction = Value("i", 0)
