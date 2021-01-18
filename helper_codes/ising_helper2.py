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


# DEFINING SOME USEFUL FUNCTIONS 

def grating(shape, bin):
    mask = np.zeros(shape)
    for i in range(shape[0]//bin):
        mask[shape[0]*bin:shape[0]*bin + bin, shape[1]*bin:shape[1]*bin + bin] = 128*(i%2)

def grating2(tot_shape, shape, tot_bin, bin):
    data2 = checkerboard(tot_shape, tot_bin)
    data2[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = grating(shape, bin)
    return data2

def checkerboard(shape, bin):
    phase = np.zeros(shape)
    for i in range(shape[0]//bin):
        for j in range(shape[1]//bin):
            phase[i*bin: i*bin + bin, j*bin: j*bin + bin] = 128*((i+j)%2)
    
    return phase

def flip(x, shape, bin, d):
    y = copy.copy(x)
    a = np.random.randint(0, shape[0]//bin, d)
    b = np.random.randint(0, shape[1]//bin, d)
    for i in range(len(a)):
        y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin] = np.pi-y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin]
    return y

def flip2(x, shape, tot_shape, bin, d):
    y = copy.copy(x)
    a = np.random.randint(0, shape[0]//bin, d)
    b = np.random.randint(0, shape[1]//bin, d)
    for i in range(len(a)):
        y[(tot_shape[0]-shape[0])//(2)+a[i]*bin:(tot_shape[0]-shape[0])//(2)+a[i]*bin + bin, (tot_shape[1]-shape[1])//(2)+b[i]*bin:(tot_shape[1]-shape[1])//(2)+b[i]*bin + bin] = np.pi - y[(tot_shape[0]-shape[0])//(2)+a[i]*bin:(tot_shape[0]-shape[0])//(2)+a[i]*bin + bin, (tot_shape[1]-shape[1])//(2)+b[i]*bin:(tot_shape[1]-shape[1])//(2) + b[i]*bin + bin]
    return y

def cost(I_target, I_camera):
    return np.sum((I_target-I_camera)**2)/np.size(I_target)

def cost2(I_target, I_camera):
    return np.sqrt((I_target-I_camera)**2)

def checkerboard2(tot_shape, shape, tot_bin, bin):
    data2 = checkerboard(tot_shape, tot_bin)
    data2[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = checkerboard(shape, bin)
    return data2

def init_state2(tot_shape, tot_bin, shape, bin):
    phase = np.pi*checkerboard2(tot_shape, shape, tot_bin, bin)/128
    phase[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = np.zeros(shape)
    phase = flip2(phase, shape, tot_shape, bin, shape[0]*shape[1]//(bin**2))
    return phase

def deltatarget(shape, extent):
    targ = np.zeros(shape)
    targ[(shape[0]-extent)//2 : (shape[0]+extent)//2, (shape[1]-extent)//2 : (shape[1]+extent)//2] = 255
    return targ
    
def hamiltonian(COST, targ, img):
    x = COST - (np.sum(img**2)/(np.size(img))) - (np.sum(targ**2)/np.size(targ))
    return x
    

def init_state3(tot_shape, shape, total_bin, bin):
    
    data2 = np.pi*checkerboard2(tot_shape, shape, total_bin, bin)/128
    data2[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = 0
    data2 = flip3(data2, tot_shape, shape, bin, shape[0]*shape[1]//(bin**2)//2)
    return data2
    
def reduce(spin, data, count, bins):
    for i in range(0,data.shape[0],bins):
        for j in range(0,data.shape[1],bins):
            spin[(data.shape[0]//bins)*(i//bins) + (j//bins), count] = data[i,j]
            
def rebin(a, bins):
    shape = (a.shape[0]//bins, a.shape[1]//bins)
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)
            

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

def blank_screen(tot_shape, shape, tot_bin, bin):
    data2 = checkerboard(tot_shape, tot_bin)
    data2[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = 0
    return data2

def spin_tuple(shape, bin_size):
    arr = []
    for i in range(0, shape[0]//bin_size):
        for j in range(0, shape[1]//bin_size):
            arr.append((i,j))
    return arr

def flip3(x, tot_shape, shape, bin, d):
    y = copy.copy(x)
    l = random.sample(spin_arr,d)
    for i in range(d):
        y[(tot_shape[0]-shape[0])//(2)+l[i][0]*bin:(tot_shape[0]-shape[0])//(2)+l[i][0]*bin + bin, (tot_shape[1]-shape[1])//(2)+l[i][1]*bin:(tot_shape[1]-shape[1])//(2)+l[i][1]*bin + bin] = np.pi - y[(tot_shape[0]-shape[0])//(2)+l[i][0]*bin:(tot_shape[0]-shape[0])//(2)+l[i][0]*bin + bin, (tot_shape[1]-shape[1])//(2)+l[i][1]*bin:(tot_shape[1]-shape[1])//(2) + l[i][1]*bin + bin]
    return y

def videostart(spin, phase):
    pathOut = str(spin) + 'x' + str(spin) + '.avi'
    fps = 5
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, phase.shape)
    return out
    
def writevideo(phase, out):
    gray = cv2.normalize(phase, None, 255, 0, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    gray_3c = cv2.merge([gray, gray, gray])
    out.write(gray_3c)
    
def videoend(out):
    out.release()
    
def flip_cluster(x, tot_shape, shape, bin, d, cluster_size):
    y = copy.copy(x)
    #l = random.sample(spin_arr,d)
    a = np.random.randint(0, (shape[0]-cluster_size*bin)//(bin), d)
    b = np.random.randint(0, (shape[1]-cluster_size*bin)//bin, d)
    for i in range(d):
        y[(tot_shape[0]-shape[0])//(2)+a[i]*bin:(tot_shape[0]-shape[0])//(2)+a[i]*bin + bin*cluster_size, (tot_shape[1]-shape[1])//(2)+b[i]*bin:(tot_shape[1]-shape[1])//(2)+b[i]*bin + bin*cluster_size] = np.pi - y[(tot_shape[0]-shape[0])//(2)+a[i]*bin:(tot_shape[0]-shape[0])//(2)+a[i]*bin + bin*cluster_size, (tot_shape[1]-shape[1])//(2)+b[i]*bin:(tot_shape[1]-shape[1])//(2) + b[i]*bin + bin*cluster_size]
    return y

def np_init(integers, tot_shape, shape, total_bin, bin):
    zeta = integers/np.max(integers)
    alpha = np.arccos(zeta)
    zetamatrix = np.zeros(shape)
    for i in range(shape[0]//bin):
      for j in range(shape[1]//bin):
        zetamatrix[bin*i:bin*i+bin, bin*j:bin*j+bin] = alpha[i,j]
    print(alpha)
    x = init_state3(tot_shape, shape, total_bin, bin)
    phase = x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2]
    idx0 = np.where(phase==0)
    idxpi = np.where(phase==np.pi)
    vec = zetamatrix
    phase[idx0] = phase[idx0]+vec[idx0]
    phase[idxpi] = phase[idxpi] - vec[idxpi]
    x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = phase
    print(np.unique(x))
    return x

def np_init2(integers, tot_shape, shape, total_bin, bin):
    zeta = integers#/np.max(integers)
    alpha = np.arccos(zeta)
    zetamatrix = np.zeros(shape)
    for i in range(shape[0]//bin):
      for j in range(shape[1]//bin):
        zetamatrix[bin*i:bin*i+bin, bin*j:bin*j+bin] = alpha[i,j]
    #print(alpha)
    x = init_state3(tot_shape, shape, total_bin, bin)
    phase = x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2]
    #phase = np.zeros(shape)
    idx0 = np.where(phase==0)
    idxpi = np.where(phase==np.pi)
    vec = zetamatrix
    phase[idx0] = vec[idx0]
    phase[idxpi] = np.pi + vec[idxpi]
    x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = phase
    #print(np.unique(x))
    return x

def np_gui_init(integers, tot_shape, shape, total_bin, bin):
    zeta = integers#/np.max(integers)
    alpha = np.arccos(zeta)
    zetamatrix = np.zeros(shape)
    for i in range(shape[0]//bin):
      for j in range(shape[1]//bin):
        zetamatrix[bin*i:bin*i+bin, bin*j:bin*j+bin] = alpha[i,j]
    #print(alpha)
    x = init_state3(tot_shape, shape, total_bin, bin)
    phase = x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2]
    #phase = np.zeros(shape)
    idx0 = np.where(phase==0)
    idxpi = np.where(phase==np.pi)
    vec = zetamatrix
    phase[idx0] = vec[idx0]
    phase[idxpi] = np.pi + vec[idxpi]
    x[(tot_shape[0]-shape[0])//2 : (tot_shape[0]+shape[0])//2, (tot_shape[1]-shape[1])//2:(tot_shape[1]+shape[1])//2] = phase
    #print(np.unique(x))
    return x


def flip_np(spin_arr, x, tot_shape, shape, bin, d):
    y = copy.copy(x)
    l = random.sample(spin_arr,d)
    for i in range(d):
        y[(tot_shape[0]-shape[0])//(2)+l[i][0]*bin:(tot_shape[0]-shape[0])//(2)+l[i][0]*bin + bin, (tot_shape[1]-shape[1])//(2)+l[i][1]*bin:(tot_shape[1]-shape[1])//(2)+l[i][1]*bin + bin] = (np.pi + y[(tot_shape[0]-shape[0])//(2)+l[i][0]*bin:(tot_shape[0]-shape[0])//(2)+l[i][0]*bin + bin, (tot_shape[1]-shape[1])//(2)+l[i][1]*bin:(tot_shape[1]-shape[1])//(2) + l[i][1]*bin + bin])%(2*np.pi)
    return y

def loss_notarget(x):
  ft_x = abs(np.fft.fftshift(np.fft.fft2(x)))**2
  c = np.sum(ft_x)
  ft_x = ft_x/np.sum(ft_x)
  return (ft_x)[N//2,N//2], c
