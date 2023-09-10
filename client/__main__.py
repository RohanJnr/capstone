from client.capture import Capture
from client.constants import Queues


def main():
    capture = Capture()
    capture_process = capture.start_process()


if __name__ == "__main__":
    main()
