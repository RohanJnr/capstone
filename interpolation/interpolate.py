import os
import torch
import torchvision
import cv2
import tqdm

import numpy as np
from torchvision.io import read_video
from transforms import ToTensorVideo , Resize

from minio import Minio
import urllib3

import argparse

parser = argparse.ArgumentParser(description='Interpolate frames')

parser.add_argument("--anomaly_id" , type=str , required=True , help="Anomaly ID of the crime")
parser.add_argument("--output_ext" , type=str , help="Output video format" , default=".avi")
parser.add_argument("--input_ext" , type=str, help="Input video format", default=".mp4")
parser.add_argument("--output_fps" , type=int , help="Target FPS" , default=24)

args = parser.parse_args()

anomaly_id = args.anomaly_id
input_ext = args.input_ext

client = Minio('127.0.0.1:9000',
                access_key='minio',
                secret_key='minio123',
                secure=False,
                http_client=urllib3.ProxyManager('http://127.0.0.1:9000')
)

def get_anomaly_clips(anomaly_id):
    """Get anomaly clips for an Anomaly ID from Minio storage."""
    objects = client.list_objects('test', prefix=f'{anomaly_id}/clip_')

    os.makedirs(f'../tmp/{anomaly_id}', exist_ok=True)

    obj_count = 0
    for object in objects:
        file_path = f'../tmp/{object.object_name}'
        client.fget_object('test', object.object_name, file_path)
        obj_count += 1
    
    print(f"Fetched {obj_count} objects for anomaly {anomaly_id}")

get_anomaly_clips(anomaly_id)