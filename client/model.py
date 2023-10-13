from multiprocessing import Process

import numpy as np
import tensorflow as tf

from client import MPClass
from client.constants import Queues, Settings


class AnomalyModel(MPClass):
    """Class representation for anomaly detection model."""

    def __init__(self) -> None:
        """init class."""
        self.model = tf.keras.models.load_model('modelnew.h5')

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
            x1 = x1.reshape(-1, 640, 360, 3)
            print("done reshaping.")
            yield x1
        

    def predict(self) -> None:
        """Predict if anomaly."""
        frames = []
        for i in range(200):
            frames.append(Queues.frame_buffer.get())

        print("got 200 frames")

        original = np.array(frames).reshape(-1, 128 * 128 * 3)
        test_nn = original.reshape(-1, 128, 128, 3) / 255

        print("starting prediction.")
        prediction = self.model.predict(test_nn, verbose=1)

        prediction = prediction > 0.5
        prediction=int(max(prediction))

        print(f"Prediction: {prediction}")
        sampled_frames = self.frame_sampling(frames)
        # Queues.prediction.put((prediction, sampled_frames))

    def dummy_predict(self) -> None:
        """return randomy numbers."""
        arr = [0, 0, 0, 1, 0, 0, 1]
        idx = 0
        while True:
            frames = []
            for i in range(200):
                frames.append(Queues.frame_buffer.get())

            print("got 200 frames")

            prediction = arr[idx]
            idx += 1

            sampled_frames = self.frame_sampling(frames)
            Queues.prediction.put((prediction, sampled_frames))

    def get_process(self) -> Process:
        """Start process."""
        return Process(target=self.predict)

    def get_dummy(self) -> Process:
        """Start dummy prediction process."""
        return Process(target=self.dummy_predict)
