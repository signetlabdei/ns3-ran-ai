import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pprint
import seaborn as sns
from io import StringIO
from math import ceil
from mmwavePlotUtils import *
from pathlib import Path
pd.set_option("display.max_rows", 100000, "display.max_columns", 100000)
# # Temporarily limit number of max cores used
# sem.parallelrunner.MAX_PARALLEL_PROCESSES = 4

def plot_stat (results, xMetric, yMetric, figName, style=','):
    num_cols = 5
    num_rows = ceil (numTrajectories / num_cols)
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
    fig.tight_layout ()

    pdf = PdfPages(figName + '.pdf')
    pdf.savefig()
    pdf.close()

ns_path = './'
ns_script = 'mmwave-gemv-integration-example'
ns_res_path = './campaigns/test-results'
figure_foder = ns_res_path + '/figures'
Path(figure_foder).mkdir(parents=True, exist_ok=True)

campaign = sem.CampaignManager.load (campaign_dir=ns_res_path)

numTrajectories = 50
params_grid = {
    "RngRun": 1,
    "firstVehicleIndex": list(range(numTrajectories)),
    "numUes": 1,
	"ulIpiMicroS": 100e3,
	"dlIpiMicroS": 500e3,
    "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_'
}
overall_list = sem.list_param_combinations(params_grid)

example_result = campaign.db.get_complete_results()[0]
# print ('This is an example result')
# pprint.pprint(example_result)

# Use the parsing function to create a Pandas dataframe
phy_folder = figure_foder + "/phy"
Path(phy_folder).mkdir(parents=True, exist_ok=True)
results = campaign.get_results_as_dataframe(read_rxPacketTrace,
                                            params=overall_list,
                                            verbose=True, 
                                            parallel_parsing=False)

plot_stat (results, 'Time [s]', 'SINR [dB]', phy_folder + '/sinr', '-')
plot_stat (results, 'Time [s]', 'MCS', phy_folder + '/mcs')
plot_stat (results, 'Time [s]', 'TB size [bytes]', phy_folder + '/tbSize')
plot_stat (results, 'Time [s]', 'OFDM symbols', phy_folder + '/symbols')

results = campaign.get_results_as_dataframe(read_dlPdcpStatsTrace,
                                            params=overall_list,
                                            verbose=True, 
                                            parallel_parsing=False)

pdcp_folder = figure_foder + "/pdcp"
Path(pdcp_folder).mkdir(parents=True, exist_ok=True)
plot_stat (results, 'end [s]', 'avg prr', pdcp_folder + '/dl-prr', '-')
plot_stat (results, 'end [s]', 'delay [s]', pdcp_folder + '/dl-delay', '-')

results = campaign.get_results_as_dataframe(read_ulPdcpStatsTrace,
                                            params=overall_list,
                                            verbose=True, 
                                            parallel_parsing=False)

plot_stat (results, 'end [s]', 'avg prr', pdcp_folder + '/ul-prr', '-')
plot_stat (results, 'end [s]', 'delay [s]', pdcp_folder + '/ul-delay', '-')

results = campaign.get_results_as_dataframe(read_dlRlcStatsTrace,
                                            params=overall_list,
                                            verbose=True, 
                                            parallel_parsing=False)

rlc_folder = figure_foder + "/rlc"
Path(rlc_folder).mkdir(parents=True, exist_ok=True)
plot_stat (results, 'end [s]', 'avg prr', rlc_folder + '/dl-prr', '-')
plot_stat (results, 'end [s]', 'delay [s]', rlc_folder + '/dl-delay', '-')

results = campaign.get_results_as_dataframe(read_ulRlcStatsTrace,
                                            params=overall_list,
                                            verbose=True, 
                                            parallel_parsing=False)

plot_stat (results, 'end [s]', 'avg prr', rlc_folder + '/ul-prr', '-')
plot_stat (results, 'end [s]', 'delay [s]', rlc_folder + '/ul-delay', '-')
