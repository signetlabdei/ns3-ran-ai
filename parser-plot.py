import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

def check_all_infinite(dataset):
  for el in dataset:
    if not math.isinf(el):
      return False
  return True

def plot_data(dataset, name="rsu"):
  fig, ax = plt.subplots(figsize=(15, 15))
  #for i in range(1, len(data.columns)):
  for i in [4, 14, 25, 36]:
    if not check_all_infinite(data[i]):
      plt.plot(data[0], data[i], label="UE "+str(i))
  plt.xlabel("Time [s]")
  plt.ylabel("Received power [dBm]")
  plt.title(name)
  plt.legend()
  plt.grid(True)
  plt.savefig(name+'.png')

data = pd.read_csv("powerTest-3.txt",sep="\t", header= None)
plot_data(data, "RSU_3")

data = pd.read_csv("powerTest-4.txt",sep="\t", header= None)
plot_data(data, "RSU_4")

data = pd.read_csv("powerTest-8.txt",sep="\t", header= None)
plot_data(data, "RSU_8")

data = pd.read_csv("powerTest-10.txt",sep="\t", header= None)
plot_data(data, "RSU_10")


data = pd.read_csv("losCondition-3.txt",sep="\t", header= None)
fig, ax = plt.subplots(figsize=(15, 15))
#for i in range(1, len(data.columns)):
for i in [4, 14, 25, 36]:
  plt.plot(data[0], data[i], label="UE "+str(i))
plt.xlabel("Time [s]")
plt.ylabel("Received power [dBm]")
plt.title("LOS Condition")
plt.legend()
plt.grid(True)
plt.show()
plt.savefig('LOS_3.png')
