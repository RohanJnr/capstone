import subprocess
from pathlib import Path
import cv2
from sewar.full_ref import ssim, psnr, msssim
from psnr_hvsm import psnr_hvs_hvsm_np, bt601ycbcr
import pandas as pd


def calculate_metrics(original_video, interpolated_video):
    print(f"Calculating metrics for {interpolated_video}")
    video1 = cv2.VideoCapture(original_video)
    video2 = cv2.VideoCapture(interpolated_video)
    frame_count = 0
    ssim_sum, psnr_sum, ms_ssim_sum = 0, 0, 0
    psnr_hvs_sum, psnr_hvsm_sum = 0, 0

    while True:
        ret1, frame1 = video1.read()
        ret2, frame2 = video2.read()

        if not ret1 or not ret2:
            break

        frame_count += 1

        # Compute SSIM
        met, _ = ssim(frame1, frame2)
        ssim_sum += met
        
        # Compute PSNR
        met = psnr(frame1, frame2)
        psnr_sum += met

        # Compute MS-SSIM
        met = msssim(frame1, frame2)
        ms_ssim_sum += met

        # Compute PSNR-HVS
        frame1, *_ = bt601ycbcr(frame1)
        frame2, *_ = bt601ycbcr(frame2)

        met, met2 = psnr_hvs_hvsm_np(frame1, frame2)
        psnr_hvs_sum += met
        psnr_hvsm_sum += met2

    ssim_avg = ssim_sum / frame_count
    psnr_avg = psnr_sum / frame_count
    ms_ssim_avg = ms_ssim_sum / frame_count
    psnr_hvs_avg = psnr_hvs_sum / frame_count
    psnr_hvsm_avg = psnr_hvsm_sum / frame_count

    print(f'SSIM = {ssim_avg}')
    print(f'PSNR = {psnr_avg}')
    print(f'MS-SSIM = {ms_ssim_avg}')
    print(f'PSNR-HVS = {psnr_hvs_avg}')
    print(f'PSNR-HVS-M = {psnr_hvsm_avg}')

    return (ssim_avg, psnr_avg, ms_ssim_avg, psnr_hvs_avg, psnr_hvsm_avg)



folder = Path("test", "videos")
date_folder = Path("client/output1")
interpolated_folder = Path("footage")


f = open("logs.txt", "w+")


# order = []

# for file in folder.iterdir():
#     if file.is_file():
#         order.append(file.absolute())
#         subprocess.run(["conda", "run", "-n", "anomaly","python", "-m", "client", file.absolute()], stdout=f, stderr=f, capture_output=True, text=True)



for fi in sorted(date_folder.iterdir()):
    subprocess.run(["conda", "run", "-n", "flavr", "python", "-m", "interpolation", "--name", fi.stem], stdout=f, stderr=f)

column_names = ["video_name", "input_size", "output_codec", "output_size", "ssim", "psnr", "ms_ssim", "psnr_hvs", "psnr_hvs_m"]
df = pd.read_csv("metrics.csv", header=0)

for i, fil in enumerate(sorted(interpolated_folder.iterdir())):
    if fil.is_dir():
        input_video = folder/f"{fil.name}.mp4"
        input_size = input_video.stat().st_size

        for _file in fil.iterdir():
            metrics = calculate_metrics(str(_file.absolute()), str(input_video.absolute()))
            row_dict = {"video_name": fil.stem, "input_size": input_size, "output_codec": _file.stem, "output_size": _file.stat().st_size, "ssim": metrics[0], "psnr": metrics[1], "ms_ssim": metrics[2], "psnr_hvs": metrics[3], "psnr_hvs_m": metrics[4]}
            df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)

df.to_csv("metrics.csv", header=True, index=False)

f.close()