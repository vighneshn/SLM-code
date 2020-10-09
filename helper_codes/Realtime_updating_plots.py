#!/usr/bin/env python
# coding: utf-8

# # Code for making plots that update during runtime

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output


# In[13]:


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1) 

for i in range(20):
    x = np.arange(0, i, 0.1);
    y = np.sin(x)
    
    ax.set_xlim(0, i)
    
    ax.cla()
    ax.plot(x, y)
    display(fig)
    
    clear_output(wait = True)
    plt.pause(0.2)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("Realtime")
display(fig)
fig.savefig("realtime1.png")


# In[3]:


fig = plt.figure()
ax = fig.add_subplot(1, 1, 1) 

for i in range(21):
    ax.set_xlim(0, 20)
    
    ax.plot(i, np.sin(i), marker='x')
    display(fig)
    
    clear_output(wait = True)
    plt.pause(0.1)

fig.savefig("realtime2.png")


# In[ ]:




