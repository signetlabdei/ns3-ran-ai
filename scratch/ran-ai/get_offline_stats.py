import sem
import pandas as pd
import os
import sys
import argparse
sys.path.insert(1, '../../')
from scripts.mmwavePlotUtils import read_ran_ai

parser = argparse.ArgumentParser()

parser.add_argument('-run', '--run', action='store_const', const=True, default=False)
parser.add_argument('-user', '--user_num', type=int, default=1)
parser.add_argument('-power', '--tx_power', type=int, default=23)
parser.add_argument('-rep', '--repetition', type=int, default=1)
parser.add_argument('-sim_duration', '--sim_duration', type=int, default=85)
parser.add_argument('-ideal_update', '--ideal_update', action='store_const', const=True, default=False)
parser.add_argument('-add_delay', '--add_delay', action='store_const', const=True, default=False)

args = vars(parser.parse_args())

pd.set_option("display.max_rows", 100000, "display.max_columns", 100000)

campaign_name = 'trial'

rng_range = list(range(1, args['repetition'] + 1))
vehicle_index_range = list(range(1, 51))
application_range = [1450, 1451, 1452]
user_num = args['user_num']
tx_power = args['tx_power']
sim_duration = args['sim_duration']  # Second
ideal_update = args['ideal_update']
add_delay = args['add_delay']

params_grid = {
    "RngRun": rng_range,
    "firstVehicleIndex": vehicle_index_range,
    "numUes": user_num,
    "applicationType": 'kitti',
    "kittiModel": application_range,
    "useFakeRanAi": True,
    "simDuration": sim_duration,
    "txPower": tx_power,
    "idealActionUpdate": ideal_update,
    "additionalDelay": add_delay,
    "gemvTracesPath": '/home/masonfed/git_repos/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
    "appTracesPath": '/home/masonfed/git_repos/ns3-mmwave-pqos/input/kitti-dataset.csv',
}

raw_path = 'offline_dataset/'
process_path = 'offline_dataset/'
if ideal_update:
    if add_delay:
        raw_path += 'ideal_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/raw_data/'
        process_path += 'ideal_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
    else:
        raw_path += 'ideal_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/raw_data/'
        process_path += 'ideal_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
else:
    if add_delay:
        raw_path += 'real_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/raw_data/'
        process_path += 'real_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
    else:
        raw_path += 'real_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/raw_data/'
        process_path += 'real_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'

if not os.path.exists(process_path):
    os.makedirs(process_path)
if not os.path.exists(raw_path):
    os.makedirs(raw_path)

ns_path = '../../'
ns_script = 'ran-ai'

campaign = sem.CampaignManager.new(ns_path=ns_path, script=ns_script, campaign_dir=raw_path, check_repo=False,
                                   overwrite=True, runner_type="ParallelRunner")

overall_list = sem.list_param_combinations(params_grid)

if args['run']:
    campaign.run_missing_simulations(overall_list)

results = campaign.db.get_results()

run = -1

for rng in rng_range:

    for vehicleIndex in vehicle_index_range:

        run += 1

        for kittiModel in application_range:

            params_grid["firstVehicleIndex"] = vehicleIndex
            params_grid["kittiModel"] = kittiModel

            overall_list = sem.list_param_combinations(params_grid)

            results = campaign.get_results_as_dataframe(read_ran_ai,
                                                        params=overall_list,
                                                        verbose=True,
                                                        parallel_parsing=False)

            new_outputs_path = process_path + str(run) + '/' + str(kittiModel) + '/'

            if not os.path.exists(new_outputs_path):
                os.makedirs(new_outputs_path)

            results.to_pickle(new_outputs_path + 'data.pkl')
