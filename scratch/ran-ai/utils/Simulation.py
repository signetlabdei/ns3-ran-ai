import os
import numpy as np
from agent.Agent import CentralizedAgent


def get_input(args: []):

    algorithm_training = args['train'] # Train the algorithm
    algorithm_testing = args['test'] # Test the algorithm
    offline_running = args['offline'] # Train the algorithm
    agent_policy = args['agent_policy'] # Agent policy

    if algorithm_training:
        assert agent_policy == 'dql'

    running = args['run'] # Run the simulation
    user_num = args['user_num']  # Number of users
    tx_power = args['tx_power']  # Tx power
    reward_penalty = args['reward_penalty']  # Reward penalty when QoS is violated
    plot_format = args['format'] # Format of the output plots
    mode = args['mode'] # KPI of the communication scenario
    
    if args['multi_alpha']:
        reward_alpha = [0.5, 1.0]
    else:
        reward_alpha = [args['reward_alpha']]  # Reward parameter to balance QoS and QoE

    step_num = args['step_num']  # Number of steps per episode
    transfer = args['transfer']  # Transfer learning
    input_offline_running = args['input_offline']  # Offline input

    # Ideal or real action update
    if args['update'] == 'ideal':
        ideal_update = True
    elif args['update'] == 'real':
        ideal_update = False
    else:
        raise ValueError

    # Consider the delay due to data encoding
    if args['delay'] == 'add':
        additional_delay = True
    elif args['delay'] == 'none':
        additional_delay = False
    else:
        raise ValueError

    if offline_running:
        offline_folder = 'offline_dataset/'

        # Offline data folder
        if ideal_update:
            if additional_delay:
                offline_folder += 'ideal_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
            else:
                offline_folder += 'ideal_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
        else:
            if additional_delay:
                offline_folder += 'real_update_add_delay/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'
            else:
                offline_folder += 'real_update/user=' + str(user_num) + '/power=' + str(tx_power) + '/process_data/'

        # Number of episode
        if args['episode_num'] is None:
            vehicle_folders = os.listdir(offline_folder)
            vehicle_num = len(vehicle_folders)
            action_folders = os.listdir(vehicle_folders[0])
            action_num = len(action_folders)
            episode_num = vehicle_num * action_num
        else:
            if agent_policy != 'random':
                episode_num = args['episode_num']
            else:
                raise ValueError

    else:

        # Offline data folder        
        offline_folder = None
        # Number of episodes
        episode_num = args['episode_num']  

    # Input parameters

    if args['input_user_num'] is None:
        input_user_num = user_num
    else:
        input_user_num = args['input_user_num']

    if args['input_tx_power'] is None:
        input_tx_power = tx_power
    else:
        input_tx_power = args['input_tx_power']

    if args['input_reward_penalty'] is None:
        input_reward_penalty = reward_penalty
    else:
        input_reward_penalty = args['input_reward_penalty']

    if args['input_reward_alpha'] is None:
        input_reward_alpha = reward_alpha
    else:
        if args['multi_alpha']:
            raise ValueError
        else:
            input_reward_alpha = [args['input_reward_alpha']]

    if args['input_episode_num'] is None:
        input_episode_num = episode_num
    else:
        input_episode_num = args['input_episode_num']

    if args['input_step_num'] is None:
        input_step_num = step_num
    else:
        input_step_num = args['input_step_num']

    if args['input_update'] is None:
        input_ideal_update = ideal_update
    else:
        if args['input_update'] == 'ideal':
            input_ideal_update = True
        elif args['input_update'] == 'real':
            input_ideal_update = False
        else:
            raise ValueError

    if args['input_delay'] is None:
        input_additional_delay = additional_delay
    else:
        if args['input_delay'] == 'add':
            input_additional_delay = True
        elif args['input_delay'] == 'none':
            input_additional_delay = False
        else:
            raise ValueError

    return algorithm_training, algorithm_testing, agent_policy, running, offline_folder, transfer, \
           user_num, tx_power, reward_penalty, reward_alpha, episode_num, step_num, ideal_update, additional_delay, offline_running, \
           input_user_num, input_tx_power, input_reward_penalty, input_reward_alpha, input_episode_num,\
           input_step_num, input_ideal_update, input_additional_delay, input_offline_running, plot_format, mode


def initialize_simulation(mode: str,
                          algorithm_training: bool,
                          algorithm_testing: bool,
                          user_num: int,
                          tx_power: int,
                          reward_penalty: float,
                          reward_alpha: float,
                          episode_num: int,
                          step_num: int,
                          ideal_update: bool,
                          additional_delay: bool,
                          offline_running: bool,
                          input_user_num: int,
                          input_tx_power: int,
                          input_reward_penalty: float,
                          input_reward_alpha: float,
                          input_episode_num: int,
                          input_step_num: int,
                          input_ideal_update: bool,
                          input_additional_delay: bool, 
                          input_offline_running: bool,
                          agent: CentralizedAgent,
                          transfer: bool,
                          agent_policy: str,
                          step_duration: float,
                          action_labels: [str],
                          action_penalties: [float]
                          ):

    # Determine input and output folders

    if offline_running and agent_policy == 'dql':
        offline_flag = '_offline'
    else:
        offline_flag = ''

    if ideal_update:
        if additional_delay:
            scenario_name = mode + '/ideal_update_add_delay/'
        else:
            scenario_name = mode + '/ideal_update/'
    else:
        if additional_delay:
            scenario_name = mode + '/real_update_add_delay/'
        else:
            scenario_name = mode + '/real_update/'

    scenario_name += 'user=' + str(user_num) + '/power=' + str(tx_power) + '/penalty=' + str(reward_penalty) + '/alpha=' + str(reward_alpha) + '/episode=' + str(
        episode_num) + str(offline_flag) + '/step=' + str(step_num) + '/'

    if input_offline_running:
        input_offline_flag = '_offline'
    else:
        input_offline_flag = ''

    if input_ideal_update:
        if input_additional_delay:
            input_scenario_name = mode + '/ideal_update_add_delay/'
        else:
            input_scenario_name = mode + '/ideal_update/'
    else:
        if input_additional_delay:
            input_scenario_name = mode + '/real_update_add_delay/'
        else:
            input_scenario_name = mode + '/real_update/'

    input_scenario_name += 'user=' + str(input_user_num) + '/power=' + str(input_tx_power) + '/penalty=' + str(
        input_reward_penalty) + '/alpha=' + str(input_reward_alpha) + '/episode=' + str(input_episode_num) + str(input_offline_flag) + '/step=' + str(
        input_step_num) + '/'

    input_folder = 'output/train/' + input_scenario_name  # Input folder

    if algorithm_training:

        assert agent_policy == 'dql'

        print("TRAINING")

        data_folder = 'output/train/' + scenario_name  # Output folder

        if transfer:
            agent.load_model(input_folder)  # Load the learning architecture

    elif algorithm_testing:

        print("TESTING")

        data_folder = 'output/test/' + scenario_name + agent_policy + '/'  # Output folder

        if agent_policy == 'dql':
            agent.load_model(input_folder)  # Load the learning architecture

    else:

        raise ValueError

    for data_type in ['state', 'learn', 'performance']:
        for user_idx in range(user_num):
            user_folder = data_folder + '/' + data_type + '/' + str(user_idx) + '/'
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

    # Duration of the simulation [s]
    sim_duration = 5 + step_num * step_duration / 1000 
    simulation_time = 0

    # Index of the action chosen by the static strategy
    default_action_index = None  
    if agent_policy != 'dql' and agent_policy != 'random' and not offline_running:
        default_action_index = action_labels.index(int(agent_policy))

    # Penalty given by not addressing the QoS requirements
    max_penalty = reward_penalty + np.max(action_penalties)  
    agent.max_penalty = max_penalty

    # Temperature for the agent training
    temperatures = get_temperature(episode_num)
    temp = 0

    return data_folder, sim_duration, default_action_index, max_penalty, simulation_time, temperatures, temp


def get_temperature(episode_num: int):

    temperatures = np.flip(np.arange(.1, 1, .9 / episode_num))

    return temperatures
