def get_campaign_params (campaignName):
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
    elif (campaignName == 'campaign-1'):
        numTrajectories = 50
        params_grid = {
            "RngRun": 1,
            "firstVehicleIndex": list(range(numTrajectories)),
            "numUes": 1,
        	"applicationType" : 'kitti',
            "kittiModel": [0, 1, 2, 1150, 1450, 1451, 1452],
        	"dlIpiMicroS": 500e3,
            "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
            "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv'
        }
        figure_path = ns_res_path + '/figures/'
    elif (campaignName == 'test-tx-power'):
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
        figure_path = ns_res_path + '/figures/'       
    else:
        print ('Unknown campaign name')
        exit ()
    
    return (ns_path, ns_script, ns_res_path, params_grid, figure_path)
