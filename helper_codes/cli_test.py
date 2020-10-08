#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt


# In[5]:


# total arguments 
n = len(sys.argv) 
print("Total arguments passed:", n) 
  
# Arguments passed 
print("\nName of Python script:", sys.argv[0]) 
  
print("\nArguments passed:", end = " ")
for i in sys.argv:
    print(i, end = " ")
a = float(sys.argv[1])
b = float(sys.argv[2])
c = float(sys.argv[3])
      
def myfunc(x, y, z):
    return x + y + z

sum = myfunc(a, b, c)
print("\nSum is:", sum)


# In[ ]:




