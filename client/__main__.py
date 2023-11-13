import sys
from pathlib import Path
from multiprocessing import Process

from loguru import logger

from client import capture, cache_handler, model

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <magenta>{level}</magenta> | <magenta>{process}.{module}.{function}</magenta> | <level>{message}</level>")
VIDEO_PATH = Path(sys.argv[1])


def main():
    cap_process: Process | None = None
    mod_process: Process | None = None
    ch_process: Process | None = None

    logger.debug("Starting all processes.")

    try:

        cap = capture.Capture(str(VIDEO_PATH))
        cap_process = cap.get_process()
        cap_process.start()

        logger.debug(f"Started Capture Process with PID: {cap_process.pid}")

        mod = model.AnomalyModel()
        mod_process = mod.get_process()
        mod_process.start()

        logger.debug(f"Started Model Process with PID: {mod_process.pid}")

        ch = cache_handler.CacheHandler()
        ch_process = ch.get_process()
        ch_process.start()

        logger.debug(f"Started Cache Handler Process with PID: {ch_process.pid}.")
        cap_process.join()
        mod_process.join()
        ch_process.join()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        logger.error("Killing all processes.")

        if isinstance(cap_process, Process):
            cap_process.kill()
        if isinstance(mod_process, Process):
            mod_process.kill()
        if isinstance(ch_process, Process):
            ch_process.kill()


if __name__ == "__main__":
    main()
