import cv2
from multiprocessing import Process, Queue

from client import MPClass
from client.constants import Queues


class Capture(MPClass):
    """Capture frames."""

    def __init__(self, video_stream: int = 0, *, frame_buffer: Queue | None = None) -> None:
        """Init class."""
        self.video_stream = video_stream
        self.queue = frame_buffer or Queues.frame_buffer

    def start_capture(self) -> None:
        """Capture frames using opencv and enqueue."""
        cap = cv2.VideoCapture(self.video_stream)

        while True:
            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (100, 100))
                self.queue.put(frame)

            cv2.imshow('Frame', frame)
            key = cv2.waitKey(1)

            if key == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def start_process(self) -> Process:
        """Start capture process."""
        process = Process(target=self.start_capture)
        return process
