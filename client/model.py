from multiprocessing import Process

import numpy as np
import tensorflow as tf

import cv2

from client import MPClass
from client.constants import Queues, Settings

tf.config.set_visible_devices([], 'GPU')

class AnomalyModel(MPClass):
    """Class representation for anomaly detection model."""

    @staticmethod
    def frame_sampling(frames) -> list:
        """Return sampled frames from initial set of frames by dropping frames."""
        count = 0
        sampled_frames = []
        for i in frames:
            if count == Settings.frames_to_skip:  # Skip (frames_to_skip) frames and consider 4th frame.
                count = 0
                sampled_frames.append(i)
            else:
                count += 1

        return sampled_frames      

    def predict(self) -> None:
        """Predict if anomaly."""
        model = tf.keras.models.load_model('modelnew.h5')
        while True:
            frames = []
            resized_frames = []
            for i in range(200):
                frame = Queues.frame_buffer.get()
                frames.append(frame)
                resized_frames.append(cv2.resize(frame, (128, 128)))

            print("got 200 frames")

            original = np.array(resized_frames).reshape(-1, 128 * 128 * 3)
            test_nn = original.reshape(-1, 128, 128, 3) / 255

            print("starting prediction.")
            prediction = model.predict(test_nn, verbose=1)

            prediction = prediction > 0.5
            prediction=int(max(prediction))

            print(f"Prediction: {prediction}")
            sampled_frames = self.frame_sampling(frames)
            Queues.prediction.put((prediction, sampled_frames))

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
        prediction_process = Process(target=self.predict)
        prediction_process.start()
        return prediction_process

    def get_dummy(self) -> Process:
        """Start dummy prediction process."""
        return Process(target=self.dummy_predict)
