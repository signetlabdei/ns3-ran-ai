from mmwave_gemv_integration_campaigns import * 
import sem
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# # Temporarily limit number of max cores used
# sem.parallelrunner.MAX_PARALLEL_PROCESSES = 1

campaignName  = 'test-periodicity'
(ns_path, ns_script, ns_res_path, 
 params_grid, _) = get_campaign_params (campaignName)

campaign = sem.CampaignManager.new (ns_path=ns_path, script=ns_script, campaign_dir=ns_res_path, 
                                    optimized=True, check_repo=False, overwrite=False)
    
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
print(f'Overall, we have {num_errors} errors out of {len(results)} simulations!')
