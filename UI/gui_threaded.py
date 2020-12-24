from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from random import randint
import numpy as np
import threading
import time
import copy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import sip

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# sample the colormaps that you want to use. Use 128 from each so we get 256
# colors in total
colors1 = plt.cm.binary(np.linspace(0., 1, 128))
colors2 = plt.cm.gist_heat_r(np.linspace(0, 1, 128))

# combine them and build a new colormap
colors = np.vstack((colors1, colors2))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)



def loss_notarget(x):
  ft_x = abs(np.fft.fftshift(np.fft.fft2(x)))**2
  c = np.sum(ft_x)
  ft_x = ft_x/np.sum(ft_x)
  return (ft_x)[N//2,N//2], c

def flip2(x, shape, bin, d):
    y = copy.copy(x)
    a = np.random.randint(0, shape[0]//bin, d)
    b = np.random.randint(0, shape[1]//bin, d)
    for i in range(len(a)):
        y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin] = (y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin]+np.pi)%(2*np.pi)
    return y



loss_arr = []
fidelity_arr = []
fidelity_arr.append(0.01)


filepath = ''
number_part = []
x = []
mask = []
eta0 = 0
N = 0
RUN = 0
bins = 5




class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        #self.setCentralWidget(self.graphWidget)
        
        self.X = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.X, self.y, pen=pen)
        
        ###
        self.cmapWidget = pg.ImageView()
        self.imagedata = self.cmapWidget.setImage(np.random.randint(0,100, (100,100)))
        widget = QtWidgets.QWidget()
        #self.graphWidget.setGeometry(50,50,100,100)
        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.graphWidget, 1,0, 7,1)
        self.layout.addWidget(self.cmapWidget, 1,1)
        self.buttonwidget = QtWidgets.QPushButton('Click')
        self.buttonwidget.clicked.connect(self.on_button_clicked)
        self.buttonwidget.resize(100,40)
        #self.buttonwidget.clicked.connect(threading.Thread(target=self.on_button_clicked).start)
        #self.buttonwidget.show()
        self.layout.addWidget(self.buttonwidget, 7,1)
        
        self.buttonwidget2 = QtWidgets.QPushButton('Load File')
        self.buttonwidget2.clicked.connect(self.on_button_clicked2)
        self.buttonwidget2.resize(100,40)
        #self.buttonwidget2.clicked.connect(threading.Thread(target=self.on_button_clicked2).start)
        self.layout.addWidget(self.buttonwidget2, 2, 1)
        
        self.buttonwidget3 = QtWidgets.QPushButton('Close Window')
        self.buttonwidget3.clicked.connect(self.on_button_clicked3)
        self.buttonwidget3.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget3, 3,1)
        
        
        self.buttonwidget4 = QtWidgets.QPushButton("Start/Continue Run")
        self.buttonwidget4.clicked.connect(self.on_button_clicked4)
        self.buttonwidget4.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget4, 4,1)
        
        self.layout.setColumnStretch(0,6)
        self.layout.setColumnStretch(1,4)
        
        self.buttonwidget5 = QtWidgets.QPushButton("Pause Run")
        self.buttonwidget5.clicked.connect(self.on_button_clicked5)
        self.buttonwidget5.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget5, 5,1)
        
        self.buttonwidget6 = QtWidgets.QPushButton("Stop Run")
        self.buttonwidget6.clicked.connect(self.on_button_clicked6)
        self.buttonwidget6.resize(100,40)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        self.layout.addWidget(self.buttonwidget6, 6,1)
        
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
            #self.X.append(self.X[-1] + 1)  # Add a new value 1 higher than the last.
            
            #self.X = self.X[1:] # Remove the first X element.
            #self.X.pop(0)
           
            #self.y = fidelity_arr
            
            #self.y.append(randint(0,100))  # Add a new random value.
            
            #self.cmapWidget.setImage(x*128/np.pi)
            
            #self.data_line.setData(self.X, self.y)  # Update the data.
        
    ###
    def on_button_clicked(self):
        self.alert = QtWidgets.QMessageBox()
        self.alert.setText('You clicked the button!')
        self.alert.exec_()
    
    def on_button_clicked2(self):
        global filepath
        global number_part
        global x
        global mask
        global eta0
        global N
        global bins
        
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File')
        print(filepath[0])
        number_part = np.loadtxt(filepath[0], delimiter=",")
        temp = np.zeros((bins*number_part.shape[0],bins*number_part.shape[1]))
        for i in range(number_part.shape[0]):
            for j in range(number_part.shape[1]):
                temp[i*bins:i*bins+bins, j*bins:j*bins+bins] = number_part[i,j]

        number_part=temp
        eta0 = np.max(number_part)
        mask = np.arccos(number_part/eta0)
        N = number_part.shape[0]
        x = (np.sign(np.random.normal(0,1,(N//bins,N//bins))+1e-7)+1)*np.pi/2
        temp = np.zeros((number_part.shape[0],number_part.shape[1]))
        for i in range(number_part.shape[0]//bins):
            for j in range(number_part.shape[1]//bins):
                temp[i*bins:i*bins+bins, j*bins:j*bins+bins] = x[i,j]

        x = temp
        self.X=[0]
        
        return filepath
    
    def on_button_clicked3(self):
        print("Closing Window")
        self.close()
        
    def on_button_clicked4(self):
        global RUN
        global x
        RUN=1
        
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1)
        
        self.timer.timeout.connect(self.update_plot_data)
        
        #self.timer.timeout.connect()
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
        idxp1 = np.where(x!=0.0)
        idxn1 = np.where(x==0.0)
        final_mask = np.zeros(mask.shape)
        final_mask[idxp1] = mask[idxp1]
        final_mask[idxn1] = -1*mask[idxn1]

        # a figure instance to plot on 
        self.figure = plt.figure() 
   
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
        ax.imshow(final_mask, cmap=mymap) 
   
        # refresh canvas 
        self.canvas.draw()
        # adding tool bar to the layout 
        self.layout.addWidget(self.toolbar) 
           
        # adding canvas to the layout 
        self.layout.addWidget(self.canvas, 1,1)
        
    def threading_test(self):
        self.X.append(self.X[-1] + 1)  # Add a new value 1 higher than the last.
        #self.X = self.X[1:] # Remove the first X element.
        #self.X.pop(0)
           
        self.y = fidelity_arr
        #self.y.append(randint(0,100))  # Add a new random value.
        self.cmapWidget.setImage(x*128/np.pi)
            
        self.data_line.setData(self.X, self.y)  # Update the data.
           
    ###


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
###

###
w.show()
sys.exit(app.exec_())