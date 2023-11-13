import subprocess
from pathlib import Path
import cv2
from sewar.full_ref import ssim, psnr, msssim
from psnr_hvsm import psnr_hvs_hvsm_np, bt601ycbcr



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

    print(f'SSIM = {ssim_avg}')
    print(f'PSNR = {psnr_avg}')
    print(f'MS-SSIM = {ms_ssim_avg}')
    print(f'PSNR-HVS = {psnr_hvs_avg}')



folder = Path("bulk_test")
date_folder = Path("/home/rohan/dev/capstone/client/anomalies/12 Nov [Sunday], 2023")
interpolated_folder = Path("/home/rohan/dev/capstone/footage")


f = open("logs.txt", "w+")


order = []

for file in folder.iterdir():
    if file.is_file():
        order.append(file.absolute())
        subprocess.run(["conda", "run", "-n", "anomaly","python", "-m", "client", file.absolute()], stdout=f, stderr=f)



for fi in sorted(date_folder.iterdir()):
    subprocess.run(["conda", "run", "-n", "flavr", "python", "-m", "interpolation", "--time", fi.stem], stdout=f, stderr=f)


for i, fil in enumerate(sorted(interpolated_folder.iterdir())):
    if fil.is_dir():
        for _file in fil.iterdir():
            calculate_metrics(str(_file.absolute()), str(order[i]))


f.close()