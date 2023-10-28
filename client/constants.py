import math
from multiprocessing import Queue, Value


class Settings:
    time_range = 30  # 120 seconds for before and after anomaly.
    frames_per_block = 200
    fps = 30  # Change value at start.

    frames_to_skip = 3  # Number of frames of skip and consider next frame immediate.

    @classmethod
    def frame_range(cls) -> int:
        return int(cls.time_range * cls.fps)

    @classmethod
    def blocks_to_persist(cls) -> int:
        return math.ceil(cls.frame_range()/cls.frames_per_block)

    @classmethod
    def set_fps(cls, new_fps: int):
        """Set the FPS and recompute dependent values."""
        cls.FPS = new_fps


class Queues:
    frame_buffer = Queue()

    # queue: multiprocessing.Queue[Tuple[int, np.ndarray]]
    prediction = Queue()


class Cache:
    num_blocks_to_persist = Value('i', 0)
