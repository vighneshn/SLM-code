#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import detect_heds_module_path
from holoeye import slmdisplaysdk
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
#%matplotlib inline
import csv
import time
from pypylon import pylon
import cv2
import cProfile, pstats, io
import sys
import argparse


# In[ ]:


# total arguments 
n = len(sys.argv) 
print("Total arguments passed:", n) 
  
# Arguments passed 
print("\nName of Python script:", sys.argv[0]) 
  
print("\nArguments passed:", end = " ")
for i in sys.argv:
    print(i, end = " ")

number = int(sys.argv[1])
mixing_factor = float(sys.argv[2])
Threshold = float(sys.argv[3])
PAUSE = float(sys.argv[4])


# In[ ]:


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


# In[ ]:


camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()


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
print("\nshape is: ", data.shape)
print("dataWidth = " + str(dataWidth))
print("dataHeight = " + str(dataHeight))

# Calculate the data:
data = 2*np.pi*np.random.rand(dataHeight, dataWidth)
print(data)
error = slm.showPhasevalues(data)


def cost(I_target, I_camera):
    return np.sum((abs(I_target-I_camera))**2)/np.size(I_target)

# Set this appropriately, can load the .npy file into this, and resize probably
TargetIntensity = np.load('target_intensity_05_10.npy')
TargetIntensity[0:1080, 0:400] = 0 # Remove background light

print(TargetIntensity.shape)
plt.imshow(TargetIntensity, cmap='gray', vmin=0, vmax=255)
plt.show()


# In[ ]:


target_phase = np.loadtxt('target_phase_mask.dat.dat')
print(target_phase)
print(target_phase.shape)
plt.imshow(target_phase, cmap='gray', vmin=0, vmax=255)
plt.show()
target_phase = 2*np.pi*target_phase/255


# In[ ]:


#number = 1000
#mixing_factor = 0.5
#Threshold = 1
#PAUSE = 0.005

#@profile
def loopfunc(number, mixing_factor, data, Threshold, PAUSE):
    COST = 9999999999
    numberOfImagesToGrab = number
    count = []
    count.append(0)
    data_init = data
    data_error = []
    data_error.append(cost(data_init, target_phase))
    intensity_error = []
    
    a = mixing_factor
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1) 
    #time_start = time.time()
    
    while count[-1] in range(numberOfImagesToGrab) and (COST>Threshold):
        
        error = slm.showPhasevalues(data)
          
        camera.StartGrabbingMax(1)
        
        while camera.IsGrabbing():
            grabResult = camera.RetrieveResult(20000, pylon.TimeoutHandling_ThrowException)
            
            if grabResult.GrabSucceeded():
                
                # Access the image data.
                img = (np.asarray(grabResult.Array))**0.5 #.reshape((grabResult.Height, grabResult.Width))
                
            else:
                print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
            grabResult.Release()
            
               
        img_sliced = img[4:1084, 64:1984]
        
        img_sliced[0:1080, 0:336]=0
       
        I = img_sliced**2
        
        #cv2.imwrite('with_phase_06_10/with_phase'+ str(iter) + '.png', I)
        
        COST = cost(TargetIntensity, I)
        
        intensity_error.append(COST)
        
        ax.set_xlim(0, count[-1])
    
        ax.cla()
        ax.plot(count, intensity_error)
        display(fig)
    
        clear_output(wait = True)
        plt.pause(PAUSE)
        
        img_fb = np.fft.fftshift(np.fft.ifft2(np.multiply(a*img_sliced+(1-a)*(TargetIntensity)**0.5, np.cos(data) + 1j*np.sin(data)))) # Multiplying phase mask to output electric field amplitude
        
        #img_fb = np.fft.fftshift(np.fft.ifft2(a*img_sliced+(1-a)*(TargetIntensity)**0.5))
        #img_fb_phase = np.angle(img_fb)
        data = np.angle(img_fb)%(2*np.pi)
        
        #data = img_fb_phase
        #data = data%(2*np.pi)
        data_error.append(cost(target_phase, data))
        
        count.append(count[-1]+1)
        #count += 1
        
    
    #time_end = time.time()
    print(data.shape)
    #print("TIME: ", time_end-time_start)
    print("Converged in ", count[-1] , " iterations")
    return data


try:
    #loopfunc(100,0.5, data, COST, Threshold)
    loopfunc(number, mixing_factor, data, Threshold, PAUSE)
    
except KeyboardInterrupt:
    print("Exited loop")
    
    pass

print("Done")


# In[ ]:


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


# In[ ]:




