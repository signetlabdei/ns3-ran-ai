"""
This files defines the parameters of each simulation campaign. 
"""

"""
Returns the parameters of a certain simulation campaign

Params:
    - campaignName: the name of the simulation campaign
Return:
    - ns_path: the path to the ns-3 root folder
    - ns_script: the name of the simulation script
    - ns_res_path: the path to the simulation results
    - params_grid: dictionary containing the simulation params
    - figure_path: the path to the figures folder
"""
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
    elif (campaignName == 'campaign-2'):
        numTrajectories = 50
        params_grid = {
            "RngRun": 1,
            "firstVehicleIndex": list(range(numTrajectories)),
            "numUes": 1,
        	"applicationType" : 'kitti',
            "kittiModel": [0, 1, 2, 1150, 1450, 1451, 1452],
            "txPower" : 23,
        	"dlIpiMicroS": 500e3,
            "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
            "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv'
        }
        figure_path = ns_res_path + '/figures/'
    elif (campaignName == 'test-periodicity'):
        # Simulations with higher periodicity in the collection of the traces
        numTrajectories = 50
        params_grid = {
            "RngRun": 1,
            "firstVehicleIndex": list(range(numTrajectories)),
            "numUes": 1,
        	"applicationType" : 'kitti',
            "kittiModel": [0, 1, 2, 1150, 1450, 1451, 1452],
            "txPower" : 23,
        	"dlIpiMicroS": 500e3,
            "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
            "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv',
            "tracesPeriodicity" : 500
        }
        figure_path = ns_res_path + '/figures/' 
    elif (campaignName == 'offline-train-dataset'):
        ns_script = 'ran-ai'
        numTrajectories = 50
        params_grid = {
            "RngRun": 1,
            "firstVehicleIndex": list(range(numTrajectories)),
            "numUes": 2,
        	"applicationType" : 'kitti',
            "kittiModel": [1452],
        	"dlIpiMicroS": 500e3,
        	"useFakeRanAi": True,
            "simDuration": 90,
            "txPower" : 23,
            "gemvTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/bolognaLeftHalfRSU3_50vehicles_100sec/13-May-2021_',
            "appTracesPath" : '/media/vol2/zugnotom/rsync/ns3-mmwave-pqos/input/kitti-dataset.csv'
        }
        figure_path = ns_res_path + '/figures/'      
    else:
        print ('Unknown campaign name')
        exit ()
    
    return (ns_path, ns_script, ns_res_path, params_grid, figure_path)
