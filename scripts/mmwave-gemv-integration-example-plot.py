from mmwave_gemv_integration_campaigns import * 
import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors
import pprint
import seaborn as sns
from io import StringIO
from math import ceil
from mmwavePlotUtils import *
from pathlib import Path
from mpl_toolkits import mplot3d
# pd.set_option("display.max_rows", 100000, "display.max_columns", 100000)
# # Temporarily limit number of max cores used
# sem.parallelrunner.MAX_PARALLEL_PROCESSES = 4

def save_figure (fig, path):
    overwrite = True
    plt.figure (fig.number)
    if overwrite == False and Path (path).exists():
        input ("File already exists, overwrite?")
    pdf = PdfPages(path)
    pdf.savefig()
    pdf.close()
    plt.close ()
    
def plot_stat (results, xMetric, yMetric, figName, style='-'):
    num_cols = 5
    num_plots = len (results ['firstVehicleIndex'].unique ())
    num_rows = ceil (num_plots / num_cols)
    fig, ax = plt.subplots (num_rows, num_cols, figsize=(7*num_rows, 9*num_cols), 
                            squeeze=False)
    
    for i in results ['firstVehicleIndex'].unique ():
        x = results [(results ['firstVehicleIndex'] == i)][xMetric]
        y = results [(results ['firstVehicleIndex'] == i)][yMetric]
        row_index = int (i / num_cols)
        col_index = i % num_cols
        ax [row_index, col_index].plot (x, y, style)
        ax [row_index, col_index].grid ()
        ax [row_index, col_index].set_title('Vehicle ' + str (i))
        ax [row_index, col_index].set_xlabel (xMetric)
        ax [row_index, col_index].set_ylabel (yMetric)
        if (yMetric == 'avg prr' or yMetric == 'avg throughput [bps]' or yMetric == 'delay [s]'):
            ax [row_index, col_index].set_ylim (bottom=0, top=max (y)*1.1)
    fig.tight_layout ()
    save_figure (fig, figName + '.pdf')
    

def map_position_to_metric (vehicleIndex, rlcOrPdcpStat, metric):
    mobilityPath = "input/bolognaLeftHalfRSU3_50vehicles_100sec/mobility/nodes/"
    mobilityDf = pd.read_csv (mobilityPath + "node-" + str (vehicleIndex) + ".txt", 
                              header=None, delimiter=" ", names=['time [s]', 'x', 'y']) 
    rlcOrPdcpStat = rlcOrPdcpStat [(rlcOrPdcpStat ['firstVehicleIndex'] == vehicleIndex)][['start [s]','end [s]', metric]]
    x = []
    y = []
    z = []
    for index, row in mobilityDf.iterrows ():
        values = rlcOrPdcpStat [(row ['time [s]'] >= rlcOrPdcpStat ['start [s]']) &
                                (row ['time [s]'] < rlcOrPdcpStat ['end [s]'])] [metric].values
        if (len (values) == 0):
            continue
        if (len (values) > 1):
            print (rlcOrPdcpStat [(row ['time [s]'] >= rlcOrPdcpStat ['start [s]']) &
                                    (row ['time [s]'] < rlcOrPdcpStat ['end [s]'])])
            print ("Error: more than 1 delay value")
            exit ()
        x += [float (row ['x'])]
        y += [float (row ['y'])]
        z += [float (values [0])]
    return x,y,z
    
def plot_metric_map (rlcOrPdcpResult, metric, figName, gamma=0.5):
    fig, ax = plt.subplots (1, 1)
    ax.grid ()
    allXYZ = pd.DataFrame ()
    for i in results ['firstVehicleIndex'].unique ():
        (x, y, z) = map_position_to_metric (i, rlcOrPdcpResult, metric)
        data = {'x' : x, 'y' : y, metric : z}
        allXYZ = allXYZ.append (pd.DataFrame (data), ignore_index=True)

    allXYZ = allXYZ.groupby (['x', 'y'], as_index=False).mean ()
    vMax = max (allXYZ [metric])
    if (metric == 'avg prr'):
        vMax = 1
    im = ax.scatter (allXYZ ['x'], allXYZ ['y'], c=allXYZ [metric], s=0.7,
                     norm=colors.PowerNorm(gamma=gamma), cmap="rainbow", 
                     vmin=0, vmax=vMax)
    ax.set_xlim ([11.310, 11.3215])
    ax.set_ylim ([44.491, 44.4975])
    ax.ticklabel_format(useOffset=False)
    fig.colorbar (im, ax=ax)
    plt.title (metric)
    save_figure (fig, figName + '.pdf')
    
def plot_box (rlcOrPdcpResult, metric, figName):
    fig, ax = plt.subplots (1, 1)
    ax.grid ()
    ax.violinplot (rlcOrPdcpResult [metric], showmeans=True)
    ax.set_ylabel (metric)
    save_figure (fig, figName + '.pdf')
    
campaignName = 'test-tx-power'
(ns_path, ns_script, ns_res_path, 
allParams, figure_foder) = get_campaign_params (campaignName)
for kittiModel in allParams ['kittiModel']:

    params_grid = allParams [allParams ['kittiModel'] == kittiModel]
    figure_foder = figure_foder + str (kittiModel)
    Path(figure_foder).mkdir(parents=True, exist_ok=True)

    campaign = sem.CampaignManager.load (campaign_dir=ns_res_path)
    overall_list = sem.list_param_combinations(params_grid)

    # Use the parsing function to create a Pandas dataframe
    phyPlots = False
    appPlots = True
    pdcpPlots = True
    rlcPlots = True

    if (phyPlots):
        phy_folder = figure_foder + "/phy"
        Path(phy_folder).mkdir(parents=True, exist_ok=True)
        results = campaign.get_results_as_dataframe(sample_rxPacketTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
                                                    
        plot_stat (results [results ['UL/DL'] == 'UL'], 'Time [s]', 'SINR [dB]', phy_folder + '/ul-sinr', '-')
        plot_stat (results [results ['UL/DL'] == 'UL'], 'Time [s]', 'MCS', phy_folder + '/ul-mcs')
        plot_stat (results [results ['UL/DL'] == 'UL'], 'Time [s]', 'TB size [bytes]', phy_folder + '/ul-tbSize')
        plot_stat (results [results ['UL/DL'] == 'UL'], 'Time [s]', 'OFDM symbols', phy_folder + '/ul-symbols')
        plot_stat (results [results ['UL/DL'] == 'DL'], 'Time [s]', 'SINR [dB]', phy_folder + '/dl-sinr', '-')
        plot_stat (results [results ['UL/DL'] == 'DL'], 'Time [s]', 'MCS', phy_folder + '/dl-mcs')
        plot_stat (results [results ['UL/DL'] == 'DL'], 'Time [s]', 'TB size [bytes]', phy_folder + '/dl-tbSize')
        plot_stat (results [results ['UL/DL'] == 'DL'], 'Time [s]', 'OFDM symbols', phy_folder + '/dl-symbols')

    if (appPlots):        
        results = campaign.get_results_as_dataframe(read_appStatsTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)

        app_folder = figure_foder + "/app"
        Path(app_folder).mkdir(parents=True, exist_ok=True)
        plot_stat (results, 'end [s]', 'avg prr', app_folder + '/prr', '-')
        plot_stat (results, 'end [s]', 'avg throughput [bps]', app_folder + '/thr', '-')
        plot_stat (results, 'end [s]', 'delay [s]', app_folder + '/delay', '-')
        plot_metric_map (results, 'delay [s]', app_folder + '/delay-map')
        plot_metric_map (results, 'avg prr', app_folder + '/prr-map')
        plot_metric_map (results, 'avg throughput [bps]', app_folder + '/thr-map')
        plot_box (results, 'delay [s]', app_folder + '/delay-box')

    if (pdcpPlots):
        results = campaign.get_results_as_dataframe(read_dlPdcpStatsTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
        results = results [ results ['LCID'] >= 3 ] # only data channels

        pdcp_folder = figure_foder + "/pdcp"
        Path(pdcp_folder).mkdir(parents=True, exist_ok=True)
        plot_stat (results, 'end [s]', 'avg prr', pdcp_folder + '/dl-prr', '-')
        plot_stat (results, 'end [s]', 'avg throughput [bps]', pdcp_folder + '/dl-thr', '-')
        plot_stat (results, 'end [s]', 'delay [s]', pdcp_folder + '/dl-delay', '-')
        plot_metric_map (results, 'delay [s]', pdcp_folder + '/dl-delay-map')
        plot_metric_map (results, 'avg prr', pdcp_folder + '/dl-prr-map')
        plot_metric_map (results, 'avg throughput [bps]', pdcp_folder + '/dl-thr-map')
        plot_box (results, 'delay [s]', pdcp_folder + '/dl-delay-box')

        results = campaign.get_results_as_dataframe(read_ulPdcpStatsTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
        results = results [ results ['LCID'] >= 3 ] # only data channels

        plot_stat (results, 'end [s]', 'avg prr', pdcp_folder + '/ul-prr', '-')
        plot_stat (results, 'end [s]', 'avg throughput [bps]', pdcp_folder + '/ul-thr', '-')
        plot_stat (results, 'end [s]', 'delay [s]', pdcp_folder + '/ul-delay', '-')
        plot_metric_map (results, 'delay [s]', pdcp_folder + '/ul-delay-map', gamma = 0.30)
        plot_metric_map (results, 'avg prr', pdcp_folder + '/ul-prr-map')
        plot_metric_map (results, 'avg throughput [bps]', pdcp_folder + '/ul-thr-map')
        plot_box (results, 'delay [s]', pdcp_folder + '/ul-delay-box')

    if (rlcPlots):
        results = campaign.get_results_as_dataframe(read_dlRlcStatsTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
        results = results [ results ['LCID'] >= 3 ] # only data channels                                

        rlc_folder = figure_foder + "/rlc"
        Path(rlc_folder).mkdir(parents=True, exist_ok=True)
        plot_stat (results, 'end [s]', 'avg prr', rlc_folder + '/dl-prr', '-')
        plot_stat (results, 'end [s]', 'avg throughput [bps]', rlc_folder + '/dl-thr', '-')
        plot_stat (results, 'end [s]', 'delay [s]', rlc_folder + '/dl-delay', '-')
        plot_metric_map (results, 'delay [s]', rlc_folder + '/dl-delay-map')
        plot_metric_map (results, 'avg prr', rlc_folder + '/dl-prr-map')
        # plot_metric_map (results, 'avg throughput [bps]', rlc_folder + '/dl-thr-map')
        plot_box (results, 'delay [s]', rlc_folder + '/dl-delay-box')

        results = campaign.get_results_as_dataframe(read_ulRlcStatsTrace,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
        results = results [ results ['LCID'] >= 3 ] # only data channels

        plot_stat (results, 'end [s]', 'avg prr', rlc_folder + '/ul-prr', '-')
        plot_stat (results, 'end [s]', 'avg throughput [bps]', rlc_folder + '/ul-thr', '-')
        plot_stat (results, 'end [s]', 'delay [s]', rlc_folder + '/ul-delay', '-')                                        
        plot_metric_map (results, 'delay [s]', rlc_folder + '/ul-delay-map', gamma = 0.30)
        plot_metric_map (results, 'avg prr', rlc_folder + '/ul-prr-map')
        plot_metric_map (results, 'avg throughput [bps]', rlc_folder + '/ul-thr-map')
        plot_box (results, 'delay [s]', rlc_folder + '/ul-delay-box')
