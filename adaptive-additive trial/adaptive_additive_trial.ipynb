# demonstrate some feature access

import detect_heds_module_path
from holoeye import slmdisplaysdk
import numpy as np
import csv
import time
from pypylon import pylon

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()
new_width = camera.Width.GetValue() - camera.Width.GetInc()
if new_width >= camera.Width.GetMin():
    camera.Width.SetValue(new_width)


datafile = open('file.csv', 'r')
datareader = csv.reader(datafile, delimiter=';')
data = []
for row in datareader:
    data.append(row)
data2 = np.asarray(data)
w,h = data2.shape
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
showSLMPreview(slm, scale=0.0)

# Calculate e.g. a vertical blazed grating:
blazePeriod = 77

# Reserve memory for the data:
dataWidth = slm.width_px
dataHeight = slm.height_px
data = slmdisplaysdk.createFieldUChar(dataWidth, dataHeight)

print("dataWidth = " + str(dataWidth))
print("dataHeight = " + str(dataHeight))

# Calculate the data:

##CHange Threshold
Error = 999999999999999999
Threshold = 1
a = 0.5
def error(I_target, I_camera):
    return np.sum((abs(I_target-I_camera))**2)/np.size(I_target)

##Set this appropriately, can load the .npy file into this, and resize probably
TargetIntensity = np.ones((grabResult.Height, grabResult.Width))

numberOfImagesToGrab = 200
camera.StartGrabbingMax(numberOfImagesToGrab)
time_start = time.time()
while camera.IsGrabbing() and (Error>THRESHOLD):
    error = slm.showData(data)
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data.
        img = (inp.asarray(grabResult.Array))**0.5 #.reshape((grabResult.Height, grabResult.Width))
        Error = error(TargetIntensity, img**2)

        ###ADDING FFT in Comment
        #img = np.fft.fftshift(np.fft.fft2(img))

        #img_fb = np.fft.fftshift(np.fft.ifft2(a*img+(1-a)*(TargetIntensity)**0.5))
        img_fb = np.fft.fftshift(np.fft.ifft2((a*img+(1-a)*(TargetIntensity)**0.5)*np.exp(i*data))) # Multiplying phase mask to output electric field amplitude
        img_fb_phase = np.degrees(img_fb)*np.pi/180

        print(img.shape)

        data = img_fb_phase

        #for y in range(dataHeight):
        #    for x in range(dataWidth):
        #        data[y,x] = int(img[int(x/dataHeight*grabResult.Height), int(y/dataWidth*grabResult.Width)])


    time2 = time.time()
    print("TIME: ", time2-time_start)
    ##Wait statements
    #time.sleep(5)
    #input("Press Enter to continue...")

    grabResult.Release()
camera.Close()

# If your IDE terminates the python interpreter process after the script is finished, the SLM content
# will be lost as soon as the script finishes.
# You may insert further code here.
# Wait until the SLM process is closed:
error = slm.utilsWaitUntilClosed()
assert error == ErrorCode.NoError, slm.errorString(error)
# Unloading the SDK may or may not be required depending on your IDE:
slm = None
