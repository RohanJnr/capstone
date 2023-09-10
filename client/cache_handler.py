
import secrets
from multiprocessing import Pipe, Process, Queue

from client import MPClass
from client.constants import Cache, Queues, Settings


class AnomalyModel(MPClass):
    """Class representation for anomaly detection model."""

    def __init__(self) -> None:
        """init class."""
        self.anomaly_id: str | None = None
        self.num_blocks_to_persist = 0

        self.block_cache = []

    def prediction_to_cache(self) -> None:
        """Handle frame caching after model prediction and frame sampling,"""
        prediction, sampled_frames = Queues.prediction.get()
        num_max_blocks = Settings.blocks_to_persist()

        if prediction == 1:
            if self.anomaly_id is None:
                self.anomaly_id = secrets.token_hex(4)

            self.num_blocks_to_persist = num_max_blocks

        if len(self.block_cache) == num_max_blocks:
            # Queue is full, store "Cache.num_blocks_to_persist.value" amount in storage.
            blocks = []
            if self.num_blocks_to_persist <= num_max_blocks:
                for _ in range(self.num_blocks_to_persist):
                    blocks.append(self.block_cache.pop(0))

            frames = []
            while not self.block_cache:
                frames.append(Queues.prediction.get()[1])

            frames.append(sampled_frames)
            print("persist.")

        else:
            # Queue is not full.
            pass

    def start_process(self) -> Process:
        """Start process."""
        pass
