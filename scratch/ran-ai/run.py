from py_interface import FreeMemory, Experiment
from utils.Simulation import get_input, initialize_simulation
from utils.Episode import initialize_online_episode, initialize_offline_episode, finalize_episode
from utils.OnlineRun import run_online_episode
from utils.OfflineRun import run_offline_episode
from agent.Agent import CentralizedAgent
from settings.GeneralSettings import *
from settings.StateSettings import state_dim, state_full_labels, state_normalization, state_mask
import os
import random
import copy
import argparse
import numpy as np

parser = argparse.ArgumentParser()

# Determine whetever to train the learning agent
parser.add_argument('-train', '--train', action='store_const', const=True, default=False)
# Determine whetever to test the learning agent (or another policy)
parser.add_argument('-test', '--test', action='store_const', const=True, default=False)
# Determine whetever to start the simulation or plot the simulation results
parser.add_argument('-run', '--run', action='store_const', const=True, default=False)
# Determine which startegy to use
parser.add_argument('-policy', '--agent_policy', type=str, default='dql')
# Determine the KPI of the scenario (teleoperated or mapscharing)
parser.add_argument('-mode', '--mode', type=str, default='teleoperated')
# Determine whetever to perform a transfer learning phase
parser.add_argument('-transfer', '--transfer', action='store_const', const=True, default=False)
# Determine whetever to repeat the simulation for different values of alpha
parser.add_argument('-multi_alpha', '--multi_alpha', action='store_const', const=True, default=False)

# PARAMETERS OF THE INPUT SCENARIO
# The following parameters are related to the scenario where the agent has been trained
# By default, they are set identical to those of the äctual"scenario"

parser.add_argument('-input_user', '--input_user_num', type=int, default=None)
parser.add_argument('-input_power', '--input_tx_power', type=int, default=None)
parser.add_argument('-input_penalty', '--input_reward_penalty', type=float, default=None)
parser.add_argument('-input_alpha', '--input_reward_alpha', type=float, default=None)
parser.add_argument('-input_episode', '--input_episode_num', type=int, default=None)
parser.add_argument('-input_step', '--input_step_num', type=int, default=None)
parser.add_argument('-input_update', '--input_update', type=str, default=None)
parser.add_argument('-input_delay', '--input_delay', type=str, default=None)
parser.add_argument('-input_offline', '--input_offline', action='store_const', const=True, default=False)

# PARAMETERS OF THE ACTUAL SCENARIO
# The following parameters are related to the scenario where the agent will be trained or tested

parser.add_argument('-user', '--user_num', type=int, default=1) # Number of user
parser.add_argument('-power', '--tx_power', type=int, default=23) # Communication power
parser.add_argument('-penalty', '--reward_penalty', type=float, default=10) # Penalty of the reward function
parser.add_argument('-alpha', '--reward_alpha', type=float, default=1.0) # Weight of the reward function
parser.add_argument('-episode', '--episode_num', type=int, default=None) # Number of episodes
parser.add_argument('-step', '--step_num', type=int, default=800) # Number of steps
parser.add_argument('-update', '--update', type=str, default='real') # Ideal/real action update
parser.add_argument('-delay', '--delay', type=str, default='none') # Additional delay for data encoding
parser.add_argument('-offline', '--offline', action='store_const', const=True, default=False) # Dermine wheter run an offline simulation
parser.add_argument('-format', '--format', type=str, default=None) # Format of the output plots

# Get input parameters

algorithm_training, algorithm_testing, agent_policy, running, offline_folder, transfer, \
    user_num, tx_power, reward_penalty, multi_reward_alpha, episode_num, step_num, ideal_update, additional_delay, offline_running, \
    input_user_num, input_tx_power, input_reward_penalty, input_multi_reward_alpha, input_episode_num, input_step_num, \
    input_ideal_update, input_additional_delay, input_offline_running, plot_format, mode = get_input(vars(parser.parse_args()))

# Determine the KPI of the communication services

if mode == 'teleoperated':
    delay_requirement = teleoperated_delay_requirement
    prr_requirement = teleoperated_prr_requirement
    qos_bonus = 'delay'
elif mode == 'mapsharing':
    delay_requirement = mapsharing_delay_requirement
    prr_requirement = mapsharing_prr_requirement
    qos_bonus = 'prr'
else:
    raise ValueError

for reward_alpha, input_reward_alpha in zip(multi_reward_alpha, input_multi_reward_alpha):

    # Action space
    action_labels = [1450, 1451, 1452] 
    # Action space size
    action_num = len(action_labels)
    # Penalty associated with each of the action
    action_penalties = [cf_mean_per_action[action] for action in action_labels]
    # Maximum Chamfer Distance
    max_chamfer_distance = np.max([cf_mean_per_action[action] for action in action_labels])

    # Initialize learning model

    agent = CentralizedAgent(state_dim=state_dim,
                             action_num=action_num,
                             step_num=step_num,
                             episode_num=episode_num,
                             user_num=user_num,
                             state_labels=state_full_labels,
                             action_labels=action_labels,
                             state_normalization=state_normalization,
                             state_mask=state_mask,
                             gamma=0.95,
                             batch_size=10,
                             target_replace=step_num * 10,
                             memory_capacity=10000,
                             learning_rate=0.00001,
                             eps=0.001,
                             weight_decay=0.0001,
                             format=plot_format)

    # Initialize simulation

    data_folder, sim_duration, default_action_index, max_penalty, simulation_time, temperatures, temp \
        = initialize_simulation(mode,
                                algorithm_training,
                                algorithm_testing,
                                user_num,
                                tx_power,
                                reward_penalty,
                                reward_alpha,
                                episode_num,
                                step_num,
                                ideal_update,
                                additional_delay,
                                offline_running,
                                input_user_num,
                                input_tx_power,
                                input_reward_penalty,
                                input_reward_alpha,
                                input_episode_num,
                                input_step_num,
                                input_ideal_update,
                                input_additional_delay,
                                input_offline_running,
                                agent,
                                transfer,
                                agent_policy,
                                step_duration,
                                action_labels,
                                action_penalties)

    if running:

        # Python-ns3 interface

        if offline_running:

            ns3Settings, experiment = None, None

        else:

            ns3Settings = {'numUes': user_num,
                           'txPower': tx_power,
                           'simDuration': sim_duration,
                           'updatePeriodicity': step_duration,
                           'idealActionUpdate': ideal_update,
                           'additionalDelay': additional_delay}

            experiment = Experiment(mempool_key, mem_size, 'ran-ai', '../../')

        print("Running...")

        if offline_running:

            # Collect the offline data and organize the data into episodes

            data_folders = os.listdir(offline_folder)

            vehicle_folders = []

            if agent_policy == 'dql':
                episode_per_action = int((episode_num + action_num) / action_num)
            else:
                episode_per_action = episode_num

            while episode_per_action > len(vehicle_folders):
                random.shuffle(data_folders)

                vehicle_folders.extend(data_folders)

            vehicle_folders = vehicle_folders[:episode_per_action]

            episode = -1

            # Repeat for each vehicle track

            for vehicle_folder in vehicle_folders:

                if agent_policy == 'dql':

                    shuffle_action_labels = copy.copy(action_labels)
                    random.shuffle(shuffle_action_labels)

                else:

                    shuffle_action_labels = [agent_policy]

                # Repeat for each action associated with the policy

                for action in shuffle_action_labels:

                    # Start a new episode

                    episode += 1

                    if episode < episode_num:

                        episode_data = offline_folder + '/' + vehicle_folder + '/' + str(action) + '/data.pkl'

                        # Initialize the new episode

                        episode_start_time = initialize_offline_episode(episode,
                                                                        episode_num,
                                                                        agent,
                                                                        data_folder)

                        default_action_index = action_labels.index(int(action))

                        # Run the simulation

                        run_offline_episode(user_num, state_dim, max_penalty, reward_alpha,
                                            default_action_index, action_penalties, prr_requirement,
                                            delay_requirement, algorithm_training, agent, episode_data, qos_bonus,
                                            step_num=step_num)

                        # Terminate the episode

                        simulation_time = finalize_episode(episode_start_time, simulation_time, episode, episode_num)

        else:

            # Exploit the ns3-ai interface to perform an online simulation

            try:
                for episode in range(episode_num):
                    
                    # Initialize the new episode

                    temp, episode_start_time, rl, pro = initialize_online_episode(episode,
                                                                                  episode_num,
                                                                                  agent,
                                                                                  data_folder,
                                                                                  algorithm_training,
                                                                                  temperatures,
                                                                                  experiment,
                                                                                  ns3Settings)

                    # Run the simulation

                    run_online_episode(action_num, user_num, state_dim, max_penalty, reward_alpha, temp, agent_policy,
                                       default_action_index, action_labels, action_penalties,
                                       prr_requirement, delay_requirement, algorithm_training, agent, rl, qos_bonus, step_num=step_num)

                    # Terminate the episode

                    simulation_time = finalize_episode(episode_start_time, simulation_time, episode, episode_num)

            finally:
                experiment.kill()
                del experiment
                FreeMemory()

        print("Total episode ", episode_num, "; time duration [min] ", simulation_time / 60)

        # Save the data of the simulation

        agent.save_data(data_folder)
        agent.save_model(data_folder)

    # Plot the data of the simulation

    agent.load_data(data_folder)
    agent.plot_data(data_folder, episode_num)
