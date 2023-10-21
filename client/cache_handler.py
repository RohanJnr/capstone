import cv2
import io
import pickle
import secrets

from multiprocessing import Process
import numpy as np
from pathlib import Path

from minio import Minio
import urllib3

from client import MPClass
from client.constants import Queues, Settings


client  = Minio('127.0.0.1:9000',
                access_key='minio',
                secret_key='minio123',
                secure=False,
                http_client=urllib3.ProxyManager('http://127.0.0.1:9000')
)

ANOMALIES_FOLDER = Path("client", "anomalies")

class CacheHandler(MPClass):
    """Class representation for anomaly detection model."""

    def __init__(self) -> None:
        """init class."""
        self.anomaly_id: str | None = None
        self.num_blocks_to_persist = 0

        self.block_cache = []

    def persist_blocks_local(self, blocks) -> None:
        """Persist blocks in local storage."""
        output_file = str(ANOMALIES_FOLDER / self.anomaly_id / f'output_video_{secrets.token_hex(6)}.mp4')  # Change the file name and extension as needed
        codec = cv2.VideoWriter_fourcc(*'mp4v')  # You can use other codecs like 'XVID' or 'MJPG'
        fps = 6.0  # Frames per second
        frame_size = (320, 240)  # Set the width and height of your frames here

        out = cv2.VideoWriter(output_file, codec, fps, frame_size)

        for block in blocks:
            for frame in block:
                out.write(frame)   
    
    def persist_blocks(self, blocks) -> None:
        """Persist blocks to minio storage."""
        cache = []
        for block in blocks:
            cache.extend(block)
        cache = np.asarray(cache)

        result = client.put_object('test', f'{self.anomaly_id}/cache_blocks_{secrets.token_hex(6)}', data=io.BytesIO(pickle.dumps(cache)), length=len(pickle.dumps(cache)))
        print("Created {0} object; etag: {1}, version-id: {2}".format(
                result.object_name, result.etag, result.version_id
            )
        )

        
    def prediction_to_cache(self) -> None:
        """Handle frame caching after model prediction and frame sampling,"""
        while True:
            prediction, sampled_frames = Queues.prediction.get()
            num_max_blocks = Settings.blocks_to_persist()

            print(f"-- Prev Cache size: {len(self.block_cache)}")
            print(f"-- Got from prediction queue: {prediction}, {len(sampled_frames)}")

            if prediction == 1:
                if self.anomaly_id is None:
                    self.anomaly_id = secrets.token_hex(4)
                    anomaly_folder = ANOMALIES_FOLDER / self.anomaly_id
                    anomaly_folder.mkdir(exist_ok=True)

                self.num_blocks_to_persist = num_max_blocks

                blocks = []
                while self.block_cache:
                    blocks.append(self.block_cache.pop(0))

                blocks.append(sampled_frames)

                print(f"xx persisting blocks: {len(blocks)}")
                self.persist_blocks_local(blocks)
                continue

            if len(self.block_cache) == num_max_blocks:
                # Queue is full, store "Cache.num_blocks_to_persist.value" amount in storage.

                if not self.anomaly_id:
                    self.block_cache.pop(0)
                    self.block_cache.append(sampled_frames)

                else:
                    blocks = []

                    while self.block_cache and self.num_blocks_to_persist != 0:
                        blocks.append(self.block_cache.pop(0))
                        self.num_blocks_to_persist -= 1

                    print(f"xx Cache full: persisting blocks: {len(blocks)}")
                    self.persist_blocks_local(blocks)

            else:
                # Queue is not full.
                self.block_cache.append(sampled_frames)

            if self.num_blocks_to_persist == 0:
                self.anomaly_id = None

    def get_process(self) -> Process:
        """Start process."""
        return Process(target=self.prediction_to_cache)
