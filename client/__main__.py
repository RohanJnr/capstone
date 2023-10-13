from pathlib import Path

from client import capture, cache_handler, model
from client.constants import Queues


VIDEO_PATH = Path("test/videos/one.mp4")


def main():


    mod = model.AnomalyModel()
    mod_process = mod.get_process()
    mod_process.start()

    cap = capture.Capture(str(VIDEO_PATH))
    cap_process = cap.get_process()

    cap_process.start()


    ch = cache_handler.CacheHandler()
    ch_process = ch.get_process()

    ch_process.start()



if __name__ == "__main__":
    main()
