import urllib3
from datetime import datetime
from multiprocessing import Process
from pathlib import Path

import cv2
from minio import Minio
from loguru import logger

from client import MPClass
from client.constants import Queues, Settings


client = Minio('127.0.0.1:9000',
    access_key='minio',
    secret_key='minio123',
    secure=False,
    http_client=urllib3.ProxyManager('http://127.0.0.1:9000')
)

ANOMALIES_FOLDER = Path("client", "anomalies")
DAY_FOLDER_STRFTIME = "%d %b [%A], %Y"
TIME_FOLDER_STRFTIME = "%H:%M"


class CacheHandler(MPClass):
    """Class representation for anomaly detection model."""

    def __init__(self) -> None:
        """init class."""
        self.anomaly_id: datetime | None = None
        self.num_blocks_to_persist = 0

        self.block_cache = []
        self.block_counter = 0
    
    def persist_blocks(self, blocks) -> None:
        """Persist blocks to minio storage."""
        clip_name = f'clip_{self.block_counter}.mp4'
        self.block_counter += 1

        anomaly_day_folder = self.anomaly_id.strftime(DAY_FOLDER_STRFTIME)
        anomaly_time_folder = self.anomaly_id.strftime(TIME_FOLDER_STRFTIME)
        codec_names = ["XVID", "MJPG", "MP4V", "avc1", "VP90", "X264"]

        for codec_name in codec_names:
            logger.info(f"TRYING CODEC: {codec_name}")
            try:
                output_file = Path(ANOMALIES_FOLDER, anomaly_day_folder, anomaly_time_folder, codec_name, clip_name)
                output_file.parent.mkdir(parents=True, exist_ok=True)

                codec = cv2.VideoWriter_fourcc(*codec_name)  # You can use other codecs like 'XVID' or 'MJPG'
                fps = 6.0  # Frames per second

                height, width, _ = blocks[0][0].shape

                frame_size = (width, height)  # Set the width and height of your frames here


                out = cv2.VideoWriter(str(output_file), codec, fps, frame_size)

                logger.debug(f"Persisting Clip {output_file}")

                for block in blocks:
                    for frame in block:
                        out.write(frame)

                out.release()
                while out.isOpened():
                    pass

                # try:
                #     result = client.fput_object(
                #         'test',
                #         f'{anomaly_day_folder}/{anomaly_time_folder}/{clip_name}',
                #         output_file.absolute(),
                #         content_type="video/mp4"
                #     )
                #     logger.debug(f"Created {result.object_name} object.")
                # except Exception as e:
                #     logger.error(e)
            except Exception as e:
                logger.error(f"Got error using codec: {codec_name} - {e}")
                
    def prediction_to_cache(self) -> None:
        """Handle frame caching after model prediction and frame sampling,"""
        logger.debug(f"Cache handler started: {Settings.blocks_to_persist()}")
        while True:
            prediction, sampled_frames = Queues.prediction.get()
            num_max_blocks = Settings.blocks_to_persist()

            logger.debug(f"Cache size: {len(self.block_cache) + 1}")

            if prediction == 1:
                logger.warning(f"Got from prediction queue: {prediction}, {len(sampled_frames)} Frames")
                if self.anomaly_id is None:
                    self.anomaly_id = datetime.now()
                    anomaly_day_folder = self.anomaly_id.strftime(DAY_FOLDER_STRFTIME)
                    anomaly_time_folder = self.anomaly_id.strftime(TIME_FOLDER_STRFTIME)

                    anomaly_folder = ANOMALIES_FOLDER / anomaly_day_folder / anomaly_time_folder
                    anomaly_folder.mkdir(parents=True, exist_ok=True)

                self.num_blocks_to_persist = num_max_blocks

                blocks = []
                while self.block_cache:
                    blocks.append(self.block_cache.pop(0))

                blocks.append(sampled_frames)

                logger.debug(f"Persisting blocks: {len(blocks)}")
                self.persist_blocks(blocks)
                continue

            logger.debug(f"Got from prediction queue: {prediction}, {len(sampled_frames)} Frames")

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

                    logger.warning(f"Cache full: persisting blocks: {len(blocks)}")
                    self.persist_blocks(blocks)

            else:
                # Queue is not full.
                self.block_cache.append(sampled_frames)

            if self.num_blocks_to_persist == 0:
                self.anomaly_id = None
                self.block_counter = 0
                logger.debug("No Anomaly")

    def get_process(self) -> Process:
        """Start process."""
        return Process(target=self.prediction_to_cache)
