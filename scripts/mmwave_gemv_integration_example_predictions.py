from mmwave_gemv_integration_campaigns import * 
from mmwave_gemv_integration_example_utils import * 
from mmwavePlotUtils import *
import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging as log
# log.basicConfig(level=log.DEBUG)
from scipy import interpolate
from sklearn.metrics import mean_squared_error, accuracy_score, precision_score, recall_score
import matplotlib.colors as colors
import geopy.distance
import math
import argparse
from multiprocessing import Process

def plot_map (ax, x, y, z):
    im = ax.scatter (x, y, c = z, s = 5, norm=colors.PowerNorm (gamma = 0.5))
    ax.set_xlim ([11.310, 11.3215])
    ax.set_ylim ([44.491, 44.4975])
    return im
    
def plot_counts (train):
    # We count the number of measurements available for each point in the 
    # traininig set
    countTrainSamples = train.groupby ('coordinates', as_index=False).agg ({'x' : 'first', 
                                                                            'y' : 'first', 
                                                                            'delay [s]' : 'count'})
    # plot the number of available measurements in each location
    fig, ax = plt.subplots (1,1)
    im = plot_map (ax, countTrainSamples ['x'], countTrainSamples ['y'], 
                   countTrainSamples ['delay [s]'])
    ax.set_title ('Number of available measurements')
    fig.colorbar (im, ax=ax)
    plt.show ()

    fig, ax = plt.subplots (1,1)
    ax.bar (countTrainSamples.index, countTrainSamples ['delay [s]'], 
            tick_label=countTrainSamples ['coordinates'])
    plt.xticks (rotation=90)
    ax.set_title ('Number of available measurements')
    plt.show ()

"""
Predicts the delay in unknown points by using a nearest neighbor or linear 
interpolation approach. 

Params: 
    - trainSamples: dataframe containing the measerements retrieved in the 
                    visited locations
    - unknownPoints: coordinates of the unknown locations 
    - method: 'nearest' for nearest neighbor, 'linear' for linear interpolation
"""     
def predict (trainSamples, unknownPoints, method):
    # import pdb; pdb.set_trace ()
    Z = interpolate.griddata (trainSamples ['coordinates'].to_list (),
                              trainSamples ['delay [s]'].to_numpy (),
                              unknownPoints, 
                              method=method)
    return Z

"""
Predicts the delay in unknown points by averaging the value measured in the 
[numNeighbors] closest visited locations. 
If idw = True, inverse distance weighting is applied.

Params: 
    - trainSamples: dataframe containing the measerements retrieved in the 
                    visited locations
    - unknownPoints: coordinates of the unknown locations 
    - numNeighbors: number of closest visited points to be considered 
    - idw: whether to apply inverse distance weighting
"""  
def movAv_predict (trainSamples, unknownPoints, numNeighbors=5, idw=False):
    Z = []
    for u in unknownPoints:
        # compute the distance between the unknown location and the visited 
        # locations 
        d = []
        newTrainSamples = trainSamples
        newTrainSamples ['distance'] = newTrainSamples.apply (lambda row, u=u: 
                                       # math.sqrt ((u [0] - row.x)**2 + (u [1] - row.y)**2), 
                                       geopy.distance.distance (u, row.coordinates).m, 
                                       axis = 1)
                
        # extract the [numNeighbors] closest visited locations
        closestPoints = newTrainSamples.sort_values ('distance').head (numNeighbors)
        
        # predict the value in the unknown location by averaging the values 
        # achieved in the closest visited locations
        if (idw):
            weights = 1 / closestPoints ['distance']
            if (np.isinf (weights).any ()):
                prediction = closestPoints ['delay [s]'].to_numpy () [0] 
            else:
                prediction = (closestPoints ['delay [s]'] * weights).sum () / weights.sum ()
        else:
            prediction = closestPoints ['delay [s]'].mean ()
                    
        Z.append (prediction)
    return Z    

###############################################################################

"""
Main function. Loads the the campaign specified by [campaignName] and extracts 
those obtained with the specified [kittiModel]. It draws [numVisitedLocations] 
random locations from those available in the results and computes the average 
delay. Using this dataset, it tries to predict the delay experienced by each 
trajectory available in the results.
Considers four prediction methods: nearest neighbors, linear interpolation, 
moving average, inverse distance weighting.
Produces some plots to demostrate the performance of the prediction methods, 
they are saved in the figure folder of the correspongin simualtion campaign.

Params: 
    - campaignName: name of the simualtion campaign to load
    - kittiModel: kitti model 
    - numVisitedLocations: number of visited locations 
    - numNeighbors: number of neighboring locations (used by moving average and 
                    inverse distance weighting to determing the size of the 
                    neighborhood)
"""  
def main (campaignName, kittiModel, numVisitedLocations, numNeighbors):

    print ("\ncampaignName = " + str (campaignName))
    print ("kittiModel = " + str (kittiModel))
    print ("numVisitedLocations = " + str (numVisitedLocations))
    print ("numNeighbors = " + str (numNeighbors) + "\n")
        
    DELAY_REQ = 0.1 # delay QoS requirement in seconds, used to discriminate 
                    # the QoS classes

    (ns_path, ns_script, ns_res_path, 
    params_grid, base_figure_foder) = get_campaign_params (campaignName)
    log.debug ('results path: ' + ns_res_path)

    # for the moment focus on a single APP mode
    params_grid ['kittiModel'] = kittiModel
    figure_folder = (base_figure_foder + 'predictions/' + 
                     str (kittiModel) + 
                    '/numVisitedLocations=' + str (numVisitedLocations) + 
                    '/numNeighbors=' + str (numNeighbors) + '/')
    Path(figure_folder).mkdir (parents=True, exist_ok=True)

    campaign = sem.CampaignManager.load (campaign_dir=ns_res_path)
    log.debug (campaign)
    overall_list = sem.list_param_combinations(params_grid)
    log.debug (overall_list)

    # parse APP layer results
    results = campaign.get_results_as_dataframe(read_appStatsTrace,
                                                params=overall_list,
                                                verbose=True, 
                                                parallel_parsing=False)
    log.debug (results)
    # results = results [results ['firstVehicleIndex'].isin ([0,1])] # for testing purposes
    data = map_position_to_metric (results, 'delay [s]')

    # create a new column by merging (x, y) values
    data ['coordinates'] = list (zip (data ['x'], data ['y']))
    log.debug (data)

    # find the unique locations in the dataset
    locations = data ['coordinates'].drop_duplicates ()
    log.debug ('\nNumber of unique locations ' + str (locations.shape [0]))

    # sample the dataset
    visitedLocations = locations.sample (n=numVisitedLocations, 
                                         random_state=1).to_list ()
    log.debug ('\nVisited locations\n' + str (visitedLocations))

    # extract the training set
    train = data [data ['coordinates'].isin (visitedLocations)]
    log.debug ('\nTrain data\n' + str (train)) 

    # plot_counts (train)

    # Train set contains multiple measurements for each point in the map.
    # We take the mean over the available measurements.
    meanTrainSamples = train.groupby ('coordinates', as_index=False).mean ()
    log.debug ('\nMean trains samples\n' + str (meanTrainSamples))

    num_cols = 5
    num_plots = len (results ['firstVehicleIndex'].unique ())
    num_rows = ceil (num_plots / num_cols)
    fig_predictions, ax_predictions = plt.subplots (num_rows, num_cols, 
                                                    figsize=(7*num_rows, 9*num_cols), 
                                                    squeeze=False)
    fig_error, ax_error = plt.subplots (num_rows, num_cols, 
                                        figsize=(7*num_rows, 9*num_cols), 
                                        squeeze=False)
                                        
    nn_mse = []
    lin_mse = []
    movAv_mse = []
    idw_mse = []
    nn_accScore = []
    lin_accScore = []
    movAv_accScore = []
    idw_accScore = []
    nn_precScore = []
    lin_precScore = []
    movAv_precScore = []
    idw_precScore = []
    nn_recallScore = []
    lin_recallScore = []
    movAv_recallScore = []
    idw_recallScore = []
    for i in results ['firstVehicleIndex'].unique ():
        print ('Testing vehicle ' + str (i))
        # create test set
        # consider a single trajectory at a time
        test = map_position_to_metric (results [results ['firstVehicleIndex'] == i], 'delay [s]')
        test ['coordinates'] = list (zip (test ['x'], test ['y']))
        
        # predict the values measured by the vehicle during its trajectory
        nn_predictions = predict (meanTrainSamples, test ['coordinates'].to_list (), 'nearest')
        # NOTE linear predictions may not be feasible for each point in the 
        # trajectory, because the point may lay "outside of the convex hull of 
        # the input points." 
        # In this case, we use NN to predict the experienced delay. 
        lin_predictions = predict (meanTrainSamples, test ['coordinates'].to_list (), 'linear')
        lin_predictions [np.isnan (lin_predictions)] = nn_predictions [np.isnan (lin_predictions)]
        movAv_predictions = movAv_predict (meanTrainSamples, test ['coordinates'].to_list (), numNeighbors)
        idw_predictions = movAv_predict (meanTrainSamples, test ['coordinates'].to_list (), numNeighbors, idw=True)
        # import pdb; pdb.set_trace ()

        row_index = int (i / num_cols)
        col_index = i % num_cols

        # determine the QoS classes based on the predicted values 
        nn_class = nn_predictions < DELAY_REQ
        nn_class = nn_class.astype (int)
        lin_class = lin_predictions < DELAY_REQ
        lin_class = lin_class.astype (int)
        movAv_class = np.array (movAv_predictions) < DELAY_REQ
        movAv_class = movAv_class.astype (int)
        idw_class = np.array (idw_predictions) < DELAY_REQ
        idw_class = idw_class.astype (int)

        trueValues = test ['delay [s]'] # true values to test regression performance
        trueClasses = test ['delay [s]'] < DELAY_REQ # true values to test classification performance
        trueClasses = trueClasses.astype (int) 

        # REGRESSION PERFORMANCE
        # plot predictions vs true values
        ax_predictions [row_index, col_index].plot (trueValues, label='true')
        ax_predictions [row_index, col_index].plot (nn_predictions, label='nn')
        ax_predictions [row_index, col_index].plot (lin_predictions, label='lin')
        ax_predictions [row_index, col_index].plot (movAv_predictions, label='movAv')
        ax_predictions [row_index, col_index].plot (idw_predictions, label='idw')
        ax_predictions [row_index, col_index].grid ()
        ax_predictions [row_index, col_index].set_title('Vehicle ' + str (i))
        ax_predictions [row_index, col_index].set_ylabel ('delay [s]')
        ax_predictions [row_index, col_index].set_xlabel ('Time index')
        ax_predictions [row_index, col_index].legend ()
        
        # plot mean absolute error
        ax_error [row_index, col_index].plot (abs (trueValues - nn_predictions), label='nn')
        ax_error [row_index, col_index].plot (abs (trueValues - lin_predictions), label='lin')
        ax_error [row_index, col_index].plot (abs (trueValues - movAv_predictions), label='movAv')
        ax_error [row_index, col_index].plot (abs (trueValues - idw_predictions), label='idw')
        ax_error [row_index, col_index].grid ()
        ax_error [row_index, col_index].set_title('Vehicle ' + str (i))
        ax_error [row_index, col_index].set_ylabel ('abs error')
        ax_error [row_index, col_index].set_xlabel ('Time index')
        ax_error [row_index, col_index].legend ()
            
        # compute the MSE
        nn_mse.append (mean_squared_error (trueValues.to_list (), nn_predictions))
        # linear prediction may not be feasible in all the test locations, therefore
        # lin_predictions may contain some nan values. This prevents the computation 
        # of the MSE. Therefore, we remove the nan values before computing the MSE
        lin_mse.append (mean_squared_error (trueValues [np.invert (np.isnan (lin_predictions))].to_list (), 
                                            lin_predictions [np.invert (np.isnan (lin_predictions))]))
        movAv_mse.append (mean_squared_error (trueValues.to_list (), movAv_predictions))
        idw_mse.append (mean_squared_error (trueValues.to_list (), idw_predictions))
        
        # CLASSIFICATION PERFORMANCE
        # Accuracy
        nn_accScore.append (accuracy_score (trueClasses, nn_class))
        lin_accScore.append (accuracy_score (trueClasses, lin_class))
        movAv_accScore.append (accuracy_score (trueClasses, movAv_class))
        idw_accScore.append (accuracy_score (trueClasses, idw_class))
        
        # Precision
        nn_precScore.append (precision_score (trueClasses, nn_class))
        lin_precScore.append (precision_score (trueClasses, lin_class))
        movAv_precScore.append (precision_score (trueClasses, movAv_class))
        idw_precScore.append (precision_score (trueClasses, idw_class))
        
        # Recall
        nn_recallScore.append (recall_score (trueClasses, nn_class))
        lin_recallScore.append (recall_score (trueClasses, lin_class))
        movAv_recallScore.append (recall_score (trueClasses, movAv_class))
        idw_recallScore.append (recall_score (trueClasses, idw_class))
        
    fig_predictions.tight_layout ()
    fig_error.tight_layout ()
    save_figure (fig_predictions, figure_folder + 'predictions.pdf')
    save_figure (fig_error, figure_folder + 'abs-error.pdf')

    # plot MSE
    fig_mse, ax_mse = plt.subplots (1, 1)
    width = 0.2
    ax_mse.bar (results ['firstVehicleIndex'].unique () - 0.5, nn_mse, width=width, label='nn')
    ax_mse.bar (results ['firstVehicleIndex'].unique () - 0.5 + width, lin_mse, width=width, label='lin')
    ax_mse.bar (results ['firstVehicleIndex'].unique () - 0.5 + 2*width, movAv_mse, width=width, label='movAv')
    ax_mse.bar (results ['firstVehicleIndex'].unique () - 0.5 + 3*width, idw_mse, width=width, label='idw')
    ax_mse.set_ylabel ('MSE')
    ax_mse.set_yscale ('log')
    ax_mse.legend ()
    ax_mse.grid ()
    save_figure (fig_mse, figure_folder + 'mse.pdf')
    
    # save MSE in a dataframe and print it as csv
    df_metrics = pd.DataFrame (columns = ['firstVehicleIndex', 
                                          'NN mse', 'NN accuracy', 'NN precision', 'NN recall', 
                                          'LIN mse', 'LIN accuracy', 'LIN precision', 'LIN recall', 
                                          'MOV_AV mse', 'MOV_AV accuracy', 'MOV_AV precision', 'MOV_AV recall', 
                                          'IDW mse', 'IDW accuracy', 'IDW precision', 'IDW recall'])

    df_metrics ['firstVehicleIndex'] = results ['firstVehicleIndex'].unique ()
    df_metrics ['NN mse'] = nn_mse
    df_metrics ['LIN mse'] = lin_mse
    df_metrics ['MOV_AV mse'] = movAv_mse
    df_metrics ['IDW mse'] = idw_mse

    df_metrics ['NN accuracy'] = nn_accScore
    df_metrics ['LIN accuracy'] = lin_accScore
    df_metrics ['MOV_AV accuracy'] = movAv_accScore
    df_metrics ['IDW accuracy'] = idw_accScore

    df_metrics ['NN precision'] = nn_precScore
    df_metrics ['LIN precision'] = lin_precScore
    df_metrics ['MOV_AV precision'] = movAv_precScore
    df_metrics ['IDW precision'] = idw_precScore

    df_metrics ['NN recall'] = nn_recallScore
    df_metrics ['LIN recall'] = lin_recallScore
    df_metrics ['MOV_AV recall'] = movAv_recallScore
    df_metrics ['IDW recall'] = idw_recallScore
    df_metrics.to_csv (figure_folder + 'prediction_metrics.csv')

    print ('NN\t', sum ([abs (n) for n in nn_mse]))
    print ('LIN\t', sum ([abs (n) for n in lin_mse]))
    print ('MOV_AV\t', sum ([abs (n) for n in movAv_mse]))
    print ('IDW\t', sum ([abs (n) for n in idw_mse]))

if __name__ == "__main__":
    
    # define default arguments
    campaignName = 'test-periodicity'
    kittiModelList = [1450]
    numVisitedLocationsList = [100]
    numNeighborsList = [5]
    
    # read command line parameters (if any)
    parser = argparse.ArgumentParser(description='Perform QoS predictions')
    parser.add_argument('-c', type=ascii, nargs=1, dest='campaignName',
                        help='name of the simulation campaign')
    parser.add_argument('-k', type=int, nargs='+', dest='kittiModelList',
                        help='kitti model (can be a list)')
    parser.add_argument('-v', type=int, nargs='+', dest='numVisitedLocationsList',
                        help='number of visited locations (can be a list)')
    parser.add_argument('-n', type=int, nargs='+', dest='numNeighborsList',
                        help='number of nighbor locations (can be a list)')
    args = parser.parse_args ()

    if (args.campaignName != None):
        campaignName = args.campaignName [0] [1: len (args.campaignName [0]) - 1]
    if (args.kittiModelList != None):
        kittiModelList = args.kittiModelList
    if (args.numVisitedLocationsList != None):
        numVisitedLocationsList = args.numVisitedLocationsList
    if (args.numNeighborsList != None):
        numNeighborsList = args.numNeighborsList

    parallelExecution = True # enable/disable multi threading option
    if (parallelExecution):
        # if more than one value per command line argument is specified, run 
        # multiple processes in parallel
        proc = [] # list of running processes
        for k in kittiModelList:
            for v in numVisitedLocationsList:
                for n in numNeighborsList: 
                    p = Process (target=main, args=(campaignName, k, v, n))
                    p.start ()
                    proc.append (p)

        # join the processes that are running
        for p in proc:
            p.join ()
    else:
        for k in kittiModelList:
            for v in numVisitedLocationsList:
                for n in numNeighborsList: 
                    main (campaignName, k, v, n)
        
