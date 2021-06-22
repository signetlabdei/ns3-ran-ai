import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# # Temporarily limit number of max cores used
# sem.parallelrunner.MAX_PARALLEL_PROCESSES = 1

campaignName = 'campaign-1'
ns_path = './'
ns_script = 'mmwave-gemv-integration-example'
ns_res_path = './campaigns/' + campaignName

campaign = sem.CampaignManager.new (ns_path=ns_path, script=ns_script, campaign_dir=ns_res_path, 
                                    optimized=True, check_repo=False, overwrite=False)

if (campaignName == 'test-results'):
    numTrajectories = 50
    params_grid = {
        "RngRun": 1,
        "firstVehicleIndex": list(range(numTrajectories)),
        "numUes": 1,
    	"ulIpiMicroS": 100e3,
    	"dlIpiMicroS": 500e3,
        "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_'
    }
elif (campaignName == 'campaign-1'):
    numTrajectories = 50
    params_grid = {
        "RngRun": 1,
        "firstVehicleIndex": list(range(numTrajectories)),
        "numUes": 1,
    	"applicationType" : 'kitti',
        "kittiModel": [1450, 1452],
    	"dlIpiMicroS": 500e3,
        "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
        "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv'
    }
else:
    print ('Unknown campaign name')
    exit ()
    
overall_list = sem.list_param_combinations(params_grid)

print ("Run simulations")
campaign.run_missing_simulations(overall_list)

def check_errors(result):
    result_filenames = campaign.db.get_result_files(result['meta']['id'])
    result_filename = result_filenames['stderr']
    with open(result_filename, 'r') as result_file:
        error_file = result_file.read()
        if (len(error_file) != 0):
            return 1
        else:
            return 0

results = campaign.db.get_results()

# Count errors
errors = []
for result_entry in results:
    errors.append(check_errors(result_entry))

num_errors = sum(errors)
print('Overall, we have {num_errors} errors out of {len(results)} simulations!')
