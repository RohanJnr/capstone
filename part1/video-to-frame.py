import sys
import cv2

VIDEO_PATH = sys.argv[1]
FRAMES_PATH = sys.argv[2]

capture = cv2.VideoCapture(VIDEO_PATH)
frameCounter = 0

while(True):
    success, frame = capture.read()
    if success:
        cv2.imwrite(f"{FRAMES_PATH}/frame_{frameCounter}.jpg",frame)

    else:
        break
    frameCounter += 1
capture.release()
