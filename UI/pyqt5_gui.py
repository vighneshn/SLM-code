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
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.graphWidget)
        layout.addWidget(self.cmapWidget)
        self.buttonwidget = QtWidgets.QPushButton('Click')
        self.buttonwidget.clicked.connect(self.on_button_clicked)
        #self.buttonwidget.clicked.connect(threading.Thread(target=self.on_button_clicked).start)
        #self.buttonwidget.show()
        layout.addWidget(self.buttonwidget)
        
        self.buttonwidget2 = QtWidgets.QPushButton('Load File')
        self.buttonwidget2.clicked.connect(self.on_button_clicked2)
        #self.buttonwidget2.clicked.connect(threading.Thread(target=self.on_button_clicked2).start)
        layout.addWidget(self.buttonwidget2)
        
        self.buttonwidget3 = QtWidgets.QPushButton('Close Window')
        self.buttonwidget3.clicked.connect(self.on_button_clicked3)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        layout.addWidget(self.buttonwidget3)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.buttonwidget4 = QtWidgets.QPushButton("Start/Continue Run")
        self.buttonwidget4.clicked.connect(self.on_button_clicked4)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        layout.addWidget(self.buttonwidget4)
        widget.setLayout(layout)
        
        self.buttonwidget5 = QtWidgets.QPushButton("Stop/Pause Run")
        self.buttonwidget5.clicked.connect(self.on_button_clicked5)
        #self.buttonwidget3.clicked.connect(threading.Thread(target=self.on_button_clicked3).start)
        layout.addWidget(self.buttonwidget5)
        widget.setLayout(layout)
        ###
        
        ###
        
        # setting title 
        self.setWindowTitle("Number Partitioning Solver") 
  
        # setting geometry 
        self.setGeometry(100, 100, 600, 500) 
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
            
            self.X.append(self.X[-1] + 1)  # Add a new value 1 higher than the last.
            #self.X = self.X[1:] # Remove the first X element.
            #self.X.pop(0)
           
            self.y = fidelity_arr
            #self.y.append(randint(0,100))  # Add a new random value.
            self.cmapWidget.setImage(x*128/np.pi)
            
            self.data_line.setData(self.X, self.y)  # Update the data.
        
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
        self.timer.setInterval(50)
        
        self.timer.timeout.connect(self.update_plot_data)
        
        #self.timer.timeout.connect()
        self.timer.start()
        
        
    def on_button_clicked5(self):
        global RUN
        RUN=0
    ###


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
###

###
w.show()
sys.exit(app.exec_())
