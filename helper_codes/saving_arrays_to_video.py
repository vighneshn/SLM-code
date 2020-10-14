import cv2
import numpy as np
import os
from os.path import isfile, join

def Gauss(x,y,w):
    return np.exp(-2*(x**2 + y**2)/(w**2))

x = np.arange(-100,100,1)
y = np.arange(-100,100,1)

X, Y = np.meshgrid(x,y)

img_array = []
fps = 5

w = np.arange(2,200,2)
size = (Gauss(X,Y,1)).shape
#size = (1366,768)
pathOut = 'test_video.avi'
out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

for i in w:
    #img_array.append(Gauss(X,Y,i))
    img = cv2.resize(Gauss(X,Y,i), size)
    #cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    gray = cv2.normalize(img, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    gray_3c = cv2.merge([gray, gray, gray])
    out.write(gray_3c)
    #out.write(img)

out.release()

# END OF MAIN CODE - WHAT FOlLOWS THIS COMMENT IS NOT REQUIRED



pathIn= './images/testing/'
pathOut = 'test_video.avi'
fps = 0.5
frame_array = []



for img in img_array:
    size = img.shape
    
    #inserting the frames into an image array
    frame_array.append(img%256)
out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
for i in range(len(frame_array)):
    # writing to a image array
    out.write(frame_array[i])
out.release()
