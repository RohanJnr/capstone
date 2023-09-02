from multiprocessing import Process, Queue

import cv2


def persist_frames(frames: list) -> None:
    frame_width = frames[0].shape[1]
    frame_height = frames[0].shape[0]

    file_path = f"output/output_{num_blocks}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(file_path, fourcc, fps, (frame_width, frame_height))

    for _frame in frames:
        out.write(_frame)

    out.release()


def start_opencv():
    pass


if __name__ == "__main__":
    q = Queue()

    p = Process(target=persist_frames, args=(q,))
    p.start()

    cv_process = Process(target=start_opencv, args=(q,))
    cv_process.start()

    cv_process.join()
    p.join()
