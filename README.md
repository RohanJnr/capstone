# Smart Storage Solution for surveillance footage with Anomaly Detection and Video Interpolation

### Installation Instructions
This project required a **conda** environment.

Execute the following commands:
```bash
conda create -n project python=3.11
conda activate project
conda install -c conda-forge opencv
pip install tensorflow
pip install loguru
pip install minio
pip install cffi
```

### Running the Project
```bash
python -m client
```
This command will spawn the following 3 Processes:

- **Capture Process**
  - This Process captures the in-coming video and enqueues the frames to the anomaly detection model.
- **Anomaly Model Process**
  - This Process dequeues frames from the queue and checks for the presence of an anomaly in the set of frames.
- **Cache Handler Process**
  - This process is responsible for persisting frames only when an anomaly is detected. The number of frames persist depends on the configuration set in `constants.py`.