# use Tkinter to show a digital clock
# tested with Python24    vegaseat    10sep2006
import tkinter as tk
from tkinter import filedialog 
from tkinter import *
import time
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk
import copy

def flip(data, shape, d):
    y = copy.copy(data)
    a = np.random.randint(0, shape[0], d)
    b = np.random.randint(0, shape[1], d)
    for i in range(len(a)):
        y[a[i], b[i]] = np.pi-y[a[i], b[i]]
    return y

def grating(shape):
    mask = np.zeros(shape)
    for i in range(shape[0]):
        mask[i, :] = 128*(i%2)
    
    return mask

def flip2(x, shape, bin, d):
    y = copy.copy(x)
    a = np.random.randint(0, shape[0]//bin, d)
    b = np.random.randint(0, shape[1]//bin, d)
    for i in range(len(a)):
        y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin] = 128-y[a[i]*bin:a[i]*bin + bin, b[i]*bin:b[i]*bin + bin]
    return y

def grating2(bin, shape):
    mask = np.zeros(shape)
    # bin = sidelength of binned cluster
    for i in range(shape[0]//bin):
        mask[i*bin:i*bin + bin, :] = 128*(i%2)
    
    return mask

spins = grating2(20,(500,500))

root = Tk()
root.geometry("600x600")
frame = Frame(root)
frame.pack()
path = filedialog.askopenfilename(initialdir="/", title="Select file",
                    filetypes=(("txt files", "*.txt"),("all files", "*.*")))
print(path)
img = cv2.imread(path)
plt.imshow(img)
plt.show()

canvas = Canvas(frame,bg='white', width = 500,height = 500)
 
file = ImageTk.PhotoImage(image=Image.fromarray(spins))
image = canvas.create_image(250, 250, image=file)
 
canvas.pack(expand = True, fill = BOTH)
#print(path.read())
time1 = ''

data2 = flip2(spins,spins.shape,20, 8)
tracker = 0

def tick2(data2):
    #global data2
    global tracker
    data2= flip2(data2,spins.shape,20, 8)
    file = ImageTk.PhotoImage(image=Image.fromarray(data2))
    image = canvas.create_image(250, 250, image=file)
    canvas.update()
    tracker +=1

    #canvas.config(image=data2)
    # calls itself every 200 milliseconds
    # to update the time display as needed
    # could use >200 ms, but display gets jerky
    canvas.after(2000, tick2(data2))
    
tick2(data2)
#savefile = filedialog.asksaveasfile(initialdir="/", title="Save file",
#                    filetypes=(("txt files", "*.txt"),("all files", "*.*"),("image",".png")))
#savefile.write(str(img))
#savefile.close()
 
root.mainloop()
