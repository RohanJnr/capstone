import cv2


SECONDS_PER_BLOCK = 1

video_path = 'video.mov'

video_capture = cv2.VideoCapture(video_path)
fps = int(video_capture.get(cv2.CAP_PROP_FPS))

frames_per_block = fps * SECONDS_PER_BLOCK

frame_count = 0
frame_cache = []
num_blocks = 0


def persist_frames(frames: list) -> None:
    frame_width = frames[0].shape[1]
    frame_height = frames[0].shape[0]

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"output/output_{num_blocks}.mp4", fourcc, fps, (frame_width, frame_height))

    for _frame in frames:
        out.write(_frame)

    out.release()


while True:
    ret, frame = video_capture.read()

    if not ret:
        break

    frame_cache.append(frame)
    frame_count += 1

    if frame_count == frames_per_block:
        persist_frames(frame_cache.copy())
        frame_cache.clear()
        frame_count = 0
        num_blocks += 1

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


video_capture.release()



