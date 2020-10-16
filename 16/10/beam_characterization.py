#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from os.path import isfile, join
import sys
import argparse
import detect_heds_module_path
from holoeye import slmdisplaysdk
import numpy as np
import matplotlib.pyplot as plt
#%matplotlib inline
import csv
import time
from pypylon import pylon
import cv2
import cProfile, pstats, io

# TAKING COMMAND LINE ARGUMENTS

# total arguments 
n = len(sys.argv) 
print("Total arguments passed:", n) 
  
# Arguments passed 
print("\nName of Python script:", sys.argv[0]) 
  
print("\nArguments passed:", end = " ")
for i in sys.argv:
    print(i, end = " ")

date = str(sys.argv[1])
month = str(sys.argv[2])
datemonth = date + '_' + month

# CREATING OUTPUT FOLDER TO STORE DATA

main_dir = "beamchar_" + datemonth
os.mkdir(main_dir)


# DEFINING HORIZONTAL BINARY GRATING FUNCTION
def grating(shape):
    mask = np.zeros(shape)
    
    idx = [2*i for i in range(shape[0]//2)]
    mask[idx,:]=128
    
    return mask
###############################################


# EXPERIMENT TO CAPTURE TARGET IMAGE

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

data_init = slmdisplaysdk.createFieldUChar(dataWidth,dataHeight)

size = data_init.shape
print("\nShape of the grating to capture the target image is: ", data_init.shape)
print("dataWidth = " + str((data_init.shape)[1]))
print("dataHeight = " + str((data_init.shape)[0]))

# Calculate the data:

data_init = 2*np.pi*grating(data_init.shape)/256
print("Phase values to be shown are: ")
print(data_init)
error = slm.showPhasevalues(data_init)

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

#camera.OffsetX.SetValue(600)
#camera.OffsetY.SetValue(0)
#camera.Width.SetValue(2048-600)
#camera.Height.SetValue(1088-88)

numberOfImagesToGrab = 1
camera.StartGrabbingMax(numberOfImagesToGrab)

while camera.IsGrabbing():
   
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data.
        img = np.asarray(grabResult.Array) #.reshape((grabResult.Height, grabResult.Width))
        
        print("Shape of the target image is: ", img.shape)

        

    grabResult.Release()
    

camera.Close()

np.save(main_dir + "/targetchar_" + datemonth, img)
img = np.load(main_dir + "/targetchar_" + datemonth + '.npy')

figtarget, axtarget = plt.subplots(1,2)

figtarget.tight_layout(pad=4)
figtarget.suptitle("Captured target")

axtarget[0][0].imshow(data_init, cmap='gray')
axtarget[0][0].set_title("Horizontal binary grating")
axtarget[0][0].set_xlabel("Column number")
axtarget[0][0].set_ylabel("Row number")
axtarget[0][0].colorbar()
axtarget[0][1].imshow(img, cmap='gray')
axtarget[0][1].set_title("Target image")
axtarget[0][1].colorbar()

figtarget.savefig(main_ dir + "/targetexpt_" + datemonth + ".png")

print("Shape of the saved target image is: ", img.shape)
plt.show(block=False)


def profile(fnc):
    
    """A decorator that uses cProfile to profile a function"""
    
    def inner(*args, **kwargs):
        
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


#### EXPERIMENT TO FIND LOCATION OF THE LASER SPOT USING THE TARGET IMAGE CAPTURED ABOVE

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

TargetIntensity = np.load(main_dir + "/targetchar_" + datemonth + '.npy')
plt.imshow(TargetIntensity, cmap='gray', vmin=0, vmax=255)
print("The dimensions of the target image captured by the camera are: ", TargetIntensity.shape)
plt.show(block=False)

# Defining cost function to be used
def cost(I_target, I_camera):
    return np.sum((I_target-I_camera)**2)/np.size(I_target)

# Putting the blackening sequence in a function which is called repeatedly

def loopfunc(shape, number):
    
    numberOfImagesToGrab=0
    count = 0
    img = 0
        
    target=TargetIntensity
    intensity_error = []
    phase = slmdisplaysdk.createFieldUChar(shape[1], shape[0])
    phase = 2*np.pi*grating(shape)/256
    if number == 0:
        numberOfImagesToGrab = shape[0]
    elif number == 1:
        numberOfImagesToGrab = shape[0]
    elif number == 2:
        numberOfImagesToGrab = shape[1]
    elif number == 3:
        numberOfImagesToGrab = shape[1]
     
    while count in range(numberOfImagesToGrab):
        
        if number == 0:
            phase[:count, :] = 0
                        
        elif number == 1:
            phase[shape[0] - count:, :] = 0
            
        elif number == 2:
            phase[:, :count] = 0
            
        elif number == 3:
            phase[:, shape[1] - count:]=0
            
            
        error = slm.showPhasevalues(phase)
          
        time.sleep(0.2) # Accounting for the time delay for a frame to be shown on the SLM screen
        
        camera.StartGrabbingMax(1)
        
        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(20000, pylon.TimeoutHandling_ThrowException)
            
            if grabResult.GrabSucceeded():
                
                # Access the image data.
                
                img = grabResult.Array
                
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
            
        intensity_error.append(cost(target, img))
        #count += 1
        count += 10
        
    return intensity_error


# CALLING FUNCTION TO BEGIN DATA ACQUISITION

ERROR = []
for i in range(4):
    ERROR.append(loopfunc(data_init.shape, i))
    
np.save(main_dir + "/beamchar_" + datemonth, ERROR)

# DATA PROCESSING AS WELL AS CREATING AND SAVING PLOTS

x = np.arange(0, 10*len(ERROR[2]),10)
y = np.arange(0, 10*len(ERROR[0]),10)
a = np.flip(ERROR[1]
b = np.flip(ERROR[3])
            
figchar, axchar = plt.subplots(2,1)

figchar.set_size_inches(12, 9)
figchar.tight_layout(pad=3.0)
figchar.suptitle("Error plots for steps of 108 and 192")
figchar.subplots_adjust(top=0.88)

axchar[0].plot(y, a, label='Bottom to top')
axchar[0].plot(y, ERROR[0], label='Top to bottom')
axchar[0].set_xlabel("Row number")
axchar[0].set_ylabel("Error in intensity")
axchar[0].legend()

axchar[1].plot(x, b, label='Right to left')
axchar[1].plot(x, ERROR[2], label='Left to right')
axchar[1].set_xlabel("Column number")
axchar[1].set_ylabel("Error in intensity")
axchar[1].legend(loc='upper right', bbox_to_anchor=(0.8, 0.5))

figchar.savefig(main_dir + "/charplots_" + datemonth + ".png")
plt.show(block=False)


# FINDING OUT THE POSITION OF THE CENTER OF THE LASER BEAM

plot1 = abs(a-ERROR[0])
plot2 = abs(b-ERROR[2])

figdiff, axdiff = plt.subplots(2,1)

figdiff.suptitle("Difference in error of opposite directions of blackening", fontsize=20)
figdiff.tight_layout(pad=3)

axdiff[0].plot(y, plot1)
axdiff[0].set_xlabel("Row number", fontsize=15)
axdiff[0].set_ylabel("Error difference", fontsize=15)
axdiff[0].set_title("Difference in errors when blackened from top to bottom and bottom to top", fontsize=15)
axdiff[1].plot(x, plot2)
axdiff[1].set_xlabel("Column number", fontsize=15)
axdiff[1].set_ylabel("Error difference", fontsize=15)
axdiff[1].set_title("Difference in errors when blackened from right to left and left to right", fontsize=15)

figdiff.savefig(main_dir + "/diffplots_" + datemonth + ".png")
figdiff.draw()

z = []
for i in range(len(y)):
    temp = []
    for j in range(len(x)):
        temp.append(plot1[i]*plot2[j])
    z.append(temp)
    
plt.pcolor(x, y, z, cmap='gray')
plt.gca().invert_yaxis()
plt.xlabel("Column number")
plt.ylabel("Row number")
plt.title("Plot to locate center of laser beam")
plt.colorbar()
plt.savefig(main_dir + "/spotloc_" + datemonth + ".png")
plt.show(block=False)

plt.show()

# CLOSING DOWN THE INSTRUMENTs

camera.Close()

# If your IDE terminates the python interpreter process after the script is finished, the SLM content
# will be lost as soon as the script finishes.
# You may insert further code here.
slm.close()
# Wait until the SLM process is closed:
error = slm.utilsWaitUntilClosed()
assert error == ErrorCode.NoError, slm.errorString(error)
# Unloading the SDK may or may not be required depending on your IDE:
slm = None

