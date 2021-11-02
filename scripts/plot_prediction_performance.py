from mmwave_gemv_integration_campaigns import * 
from mmwave_gemv_integration_example_utils import * 
from mmwavePlotUtils import *
import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

campaignName = 'test-periodicity'
(ns_path, _, _, paramsList, figureFolder) = get_campaign_params (campaignName)

baseFolder = figureFolder + 'predictions/'

# compare prediction performance for different app models
kittiModelList = paramsList ['kittiModel']
numVisitedLocations=100
numNeighbors=5
overallData = pd.DataFrame ()
for k in paramsList ['kittiModel']:
    dataFolder = (baseFolder + str (k) + 
                '/numVisitedLocations=' + str (numVisitedLocations) +
                '/numNeighbors=' + str (numNeighbors))
    data = pd.read_csv (dataFolder + '/prediction_metrics.csv', index_col=0)
    data ['kittiModel'] = k
    overallData = overallData.append (data, ignore_index=True)

fig, ax = plt.subplots (2, 2, figsize=(6.4 * 2, 4.8 * 2))
fig.suptitle ("numVisitedLocations=" + str (numVisitedLocations) + 
              " numNeighbors=" + str (numNeighbors))
# [[b.set_ylim (0, 10) for b in a] for a in ax]
[[b.grid () for b in a] for a in ax]
ax [0,0].set_title ("NN")
g = sns.boxplot(data=overallData, x="kittiModel", y="NN mse", ax=ax[0, 0])
g.set_yscale("log")
g.set (ylabel="MSE")

ax [0,1].set_title ("Lin")
g = sns.boxplot(data=overallData, x="kittiModel", y="LIN mse", ax=ax[0, 1])
g.set_yscale("log")
g.set (ylabel="MSE")

ax [1,0].set_title ("MovAv")
g = sns.boxplot(data=overallData, x="kittiModel", y="MOV_AV mse", ax=ax[1, 0])
g.set_yscale("log")
g.set (ylabel="MSE")

ax [1,1].set_title ("IDW")
g = sns.boxplot(data=overallData, x="kittiModel", y="IDW mse", ax=ax[1, 1])
g.set_yscale("log")
g.set (ylabel="MSE")
save_figure (fig, baseFolder + "/mse_numVisitedLocations=" + str (numVisitedLocations) + 
                               "_numNeighbors=" + str (numNeighbors))

# fig, ax = plt.subplots (1, 3, sharey=True)
# fig.suptitle ("NN")
# sns.boxplot(data=overallData, x="kittiModel", y="NN accuracy", ax=ax[0])
# sns.boxplot(data=overallData, x="kittiModel", y="NN precision", ax=ax[1])
# sns.boxplot(data=overallData, x="kittiModel", y="NN recall", ax=ax[2])
# 
# fig, ax = plt.subplots (1, 3, sharey=True)
# fig.suptitle ("LIN")
# sns.boxplot(data=overallData, x="kittiModel", y="LIN accuracy", ax=ax[0])
# sns.boxplot(data=overallData, x="kittiModel", y="LIN precision", ax=ax[1])
# sns.boxplot(data=overallData, x="kittiModel", y="LIN recall", ax=ax[2])
# 
# fig, ax = plt.subplots (1, 3, sharey=True)
# fig.suptitle ("MOV_AV")
# sns.boxplot(data=overallData, x="kittiModel", y="MOV_AV accuracy", ax=ax[0])
# sns.boxplot(data=overallData, x="kittiModel", y="MOV_AV precision", ax=ax[1])
# sns.boxplot(data=overallData, x="kittiModel", y="MOV_AV recall", ax=ax[2])
# 
# fig, ax = plt.subplots (1, 3, sharey=True)
# fig.suptitle ("IDW")
# sns.boxplot(data=overallData, x="kittiModel", y="IDW accuracy", ax=ax[0])
# sns.boxplot(data=overallData, x="kittiModel", y="IDW precision", ax=ax[1])
# sns.boxplot(data=overallData, x="kittiModel", y="IDW recall", ax=ax[2])


newDf = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'kittiModel'], 
                 value_vars=['NN accuracy', 'LIN accuracy', 'MOV_AV accuracy', 'IDW accuracy'])
g = sns.catplot (data=newDf, x="kittiModel", y="value", hue="variable", kind="box")
g.set(ylabel="Accuracy")
plt.grid ()
plt.title ("numVisitedLocations=" + str (numVisitedLocations) + 
           " numNeighbors=" + str (numNeighbors))
g.fig.set_size_inches (6.4 * 2, 4.8 * 2)
save_figure (g.fig, baseFolder + "/accuracy_numVisitedLocations=" + str (numVisitedLocations) + 
                              "_numNeighbors=" + str (numNeighbors))
newDf = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'kittiModel'], 
                 value_vars=['NN precision', 'LIN precision', 'MOV_AV precision', 'IDW precision'])
g = sns.catplot (data=newDf, x="kittiModel", y="value", hue="variable", kind="box")
g.set(ylabel="Precision")
plt.grid ()
plt.title ("numVisitedLocations=" + str (numVisitedLocations) + 
           " numNeighbors=" + str (numNeighbors))
g.fig.set_size_inches (6.4 * 2, 4.8 * 2)
save_figure (g.fig, baseFolder + "/precision_numVisitedLocations=" + str (numVisitedLocations) + 
                              "_numNeighbors=" + str (numNeighbors))
newDf = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'kittiModel'], 
                 value_vars=['NN recall', 'LIN recall', 'MOV_AV recall', 'IDW recall'])
g = sns.catplot (data=newDf, x="kittiModel", y="value", hue="variable", kind="box")
g.set(ylabel="Recall")
plt.grid ()
plt.title ("numVisitedLocations=" + str (numVisitedLocations) + 
           " numNeighbors=" + str (numNeighbors))
g.fig.set_size_inches (6.4 * 2, 4.8 * 2)
save_figure (g.fig, baseFolder + "/recall_numVisitedLocations=" + str (numVisitedLocations) + 
                              "_numNeighbors=" + str (numNeighbors))

# compare prediction performance with different number of visited locations
kittiModel = 1451
numVisitedLocationsList = [10, 50, 100, 300, 500]
numNeighbors=5
overallData = pd.DataFrame ()
for v in numVisitedLocationsList:
    dataFolder = (baseFolder + str (kittiModel) + 
                '/numVisitedLocations=' + str (v) +
                '/numNeighbors=' + str (numNeighbors))
    data = pd.read_csv (dataFolder + '/prediction_metrics.csv', index_col=0)
    data ['numVisitedLocations'] = v
    # data = data [data ['firstVehicleIndex'] == 1]
    overallData = overallData.append (data, ignore_index=True)

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numNeighbors=" + str (numNeighbors))
newDf1 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numVisitedLocations'], 
                 value_vars=['NN mse', 'LIN mse', 'MOV_AV mse', 'IDW mse'], 
                 value_name='mse')
sns.lineplot (data=newDf1, x="numVisitedLocations", y="mse", hue="variable")
plt.grid ()
save_figure (g.fig, baseFolder + "/mse_kittiModel=" + str (kittiModel) + 
                              "_numNeighbors=" + str (numNeighbors))

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numNeighbors=" + str (numNeighbors))
newDf2 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numVisitedLocations'], 
                 value_vars=['NN accuracy', 'LIN accuracy', 'MOV_AV accuracy', 'IDW accuracy'], 
                 value_name='accuracy')
sns.lineplot (data=newDf2, x="numVisitedLocations", y="accuracy", hue="variable")
plt.grid ()
g.set(ylabel="Accuracy")
save_figure (g.fig, baseFolder + "/accuracy_kittiModel=" + str (kittiModel) + 
                              "_numNeighbors=" + str (numNeighbors))


plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numNeighbors=" + str (numNeighbors))
newDf3 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numVisitedLocations'], 
                 value_vars=['NN precision', 'LIN precision', 'MOV_AV precision', 'IDW precision'], 
                 value_name='precision')
sns.lineplot (data=newDf3, x="numVisitedLocations", y="precision", hue="variable")
plt.grid ()
g.set(ylabel="Precision")
save_figure (g.fig, baseFolder + "/precision_kittiModel=" + str (kittiModel) + 
                              "_numNeighbors=" + str (numNeighbors))


plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numNeighbors=" + str (numNeighbors))
newDf4 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numVisitedLocations'], 
                 value_vars=['NN recall', 'LIN recall', 'MOV_AV recall', 'IDW recall'],
                 value_name='recall')
sns.lineplot (data=newDf4, x="numVisitedLocations", y="recall", hue="variable")
plt.grid ()
g.set(ylabel="Recall")
save_figure (g.fig, baseFolder + "/recall_kittiModel=" + str (kittiModel) + 
                              "_numNeighbors=" + str (numNeighbors))

# compare prediction performance with different number of neighbors
kittiModel = 1450
numVisitedLocations = 100
numNeighborsList = [1, 5, 10, 20]
overallData = pd.DataFrame ()
for n in numNeighborsList:
    dataFolder = (baseFolder + str (kittiModel) + 
                '/numVisitedLocations=' + str (numVisitedLocations) +
                '/numNeighbors=' + str (n))
    data = pd.read_csv (dataFolder + '/prediction_metrics.csv', index_col=0)
    data ['numNeighbors'] = n
    overallData = overallData.append (data, ignore_index=True)

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numVisitedLocations=" + str (numVisitedLocations))
newDf1 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numNeighbors'], 
                 value_vars=['MOV_AV mse', 'IDW mse'], 
                 value_name='mse')
sns.lineplot (data=newDf1, x="numNeighbors", y="mse", hue="variable")
save_figure (g.fig, baseFolder + "/mse_kittiModel" + str (kittiModel) + 
                                "_numVisitedLocation=" + str (numVisitedLocations))

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numVisitedLocations=" + str (numVisitedLocations))
newDf1 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numNeighbors'], 
                 value_vars=['MOV_AV accuracy', 'IDW accuracy'], 
                 value_name='accuracy')
sns.lineplot (data=newDf1, x="numNeighbors", y="accuracy", hue="variable")
save_figure (g.fig, baseFolder + "/accuracy_kittiModel" + str (kittiModel) + 
                                "_numVisitedLocation=" + str (numVisitedLocations))

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numVisitedLocations=" + str (numVisitedLocations))
newDf1 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numNeighbors'], 
                 value_vars=['MOV_AV precision', 'IDW precision'], 
                 value_name='precision')
sns.lineplot (data=newDf1, x="numNeighbors", y="precision", hue="variable")
save_figure (g.fig, baseFolder + "/precision_kittiModel" + str (kittiModel) + 
                                "_numVisitedLocation=" + str (numVisitedLocations))

plt.figure (figsize=(6.4 * 2, 4.8 * 2))
plt.title ("kittiModel=" + str (kittiModel) + " numVisitedLocations=" + str (numVisitedLocations))
newDf1 = pd.melt (overallData, id_vars= ['firstVehicleIndex', 'numNeighbors'], 
                 value_vars=['MOV_AV recall', 'IDW recall'], 
                 value_name='recall')
sns.lineplot (data=newDf1, x="numNeighbors", y="recall", hue="variable")
save_figure (g.fig, baseFolder + "/recall_kittiModel" + str (kittiModel) + 
                                "_numVisitedLocation=" + str (numVisitedLocations))

kittiModel = 1451
numVisitedLocations = 100
numNeighbors=5
dataFolder = (baseFolder + str (kittiModel) + 
            '/numVisitedLocations=' + str (v) +
            '/numNeighbors=' + str (numNeighbors))
data = pd.read_csv (dataFolder + '/prediction_metrics.csv', index_col=0)
data = pd.melt (data, id_vars= ['firstVehicleIndex'], 
                 value_vars=['NN mse', 'LIN mse', 'MOV_AV mse', 'IDW mse'],
                 value_name='mse')
plt.figure ()
plt.title ("numVisitedLocations=" + str (numVisitedLocations) + 
           " numNeighbors=" + str (numNeighbors))
g = sns.barplot (data=data, x='firstVehicleIndex', y='mse', hue='variable')
g.set_yscale("log")
g.set(xlabel="Vehicle index", ylabel="MSE")
plt.show ()
import pdb; pdb.set_trace ()
    
