#!/usr/bin/env python
# coding: utf-8

# In[2]:


### IMPORTING REQUISITE PACKAGES

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication

import detect_heds_module_path
from holoeye import slmdisplaysdk

import numpy as np
import threading
import time
import copy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import csv
import sip
from pypylon import pylon
import cv2
import cProfile, pstats, io
import scipy as sp
from scipy.signal import *
import os
from os.path import isfile, join
import random
from random import randint
import ising_helper2
from ising_helper2 import *


# In[1]:





# In[3]:




# sample the colormaps that you want to use. Use 128 from each so we get 256
# colors in total
colors1 = plt.cm.binary(np.linspace(0., 1, 128))
colors2 = plt.cm.gist_heat_r(np.linspace(0, 1, 128))

# combine them and build a new colormap
colors = np.vstack((colors1, colors2))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)




loss_arr = []
loss_arr.append(255)
fidelity_arr = []
fidelity_arr.append(0.01)
spinflip = []

filepath = ''
number_part = []
x = []
mask = []
eta0 = 0
N = 0
RUN = 0
bins = 2**3

outer_bins = 2**4
size = 0
d = 2**2
numbers_shape = 2**6
numbers = np.random.uniform(0, 1, (numbers_shape,numbers_shape))
numbers = (numbers*1000).astype(int)
print(numbers)
np.savetxt("numbers.csv", numbers, delimiter=',')
mask_temp1=[]


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setLabel('left', "Fidelity")
        self.graphWidget.setLabel('bottom', "Iteration number")
        #self.setCentralWidget(self.graphWidget)

        self.X = list(range(100))  # 100 time points
        self.y = [0 for _ in range(100)]  # 100 data points
        #self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        #self.data_line =  self.graphWidget.plot(self.X, self.y, pen=pen)

        ###

        self.cmapWidget = pg.ImageView()
        self.imagedata = self.cmapWidget.setImage(np.ones((100,100)))
        #self.imagedata = self.cmapWidget.setImage(np.random.randint(0,100, (100,100)))

        self.cmapWidget.ui.histogram.hide()
        self.cmapWidget.ui.roiBtn.hide()
        self.cmapWidget.ui.menuBtn.hide()

        self.p1 = self.graphWidget.plotItem
        self.p1.setLabels(left='Fidelity')

        self.p2 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p2)
        self.p1.getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.p1)
        self.p1.getAxis('right').setLabel('Hamiltonian', color='#0000ff')

        #self.imagedata = pg.Image(np.random.randint(0,100, (100,100)))
        widget = QtWidgets.QWidget()
        #self.graphWidget.setGeometry(50,50,100,100)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.graphWidget, 1,0, 7,1)
        self.layout.addWidget(self.cmapWidget, 1,1, 1,2)

        self.fidelity_disp = QtWidgets.QLabel()
        self.fidelity_disp.setText("Fidelity: "+str(1))
        self.layout.addWidget(self.fidelity_disp)

        #self.buttonwidget = QtWidgets.QPushButton('Click')
        #self.buttonwidget.clicked.connect(self.on_button_clicked)
        #self.buttonwidget.resize(100,40)

        #self.plotbg = pg.plot()
        #self.bg = pg.BarGraphItem(x = [1,2], height = np.asarray([1,4]), width = 0.1, brush ='g')
        #self.plotbg.addItem(self.bg)
        #self.layout.addWidget(self.plotbg,1,3)

        #self.buttonwidget.clicked.connect(threading.Thread(target=self.on_button_clicked).start)
        #self.buttonwidget.show()
        #self.layout.addWidget(self.buttonwidget, 7,1)

        self.buttonwidget2 = QtWidgets.QPushButton('Load File')
        self.buttonwidget2.clicked.connect(self.on_button_clicked2)
        self.buttonwidget2.resize(100,40)
        #self.buttonwidget2.clicked.connect(threading.Thread(target=self.on_button_clicked2).start)
        self.layout.addWidget(self.buttonwidget2, 2, 1)

        self.buttonwidget3 = QtWidgets.QPushButton('Close Window')
        self.buttonwidget3.clicked.connect(self.on_button_clicked3)
        self.buttonwidget3.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget3, 4,2)


        self.buttonwidget4 = QtWidgets.QPushButton("Start/Continue Run")
        self.buttonwidget4.clicked.connect(self.on_button_clicked4)
        self.buttonwidget4.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget4, 3,1)

        self.layout.setColumnStretch(0,6)
        self.layout.setColumnStretch(1,2)
        self.layout.setColumnStretch(2,2)

        self.buttonwidget5 = QtWidgets.QPushButton("Pause Run")
        self.buttonwidget5.clicked.connect(self.on_button_clicked5)
        self.buttonwidget5.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget5, 3,2)

        self.buttonwidget6 = QtWidgets.QPushButton("Stop Run")
        self.buttonwidget6.clicked.connect(self.on_button_clicked6)
        self.buttonwidget6.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget6, 4,1)
        
        self.buttonwidget7 = QtWidgets.QPushButton("Set Exposure Time")
        self.buttonwidget7.clicked.connect(self.on_button_clicked7)
        self.buttonwidget7.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget7, 2,2)
        
        self.buttonwidget8 = QtWidgets.QPushButton("Set d value")
        self.buttonwidget8.clicked.connect(self.on_button_clicked8)
        self.buttonwidget8.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget8, 2,3)

        
        number_shape, done = QtWidgets.QInputDialog.getInt(self, 'Input Dialog', 'Enter side of 2d grid of numbers to be partitioned:')
        numbers = np.random.uniform(0, 1, (numbers_shape,numbers_shape))
        numbers = (numbers*1000).astype(int)
        print(numbers)
        np.savetxt("numbers.csv", numbers, delimiter=',')


        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        ###

        ###

        # setting title
        self.setWindowTitle("Number Partitioning Solver")

        # setting geometry
        self.setGeometry(100, 100, 800, 800)
        # showing all the widgets
        self.show()

        ###

        # ... init continued ...

    def updateViews(self):
        ## view has resized; update auxiliary views to match
        #global p1, p2, p3
        self.p2.setGeometry(self.p1.vb.sceneBoundingRect())

        ## need to re-update linked axes since this was called
        ## incorrectly while views had different shapes.
        ## (probably this should be handled in ViewBox.resizeEvent)
        self.p2.linkedViewChanged(self.p1.vb, self.p2.XAxis)

    def update_plot_data2(self):
        global x

        x2 = flip2(x,x.shape,bins,1)
        prev_loss, val = loss_notarget(np.exp(1j*((x+mask))))

        loss2,_ = loss_notarget(np.exp(1j*((x2+mask))))
        if loss2 < prev_loss:
            x = x2
            loss_arr.append(loss2)
        else:
            x = x
            loss_arr.append(prev_loss)


        idxp = np.where(x!=0.0)
        idxn = np.where(x==0.0)

        sump = np.sum(abs(mask[idxp]))
        sumn = np.sum(abs(mask[idxn]))
        fidelity_arr.append(abs(sump-sumn)/(sump+sumn))
        time.sleep(0.15)
        thread1 = threading.Thread(target=self.threading_test)
        thread1.start()
        thread1.join()
    
    def update_plot_data(self):
        global x

        if RUN==1:
            x2 = flip2(x,x.shape,bins,1)
            prev_loss, val = loss_notarget(np.exp(1j*((x+mask))))

            loss2,_ = loss_notarget(np.exp(1j*((x2+mask))))
            if loss2 < prev_loss:
                x = x2
                loss_arr.append(loss2)
            else:
                x = x
                loss_arr.append(prev_loss)


            idxp = np.where(x!=0.0)
            idxn = np.where(x==0.0)

            sump = np.sum(abs(mask[idxp]))
            sumn = np.sum(abs(mask[idxn]))
            fidelity_arr.append(abs(sump-sumn)/(sump+sumn))
            time.sleep(0.15)
            thread1 = threading.Thread(target=self.threading_test)
            thread1.start()
            thread1.join()
            
    def update_expt_plot(self):
        global x

        if RUN==1:
            x2 = flip_np(self.spin_arr, x, self.area, self.active_area, bins, d)
            error = self.slm.showPhasevalues(x2+mask)
            thread1 = threading.Thread(target=self.threading_test)
            thread1.start()
            thread1.join()
            time.sleep(0.15)
            
            self.camera.StartGrabbingMax(1)
        
            while self.camera.IsGrabbing():
            # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                    # Access the image data.
                    #img = rebin(grabResult.Array, imgbin)
                    img = (grabResult.Array)[124:132,124:132]

                else:
                    print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                grabResult.Release()

            #C1 = cost(target, img)
            #C1 = np.sum(img[247:263,247:263])*1.0
            C1 = np.sum(img)/np.size(img)
            #ham.append(hamiltonian(C1, target, img))
            delE = C1 - loss_arr[-1]
            #print(C1, COST[-1], delE)

            p = np.exp(-1*self.beta[self.count]*delE)                


            if delE <= 0:
                x=x2
                #print("Accepted")
                loss_arr.append(C1)
                spinflip.append(d)
            elif np.random.choice(a=[0,1], p=[p, 1-p])==0:
                x=x2
                loss_arr.append(C1)
                spinflip.append(d)
            else:
                x=x
                loss_arr.append(loss_arr[-1])
                spinflip.append(0)
                #d *= 2

            self.count += 1
            #ham.append(C1)
            #beta -= 0.1
            #beta += 0.1
            #writevideo(data, out)
            final_screen = x[(self.area[0]-self.active_area[0])//2:(self.area[0]+self.active_area[0])//2, (self.area[1]-self.active_area[1])//2:(self.area[1]+self.active_area[1])//2]


            s1 = np.where(final_screen < np.pi)
            s2 = np.where(final_screen >= np.pi)
            fidelity = (np.sum(number_part[s1])-np.sum(number_part[s2]))/(np.sum(number_part[s1])+np.sum(number_part[s2]))
            fidelity_arr.append(fidelity)
            
           
    
    ###
    def on_button_clicked(self):
        self.alert = QtWidgets.QMessageBox()
        self.alert.setText('You clicked the button!')
        self.alert.exec_()

    def on_button_clicked2(self):
        global filepath
        global number_part
        global x
        global size
        global mask
        global eta0
        global N
        global bins
        global mask_temp1

        filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File')
        self.beta = np.arange(600,0,-0.2)
        self.count=0
        self.active_area = (2**9,2**9)
        self.spin_arr = spin_tuple(self.active_area, bins)
        self.area = (2**10,2**10)
        mask = np.zeros(self.area)
        self.ErrorCode = slmdisplaysdk.SLMDisplay.ErrorCode
        self.ShowFlags = slmdisplaysdk.SLMDisplay.ShowFlags

        # Initializes the SLM library
        self.slm = slmdisplaysdk.SLMDisplay()

        # Check if the library implements the required version
        if not self.slm.requiresVersion(2):
            exit(1)

        # Detect SLMs and open a window on the selected SLM
        error = self.slm.open()
        assert error == self.ErrorCode.NoError, self.slm.errorString(error)
        from showSLMPreview import showSLMPreview
        # Reserve memory for the data:
        dataWidth = self.slm.width_px
        dataHeight = self.slm.height_px
        
        x = slmdisplaysdk.createFieldUChar(self.area[0],self.area[1])
        
        

        number_part = np.loadtxt(filepath[0], delimiter=",")
        x = np.pi*checkerboard(self.area,outer_bins)/128
        temp = np.zeros((bins*number_part.shape[0],bins*number_part.shape[1]))
        for i in range(number_part.shape[0]):
            for j in range(number_part.shape[1]):
                temp[i*bins:i*bins+bins, j*bins:j*bins+bins] = number_part[i,j]

        check = np.ones(self.active_area)
        for i in range(self.active_area[0]//2):
            for j in range(self.active_area[1]//2):
                check[i*2:i*2+2,j*2:j*2+2] = (-1)**(i+j)
        
        #check = np.ones(check.shape)
        number_part=temp
        eta0 = np.max(number_part)
        mask_temp1 = np.arccos(number_part/eta0)
        mask_temp= check*mask_temp1
        N = number_part.shape[0]
        v = [np.sign(np.random.normal(0,1,(N//bins,N//bins))+1e-7) for i in range(5)]
        min_fid = 0
        min_idx = 0
        for i in range(5):
            idxp = np.where(v==1)
            idxn = np.where(v==-1)
            f = np.abs(np.sum(number_part[idxp])-np.sum(number_part[idxn]))/np.sum(number_part)
            if(f>min_fid):
                min_fid = f
                min_idx = i
        x_temp = (v[i]+1)*np.pi/2 + (np.pi/2)
        #CAN YOU COPY THIS LINE 5 TIMES? like you doingrt click copy paste
        

        #x_temp = (np.sign(np.random.normal(0,1,(N//bins,N//bins))+1e-7)+1)*np.pi/2 + (np.pi/2)
        
        
        #x_temp = np.pi*np.ones(x_temp.shape)
        temp = np.zeros((number_part.shape[0],number_part.shape[1]))
        for i in range(number_part.shape[0]//bins):
            for j in range(number_part.shape[1]//bins):
                temp[i*bins:i*bins+bins, j*bins:j*bins+bins] = x_temp[i,j]

        mask[(self.area[0]-self.active_area[0])//2:(self.area[0]+self.active_area[0])//2, (self.area[1]-self.active_area[1])//2:(self.area[1]+self.active_area[1])//2] = mask_temp
        x_temp = temp
        x[(self.area[0]-self.active_area[0])//2:(self.area[0]+self.active_area[0])//2, (self.area[1]-self.active_area[1])//2:(self.area[1]+self.active_area[1])//2] = x_temp
        
        #self.X=[0]
        print(filepath[0])
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.camera.Open()
        self.camera.ExposureTime.SetValue(45)
        
        plt.imshow(x)
        plt.show()
        print("shape is: ", x.shape)
        print("dataWidth = " + str(dataWidth))
        print("dataHeight = " + str(dataHeight))

        
        # Calculate the data:
        #data = 2*np.pi*np.random.rand(dataHeight, dataWidth)
        #data = init_state(data.shape, bins)
        #data = init_state2(data.shape, outer_bins, active_area, bins)
        #data = init_state3(data.shape, active_area, outer_bins, bins)
        
        error = self.slm.showPhasevalues(x+mask)
        print("Random distribution shown on SLM")
        return filepath

    def on_button_clicked8(self):
        global d
        x, done = QtWidgets.QInputDialog.getInt(self, 'Input Dialog', 'Enter value for d:')
        d = x
        print("New value of d = ", d)

    def on_button_clicked3(self):
        print("Closing Window")
        self.close()

    def on_button_clicked4(self):
        global RUN
        global x
        RUN=1
        print("Starting Run")
        
        #while RUN==1:
            #self.update_plot_data2()

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        #self.timer.timeout.connect(self.update_plot_data)
        self.timer.timeout.connect(self.update_expt_plot)
        
        self.timer.start()


    def on_button_clicked5(self):
        global RUN
        RUN=0
        #final_cmap = pg.ColorMap(pos=,color=colors)
        #self.cmapWidget.setColorMap(final_cmap)
        #self.cmapWidget.setImage(2*final_mask/np.pi)

    def on_button_clicked6(self):
        global RUN
        RUN=0
        self.layout.removeWidget(self.cmapWidget)
        sip.delete(self.cmapWidget)
        self.cmapWidget = None
        #self.layout.removeWidget(self.cmapWidget)
        idxp1 = np.where(x!=np.pi/2)
        idxn1 = np.where(x==np.pi/2)
        
        
        final_mask = np.zeros(self.area)
        final_mask[idxp1] = mask[idxp1]
        final_mask[idxn1] = -1*mask[idxn1]
        #final_mask = final_mask[(self.area[0]-self.active_area[0])//2:(self.area[0]+self.active_area[0])//2, (self.area[1]-self.active_area[1])//2:(self.area[1]+self.active_area[1])//2]

        # a figure instance to plot on
        self.figure = plt.figure(figsize=(6,6))

        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)
        # clearing old figure
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # plot data
        im = ax.imshow(final_mask, cmap=mymap)
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        self.figure.colorbar(im, cax=cax, orientation='vertical')

        # refresh canvas
        self.canvas.draw()
        # adding tool bar to the layout
        self.layout.addWidget(self.toolbar)

        # adding canvas to the layout
        self.layout.addWidget(self.canvas, 1,1, 1,2)
        
        self.camera.Close()

        # If your IDE terminates the python interpreter process after the script is finished, the SLM content
        # will be lost as soon as the script finishes.
        # You may insert further code here.
        self.slm.close()
        # Wait until the SLM process is closed:
        error = self.slm.utilsWaitUntilClosed()
        assert error == self.ErrorCode.NoError, self.slm.errorString(error)
        # Unloading the SDK may or may not be required depending on your IDE:
        self.slm = None

    def on_button_clicked7(self):
        exp_time = 45
        img = []
        N = 500
        for i in range(N):
            self.camera.ExposureTime.SetValue(exp_time)  # microsecond
            self.camera.StartGrabbingMax(1)

            while self.camera.IsGrabbing():
            # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                     # Access the image data.
                    #img = rebin(grabResult.Array, imgbin)
                    img.append(np.mean((grabResult.Array)[127:129,127:129]))

                else:
                    print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                grabResult.Release()
            exp_time += 5
        self.EXP_TIME = 45+5*np.where(np.asarray(img)>=250)[0][0]
        print("Optimal exposure time is: ", self.EXP_TIME, " microseconds")
        self.camera.ExposureTime.SetValue(self.EXP_TIME*1.0)
            
        
    def threading_test(self):
        #self.X.append(self.X[-1] + 1)  # Add a new value 1 higher than the last.
        #self.X = self.X[1:] # Remove the first X element.
        #self.X.pop(0)

        #self.y = fidelity_arr
        #self.y.append(randint(0,100))  # Add a new random value.
        self.fidelity_disp.setText("Fidelity: "+str(fidelity_arr[-1]))
        
        self.cmapWidget.setImage((x[(self.area[0]-self.active_area[0])//2:(self.area[0]+self.active_area[0])//2,(self.area[1]-self.active_area[1])//2:(self.area[1]+self.active_area[1])//2]-np.pi/2)*128/np.pi)

        #self.p2.setGeometry(self.graphWidget.vb.sceneBoundingRect())
        #self.p2.linkedViewChanged(self.graphWidget.vb, self.p2.XAxis)
        self.updateViews()

        #self.data_line.setData(self.X, self.y)  # Update the data.
        self.p1.plot(fidelity_arr)
        #self.p1.plot(self.y)
        self.p2.addItem(pg.PlotCurveItem(loss_arr[1:], pen='b'))

    ###


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
###

###
w.show()
sys.exit(app.exec_())


# In[3]:


#w.camera.Close()


# In[4]:


#w.slm.close()
#w.slm = None


# In[11]:


#print(np.unique(x))


# In[ ]:




