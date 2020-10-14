import detect_heds_module_path
from holoeye import slmdisplaysdk
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
import csv
import time
from pypylon import pylon
import cv2
import copy
import os
from os.path import isfile, join

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
#new_width = camera.Width.GetValue() - camera.Width.GetInc()
#if new_width >= camera.Width.GetMin():
#    camera.Width.SetValue(new_width)

# Make some enumerations available locally to avoid too much code:
ErrorCode = slmdisplaysdk.SLMDisplay.ErrorCode
ShowFlags = slmdisplaysdk.SLMDisplay.ShowFlags

# Initializes the SLM library
slm = slmdisplaysdk.SLMDisplay()

# Check if the library implements the required version
if not slm.requiresVersion(2):
    exit(1)

# Detect SLMs and open a window on the selected SLM
error = slm.open()
assert error == ErrorCode.NoError, slm.errorString(error)

# Open the SLM preview window in "Fit" mode:
# Please adapt the file showSLMPreview.py if preview window
# is not at the right position or even not visible.
from showSLMPreview import showSLMPreview
#showSLMPreview(slm, scale=0.0)

# Reserve memory for the data:
dataWidth = slm.width_px
dataHeight = slm.height_px
data = slmdisplaysdk.createFieldUChar(dataWidth, dataHeight)
#print(data)
print("shape is: ", data.shape)
print("dataWidth = " + str(dataWidth))
print("dataHeight = " + str(dataHeight))

size = (dataHeight,dataWidth)

# Calculate the data:
#data = 2*np.pi*np.random.rand(dataHeight, dataWidth)
data = np.pi*(np.sign(np.random.normal(0,1,size)+1e-7) + 1)/2
print(data)
error = slm.showPhasevalues(data)


def cost(I_target, I_camera):
    return np.sum((abs(I_target-I_camera))**2)/np.size(I_target)

# Set this appropriately, can load the .npy file into this, and resize probably
TargetIntensity = np.load('target_intensity_05_10.npy')

print(TargetIntensity.shape)
plt.imshow(TargetIntensity, cmap='gray', vmin=0, vmax=255)
plt.show()


numberOfImagesToGrab = 30

#data = 2*np.pi*np.random.rand(dataHeight, dataWidth)


count = 0
COST = []
img = []
TIME = []
time_start = time.time()

data2 = slmdisplaysdk.createFieldUChar(shape)
data2 = grating()
error = slm.showPhasevalues(data2) # SHOW GRATING 
camera.StartGrabbingMax(numberOfImagesToGrab)
while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(20000, pylon.TimeoutHandling_ThrowException)
    if grabResult.GrabSucceeded():
        # Access the image data.
        img.append(grabResult.Array)
        TIME.append(time.time())
    else:
        print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
    grabResult.Release()
    count += 1
    #cv2.imwrite('with_phase_06_10/with_phase'+ str(iter) + '.png', img[-1])
    
    
time_end = time.time()
print(data.shape)
print("TIME: ", time_end-time_start)

fps = 1
size = (img[1]).shape
pathOut = 'test_video.avi'
out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

plt.plot(COST)
E = []
for i in range(30):
   COST.append(cost(TargetIntensity, img[i]))
   E.append(np.sum(img[i]))
   gray = cv2.normalize(img[i], None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
   gray_3c = cv2.merge([gray, gray, gray])
   out.write(gray_3c)
   
out.release()
plt.plot(TIME, E)
plt.show()
plt.plot(TIME, COST)
plt.show()
