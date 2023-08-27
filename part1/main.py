from multiprocessing import Process

import cv2


SECONDS_PER_BLOCK = 10

# video_path = 'video.mov'

video_capture = cv2.VideoCapture(0)
fps = int(video_capture.get(cv2.CAP_PROP_FPS))

frames_per_block = fps * SECONDS_PER_BLOCK

frame_count = 0
frame_cache = []
num_blocks = 0


def persist_frames(frames: list) -> None:
    frame_width = frames[0].shape[1]
    frame_height = frames[0].shape[0]
    
    file_path = f"output/output_{num_blocks}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(file_path,fourcc, fps, (frame_width, frame_height))

    for _frame in frames:
        out.write(_frame)

    out.release()


print(fps)
process_pool = []

while True:
    ret, frame = video_capture.read()

    if not ret:
        break

    frame_cache.append(frame)
    frame_count += 1
    print(frame_count)

    if frame_count == frames_per_block:
        p = Process(target=persist_frames, args=(frame_cache.copy(),))
        p.start()

        process_pool.append(p)

        frame_cache.clear()

        frame_count = 0
        num_blocks += 1

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


video_capture.release()

for process in process_pool:
    process.join()
