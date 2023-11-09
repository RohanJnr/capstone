import argparse
import os
import torch
import tqdm

from .model.FLAVR_arch import UNet_3D_3D

from .utils import *


parser = argparse.ArgumentParser(description='Interpolate frames')

parser.add_argument("--date" , type=str , required=True , help="Date of the crime")
parser.add_argument("--time" , type=str , required=True , help="Time of the crime")
parser.add_argument("--output_fps" , type=int , help="Target FPS" , default=30)

args = parser.parse_args()

if os.path.exists(f"tmp/{args.date}/{args.time}"):
    print("Clips already exist, skipping download.")
# else:
#     get_anomaly_clips(args.date, args.time) # Download clips from Minio

# codec_names = ["XVID", "MJPG", "MP4V", "avc1", "VP90", "X264"]
codec_names = ["XVID"]
for codec in codec_names:

    output_video = os.path.abspath(f"footage/{codec}_{args.date}_{args.time}.mp4")

    # Model parameters
    model_name = "unet_18"
    nbr_frame = 4
    joinType = "concat"
    n_outputs = 3
    up_mode = "transpose"

    checkpoint = "interpolation/FLAVR_4x.pth"

    model = UNet_3D_3D(model_name.lower() , n_inputs=4, n_outputs=n_outputs,  joinType=joinType , upmode=up_mode)
    loadModel(model , checkpoint)
    model = model.cuda()

    videoTensor, tensor_size = videos_to_tensor(f"tmp/{args.date}/{args.time}/{codec}")

    idxs = torch.Tensor(range(len(videoTensor))).type(torch.long).view(1,-1).unfold(1,size=nbr_frame,step=1).squeeze(0)
    videoTensor = video_transform(videoTensor, (tensor_size[1], tensor_size[0]))
    print("Video tensor shape is,", videoTensor.shape)

    frames = torch.unbind(videoTensor , 1)
    n_inputs = len(frames)
    width = n_outputs + 1

    outputs = [] ## store the input and interpolated frames

    outputs.append(frames[idxs[0][1]])

    model = model.eval()

    for i in tqdm.tqdm(range(len(idxs))):
        idxSet = idxs[i]
        inputs = [frames[idx_].cuda().unsqueeze(0) for idx_ in idxSet]
        with torch.no_grad():
            outputFrame = model(inputs)   
        outputFrame = [of.squeeze(0).cpu().data for of in outputFrame]
        outputs.extend(outputFrame)
        outputs.append(inputs[2].squeeze(0).cpu().data)

    new_video = [make_image(im_) for im_ in outputs]

    print("Writing to", output_video.split(".")[0] + ".mp4")
    write_video_cv2(new_video , output_video , args.output_fps , tensor_size, codec)
# os.system('ffmpeg -hide_banner -loglevel warning -i %s %s'%(output_video , output_video.split(".")[0] + ".mp4"))
# os.remove(output_video)
