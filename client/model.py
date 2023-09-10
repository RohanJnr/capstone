from multiprocessing import Process, Queue

import numpy as np
import tensorflow as tf

from client import MPClass
from client.constants import Queues, Settings


class AnomalyModel(MPClass):
    """Class representation for anomaly detection model."""

    def __init__(self) -> None:
        """init class."""
        self.model = tf.keras.models.load_model('model.h5')

    @staticmethod
    def frame_sampling(frames) -> list:
        """Return sampled frames from initial set of frames by dropping frames."""
        count = 0
        sampled_frames = []
        for i in frames:
            if count == Settings.frames_to_skip:  # Skip (frames_to_skip) frames and consider 5th frame.
                count = 0
                sampled_frames.append(i)
            else:
                count += 1

        return sampled_frames

    @staticmethod
    def generate_optical_flow(frames: list):
        """Convert frames into optical flow."""
        while True:
            list_x1 = []
            optical_flow = frames

            if len(optical_flow) < 50:
                while len(optical_flow) < 50:
                    optical_flow.append(optical_flow[-1])
            else:
                optical_flow = optical_flow[0:50]
            list_x1.append(optical_flow)

            x1 = np.array(list_x1)
            x1 = x1.astype('float32')
            x1 /= 255
            x1 = x1.reshape((x1.shape[0], 50, 100, 100, 3))

            yield x1

    def predict(self) -> None:
        """Predict if anomaly."""
        frames = []
        for i in range(200):
            frames.append(Queues.frame_buffer.get())

        prediction = self.model.predict(
            self.generate_optical_flow(frames),
            steps=1,
            max_queue_size=10,
            verbose=2
        )
        prediction = np.argmax(prediction, axis=1)

        sampled_frames = self.frame_sampling(frames)
        Queues.prediction.put((prediction[0], sampled_frames))

    def start_process(self) -> Process:
        """Start process."""
        return Process(target=self.predict)

