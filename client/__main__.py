from pathlib import Path

from client import capture, cache_handler, model


VIDEO_PATH = Path("./test/videos/test_again.mp4")


def main():
    try:
        cap = capture.Capture(str(VIDEO_PATH))
        cap_process = cap.get_process()
        cap_process.start()

        mod = model.AnomalyModel()
        mod_process = mod.get_process()

        ch = cache_handler.CacheHandler()
        ch_process = ch.get_process()
        ch_process.start()

        cap_process.join()
        mod_process.join()
        ch_process.join()
    except KeyboardInterrupt:
        cap_process.kill()
        mod_process.kill()
        ch_process.kill()



if __name__ == "__main__":
    main()
