import subprocess
from pathlib import Path
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import pandas as pd


def calculate_metrics(original_video, interpolated_video):
    print(f"Calculating metrics for {interpolated_video}")
    video1 = cv2.VideoCapture(original_video)
    video2 = cv2.VideoCapture(interpolated_video)
    frame_count = 0
    ssim_sum, psnr_sum = 0, 0

    while True:
        ret1, frame1 = video1.read()
        ret2, frame2 = video2.read()

        if not ret1 or not ret2:
            break

        frame_count += 1

        # Compute SSIM
        met = ssim(frame1, frame2, channel_axis=2)
        ssim_sum += met

        # Compute PSNR
        met = psnr(frame1, frame2)
        psnr_sum += met

    ssim_avg = ssim_sum / frame_count
    psnr_avg = psnr_sum / frame_count

    print(f"SSIM = {ssim_avg}")
    print(f"PSNR = {psnr_avg}")

    return (ssim_avg, psnr_avg)


folder = Path("test", "videos")
date_folder = Path("client/output1")
interpolated_folder = Path("footage")


f = open("logs.txt", "w+")


# order = []

# for file in folder.iterdir():
#     if file.is_file():
#         order.append(file.absolute())
#         subprocess.run(
#             [
#                 "conda",
#                 "run",
#                 "-n",
#                 "anomaly",
#                 "python",
#                 "-m",
#                 "client",
#                 file.absolute(),
#             ],
#             capture_output=True,
#             text=True,
#         )


# for fi in sorted(date_folder.iterdir()):
#     subprocess.run(
#         [
#             "conda",
#             "run",
#             "-n",
#             "flavr",
#             "python",
#             "-m",
#             "interpolation",
#             "--name",
#             fi.stem,
#         ],
#         capture_output=True,
#         text=True,
#     )

# column_names = [
#     "video_name",
#     "input_size",
#     "output_codec",
#     "output_size",
#     "ssim",
#     "psnr",
# ]
# df = pd.read_csv("metrics.csv", header=0)

# for i, fil in enumerate(sorted(interpolated_folder.iterdir())):
#     if fil.is_dir():
#         input_video = folder / f"{fil.name}.mp4"
#         input_size = input_video.stat().st_size / 1e6

#         for _file in fil.iterdir():
#             metrics = calculate_metrics(
#                 str(_file.absolute()), str(input_video.absolute())
#             )
#             row_dict = {
#                 "video_name": fil.stem,
#                 "input_size": input_size,
#                 "output_codec": _file.stem,
#                 "output_size": _file.stat().st_size / 1e6,
#                 "ssim": metrics[0],
#                 "psnr": metrics[1],
#             }
#             df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)

# df.to_csv("metrics.csv", header=True, index=False)

calculate_metrics(
    "/home/ayush/Projects/Capstone/test/videos/Assault009_x264.mp4",
    "/home/ayush/Projects/Capstone/test/videos/Assault009_x264.mp4",
)

f.close()
