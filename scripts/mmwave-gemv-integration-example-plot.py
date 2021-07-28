from mmwave_gemv_integration_campaigns import * 
from mmwave_gemv_integration_example_utils import * 
from mmwavePlotUtils import *
import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.colors as colors
from io import StringIO
from pathlib import Path
from mpl_toolkits import mplot3d
pd.set_option("display.max_rows", 100000, "display.max_columns", 100000)
# Temporarily limit number of max cores used
# sem.parallelrunner.MAX_PARALLEL_PROCESSES = 4

# name of the simulation campaign
campaignName = 'campaign-2'

# enable/disable plots
phyPlots = False
appPlots = False
pdcpPlots = False
rlcPlots = False
load = True

(ns_path, ns_script, ns_res_path, 
allParams, base_figure_foder) = get_campaign_params (campaignName)
for kittiModel in allParams ['kittiModel']:

    params_grid = allParams
    params_grid ['kittiModel'] = kittiModel
    figure_foder = base_figure_foder + str (kittiModel)
    Path(figure_foder).mkdir(parents=True, exist_ok=True)

    campaign = sem.CampaignManager.load (campaign_dir=ns_res_path)
    overall_list = sem.list_param_combinations(params_grid)

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
        # plot_stat (results, 'end [s]', 'avg throughput [bps]', pdcp_folder + '/dl-thr', '*')
        plot_stat (results, 'end [s]', 'delay [s]', pdcp_folder + '/dl-delay', '-')
        plot_metric_map (results, 'delay [s]', pdcp_folder + '/dl-delay-map')
        plot_metric_map (results, 'avg prr', pdcp_folder + '/dl-prr-map')
        # plot_metric_map (results, 'avg throughput [bps]', pdcp_folder + '/dl-thr-map')
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
        # plot_stat (results, 'end [s]', 'avg throughput [bps]', rlc_folder + '/dl-thr', '*')
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
        
    if (load):
        load_folder = figure_foder + "/load"
        Path(load_folder).mkdir(parents=True, exist_ok=True)
        results = campaign.get_results_as_dataframe(calc_ofdm_sym,
                                                    params=overall_list,
                                                    verbose=True, 
                                                    parallel_parsing=False)
        available_sym = 100 * 4 * 12 # 100 subframes * 4 slots per sf * 12 data symbols
        results ['load'] = results ['OFDM symbols'] / available_sym
        plot_stat (results, 'Time [s]', 'load', load_folder + '/load', '-')
