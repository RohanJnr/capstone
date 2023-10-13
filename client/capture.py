from pathlib import Path
from multiprocessing import Process

import cv2


from client import MPClass
from client.constants import Queues


class Capture(MPClass):
    """Capture frames."""

    def __init__(self, video_stream: int | str = 0) -> None:
        """Init class."""
        self.video_stream = video_stream
        self.queue = Queues.frame_buffer

    def start_capture(self) -> None:
        """Capture frames using opencv and enqueue."""
        cap = cv2.VideoCapture(self.video_stream)

        while cap.isOpened():
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (128, 128))
                self.queue.put(frame)

                cv2.imshow('Frame', frame)
                # Press Q on keyboard to exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            else:
                break
        cap.release()
        cv2.destroyAllWindows()

    def get_process(self) -> Process:
        """Start capture process."""
        process = Process(target=self.start_capture)
        return process
