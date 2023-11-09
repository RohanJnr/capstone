import os
import cv2
from pathlib import Path

def get_video_bitrate(video_path):
    cap = cv2.VideoCapture(video_path)

    # Get frames per second (fps) and frame count
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get duration of the video in seconds
    duration_seconds = frame_count / fps

    # Get bitrate by dividing the file size by the duration
    file_size_bytes = os.path.getsize(video_path)
    bitrate = (8 * file_size_bytes) / duration_seconds  # Convert bytes to bits

    cap.release()

    return bitrate

def main(folder_path):
    path = Path(folder_path)
    for p in path.iterdir():
        if p.is_dir():
            for file in p.iterdir():
                print(f"{p.name}, {file.name}, {get_video_bitrate(str(file.absolute()))//1024} KBPS")

# Example usage:
folder_path = '/home/rohan/dev/capstone/client/anomalies/09 Nov [Thursday], 2023/23:33'
main(folder_path)