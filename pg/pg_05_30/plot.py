import sys
import numpy as np
import csv
import matplotlib.pyplot as plt

filename = "results.txt"

y_col = 9
x_col = 1

title = []
xlabel = []
ylabel = []

x_collection = []
y_collection = []

with open(filename) as f:
    data = f.read()

data = data.split('\n')

for row in data:
    row_spl = row.split()
    if (len(row_spl) > y_col):
       x = row_spl[x_col]
       y = row_spl[y_col]
       #print(x,y)
       try:
           x_collection.append(float(x))
           y_collection.append(float(y))
       except:
           continue
           
plt.title(title)    
plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.plot(x_collection,y_collection, c='r', label='the data')
plt.grid(True)
plt.savefig('plot.pdf')
plt.show()