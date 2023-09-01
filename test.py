import cv2
import numpy as np
import multiprocessing
import time
import random
import time
import tensorflow as tf
import os
import sklearn
import pickle

from sklearn.model_selection import StratifiedKFold
from keras.utils import np_utils
# Create a VideoCapture object.
def generatorOurs(frames):

        while True:


                batch_start = 0
                batch_stop = 1

                lx1 = list()

        
                optical_flow = frames

                if len(optical_flow) < 50:
                        while len(optical_flow) < 50:
                                optical_flow.append(optical_flow[-1])
                else:
                        optical_flow = optical_flow[0:50]

                lx1.append(optical_flow)

                x1 = np.array(lx1)
                x1 = x1.astype('float32')
                x1 /= 255
                x1 = x1.reshape((x1.shape[0], 50, 100, 100, 3))

                yield x1

                

# Set the buffer size.


# Create a buffer to store the frames.

def frame_sampling(conn,frames):
    count=0
    l=[]
    for i in frames:
        if count==4:
            count=0
            l.append(i)
        else:
            count+=1
    
    conn.send(l)
        
def read(queue):
  try:
    cap = cv2.VideoCapture(0)
  # Start capturing frames from the video.
    while True:
      # Read the next frame from the video.
      ret, frame = cap.read()

      # If a frame was successfully read, append it to the buffer.
      if ret:
        frame = cv2.resize(frame, (100,100))
        queue.put(frame)

      # If the buffer is full, write it to a file.
      

      # Display the frame.
      cv2.imshow('Frame', frame)

      # Wait for a key press.
      key = cv2.waitKey(1)

      # If the key is ESC, quit the program.
      if key == 27:
        break

    # Release the VideoCapture object.
    cap.release()

    # Close all open windows.
    cv2.destroyAllWindows()
  except KeyboardInterrupt:
      cap.release()

    # Close all open windows.
      cv2.destroyAllWindows()
      print("Ended")
def write(queue,):
  model = tf.keras.models.load_model('model.h5')  
  predictions=[]
  cache=multiprocessing.Queue()
  y=multiprocessing.Value('i',0)
  try:
    block_no=0
    
    while True:
        if queue.qsize()<200:
            time.sleep(4)
        else:
          frames=[]
          
          for i in range(200):
            frames.append(queue.get())
          
          prediction = model.predict(generatorOurs(frames),
                                        steps=1,
                                        max_queue_size=10,
                                        verbose=2)


          prediction = np.argmax(prediction, axis=1)
          print(prediction)
          q = multiprocessing.Process(target=prediction_to_cache, args=(cache,prediction,y))
          pipe=multiprocessing.Pipe()
          r=multiprocessing.Process(target=frame_sampling,args=(pipe[1],frames))
          q.start()
          r.start()
          frames=pipe[0].recv()
          q.join()
          r.join()
          for frame in frames:
            cache.put(frame)
          y=prediction
          print(cache.qsize())
          
          
  except KeyboardInterrupt:
     print("Ended")
def store(frames):
    print("Storage done")
def prediction_to_cache(cache,prediction,value):
    if prediction[0]==1 and cache.qsize()==120:
            frames=[]
            
            while cache.qsize()!=0:
              frames.append(cache.get())
            q = multiprocessing.Process(target=store, args=(frames,))
            q.start()
            print(cache.qsize())
    elif prediction[0]==0:
        if value==1:
            frames=[]
            while cache.qsize()!=0:
              frames.append(cache.get())
            q = multiprocessing.Process(target=store, args=(frames,))
            q.start()
            print(cache.qsize())
        elif value==0:
            if cache.qsize()==120:
              for i in range(40):
                  cache.get()
            
              

            
if __name__ == '__main__':
  queue = multiprocessing.Queue()
  
  p = multiprocessing.Process(target=read, args=(queue,))
  
  # Create a consumer process.
  c = multiprocessing.Process(target=write, args=(queue,))

  # Start the processes.
  p.start()
  c.start()
  try:
        p.join()
        c.join()
  except KeyboardInterrupt:
        print("Sending termination signal to dequeue process...")
          # Signal the dequeue process to stop
        p.join()
        c.join()
        file_path = "output/output_final.avi"

        print(queue.qsize())
           
        print("Both processes terminated.")

  # Wait for the processes to finish.
 
    