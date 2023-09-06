from client.capture import Capture
from client.constants import Queues, Values


def main():

    capture = Capture(queue=Queues.frame_buffer)
    capture_process = capture.start_process()


if __name__ == "__main__":
    main()