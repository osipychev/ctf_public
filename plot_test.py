#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 14:17:34 2018

@author: dos
"""
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure(1)

##Plotter
def plotter(array1,array2):
   plt.scatter([array1[0]],[array1[1]],color='b')
   plt.scatter([array2[0]],[array2[1]],color='r')
   #plt.show()
   plt.pause(0.1)
#  plt.close()
   plt.gcf().clear() 
 
for i in range(10):
    a1 = np.random.rand(2,10)
    a2 = np.random.rand(2,10)
    plotter(a1,a2)
    plt.close()