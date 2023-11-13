import subprocess
from pathlib import Path
import sys
import cv2
from skimage.metrics import structural_similarity as ssim


def calc_ssim(video_1, video_2):
    print(f"calculating SSIM between {video_1} - {video_2}")
    video1 = cv2.VideoCapture(video_1)
    video2 = cv2.VideoCapture(video_2)
    c = 0
    s = 0

    while True:
        ret1, frame1 = video1.read()
        ret2, frame2 = video2.read()

        if not ret1 or not ret2:
            break

        # Convert frames to grayscale (if necessary)
        # frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
        # frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        # Compute SSIM
        similarity = ssim(frame1, frame2, channel_axis=2)
        s += similarity
        c += 1

    sim = s/c

    print(f'SSIM between {video_1} - {video_2} = {sim}')


folder = Path("bulk_test")
date_folder = Path("/home/rohan/dev/capstone/client/anomalies/12 Nov [Sunday], 2023")
interpolated_folder = Path("/home/rohan/dev/capstone/footage")


f = open("logs.txt", "w+")


order = []

for file in folder.iterdir():
    if file.is_file():
        order.append(file.absolute())
        subprocess.run(["python", "-m", "client", file.absolute()], stdout=f, stderr=f)



for fi in sorted(date_folder.iterdir()):
    subprocess.run(["conda", "run", "-n", "flavr", "python", "-m", "interpolation", "--time", fi.stem], stdout=f, stderr=f)


for i, fil in enumerate(sorted(interpolated_folder.iterdir())):
    if fil.is_dir():
        for _file in fil.iterdir():
            calc_ssim(str(_file.absolute()), str(order[i]))


f.close()