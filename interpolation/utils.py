import os
import cv2
import torch
import torchvision

import numpy as np
from torchvision.io import read_video

from .transforms import ToTensorVideo , Resize

# from interpolation import minio_client


# def get_anomaly_clips(date, time):
#     """Get anomaly clips for an Anomaly ID from Minio storage."""
#     objects = minio_client.list_objects('test', prefix=f'{date}/{time}/clip_')

#     os.makedirs(f'../tmp/', exist_ok=True)

#     obj_count = 0
#     for object in objects:
#         file_path = f'../tmp/{object.object_name}'
#         minio_client.fget_object('test', object.object_name, file_path)
#         obj_count += 1
    
#     print(f"Fetched {obj_count} clips for timestamp {date} {time}")

def loadModel(model, checkpoint):
    """Load model from checkpoint."""
    saved_state_dict = torch.load(checkpoint)['state_dict']
    saved_state_dict = {k.partition("module.")[-1]:v for k,v in saved_state_dict.items()}
    model.load_state_dict(saved_state_dict)

def write_video_cv2(frames , video_name , fps , sizes, codec):
    """Write video using OpenCV."""
    out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*codec), fps, sizes)

    for frame in frames:
        out.write(frame)
    
    out.release()
    while out.isOpened():
        pass

def make_image(img):
    """Convert tensor to image."""
    q_im = img.data.mul(255.).clamp(0,255).round()
    im = q_im.permute(1, 2, 0).cpu().numpy().astype(np.uint8)
    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    return im

def videos_to_tensor(clips_path):
    """Convert clips to tensor and combine."""
    clip_tesnors = []

    for clip in sorted(os.listdir(clips_path)):
        clip_path = os.path.join(clips_path, clip)
        video_tensor , _ , meta = read_video(clip_path)
        clip_tesnors.append(video_tensor)

    final_tensor = torch.cat(clip_tesnors, dim=0)
    return final_tensor, (final_tensor.shape[2], final_tensor.shape[1])

def video_transform(videoTensor, tensor_size):
    """Transform video tensor."""
    transforms = torchvision.transforms.Compose([ToTensorVideo(), Resize(tensor_size)])
    return transforms(videoTensor)