def get_campaign_params (campaignName, kittiModel):
    ns_path = './'
    ns_script = 'mmwave-gemv-integration-example'
    ns_res_path = './campaigns/' + campaignName

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
        figure_path = ns_res_path + '/figures'
    elif ((campaignName == 'campaign-1') or (campaignName == 'test-tx-power')):
        numTrajectories = 50
        params_grid = {
            "RngRun": 1,
            "firstVehicleIndex": list(range(numTrajectories)),
            "numUes": 1,
        	"applicationType" : 'kitti',
            "kittiModel": kittiModel,
        	"dlIpiMicroS": 500e3,
            "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
            "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv'
        }
        figure_path = ns_res_path + '/figures/' + str (params_grid['kittiModel'])
    else:
        print ('Unknown campaign name')
        exit ()
    
    return (ns_path, ns_script, ns_res_path, params_grid, figure_path)
