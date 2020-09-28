#-*- coding: utf-8 -*-
#--------------------------------------------------------------------#
#                                                                    #
# Copyright (C) 2020 HOLOEYE Photonics AG. All rights reserved.      #
# Contact: https://holoeye.com/contact/                              #
#                                                                    #
# This file is part of HOLOEYE SLM Display SDK.                      #
#                                                                    #
# You may use this file under the terms and conditions of the        #
# "HOLOEYE SLM Display SDK Standard License v1.0" license agreement. #
#                                                                    #
#--------------------------------------------------------------------#

# Shows a 2d matrix of grayscale data with data type uint8 (byte) on the SLM.
# The gray values have a range from 0 to 255, non-fitting values will be wrapped by the data type.
# Import the SLM Display SDK:

import detect_heds_module_path
from holoeye import slmdisplaysdk
import numpy as np
import csv
import time

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

time_start = time.time()
# Calculate the data:
for y in range(dataHeight):
    for x in range(dataWidth):
        data[y,x] = int(data2[int(x/dataHeight*h), int(y/dataWidth*w)])

# Show data on SLM:
error = slm.showData(data)
time2 = time.time()
print("TIME: ", time2-time_start)

##Wait statements
#time.sleep(5)
input("Press Enter to continue...")

assert error == ErrorCode.NoError, slm.errorString(error)

# If your IDE terminates the python interpreter process after the script is finished, the SLM content
# will be lost as soon as the script finishes.
# You may insert further code here.
# Wait until the SLM process is closed:

error = slm.utilsWaitUntilClosed()
assert error == ErrorCode.NoError, slm.errorString(error)
# Unloading the SDK may or may not be required depending on your IDE:
slm = None
