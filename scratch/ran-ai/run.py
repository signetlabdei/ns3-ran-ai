from ctypes import *
from py_interface import *
import numpy as np
import time
import os
from Agent.Agent import Agent
from Agent.StateProcessing import state_process, reward_process


# The environment is shared between ns-3
# and python with the same shared memory
# using the ns3-ai model.

class Env(Structure):
    _pack_ = 1
    _fields_ = [
        ('imsiStatsMap', (c_double * 28) * 50)
    ]


env_features = ['imsi',
                'mcs',
                'symbols',
                'sinr',

                'rlc_tx_pkt',
                'rlc_tx_data',
                'rlc_rx_pkt',
                'rlc_rx_data',

                'rlc_delay_mean',
                'rlc_delay_stdev',
                'rlc_delay_min',
                'rlc_delay_max',

                'pdcp_tx_pkt',
                'pdcp_tx_data',
                'pdcp_rx_pkt',
                'pdcp_rx_data',

                'pdcp_delay_mean',
                'pdcp_delay_stdev',
                'pdcp_delay_min',
                'pdcp_delay_max',

                'app_tx_pkt',
                'app_tx_data',
                'app_rx_pkt',
                'app_rx_data',

                'app_delay_mean',
                'app_delay_stdev',
                'app_delay_min',
                'app_delay_max'
                ]

env_normalization = {'imsi': None,
                     'mcs': (0, 28),
                     'symbols': (0, 12),
                     'sinr': (0, 60),

                     'rlc_tx_pkt': (0, 1),
                     'rlc_tx_data': (0, 1),
                     'rlc_rx_pkt': (0, 1),
                     'rlc_rx_data': (0, 1),

                     'rlc_delay_mean': (0, 100000000),
                     'rlc_delay_stdev': (0, 100000000),
                     'rlc_delay_min': (0, 100000000),
                     'rlc_delay_max': (0, 100000000),

                     'pdcp_tx_pkt': (0, 1),
                     'pdcp_tx_data': (0, 1),
                     'pdcp_rx_pkt': (0, 1),
                     'pdcp_rx_data': (0, 1),

                     'pdcp_delay_mean': (0, 100000000),
                     'pdcp_delay_stdev': (0, 100000000),
                     'pdcp_delay_min': (0, 100000000),
                     'pdcp_delay_max': (0, 100000000),

                     'app_tx_pkt': (0, 1),
                     'app_tx_data': (0, 1),
                     'app_rx_pkt': (0, 1),
                     'app_rx_data': (0, 1),

                     'app_delay_mean': (0, 100000000),
                     'app_delay_stdev': (0, 100000000),
                     'app_delay_min': (0, 100000000),
                     'app_delay_max': (0, 100000000)
                     }


# The result is calculated by python
# and put back to ns-3 with the shared memory.

class Act(Structure):
    _pack_ = 1
    _fields_ = [
        ('actions', (c_int16 * 2) * 50)
    ]


user_num = 2
episode_num = 20  # Number of episodes
step_num = 100  # Number of steps per episode
temperatures = np.flip(np.arange(episode_num)) / episode_num  # Temperatures (for the epsilon greedy policy)
step_duration = 100  # Duration of a step [ms]
sim_duration = step_num * step_duration / 1000  # Duration of the simulation [s]

state_labels = ['MCS', 'Symbols', 'SINR', 'Mean delay [ms]', 'Max delay  [ms]', 'PDR']
state_normalization = [(0, 28), (0, 12), (0, 60), (0, 100), (0, 1000), (0, 1)]

state_features = ['mcs',
                  'symbols',
                  'sinr',
                  'pdcp_delay_mean',
                  'pdcp_delay_max']

pdr_features = [('pdcp_rx_data',
                 'pdcp_tx_data')]

state_feature_normalization = [env_normalization[feature] for feature in state_features]

pdr_normalization = [(0, 1), (0, 1)]

state_feature_indexes = []

for feature in state_features:
    state_feature_indexes.append(env_features.index(feature))

pdr_indexes = []

for num, den in pdr_features:
    pdr_indexes.append((env_features.index(num), env_features.index(den)))

action_keys = [1, 2, 1452]
action_num = len(action_keys)

cf_mean_per_action = {1150: 0.002492, 1450: 0.000044, 1451: 5.476881, 1452: 35.634660, 1: 5.476811, 2: 35.634485}
action_indexes = range(action_num)
action_bonus = [cf_mean_per_action[action] for action in action_keys]
last_action_indexes = [0] * user_num

# Python-ns3 interface

ns3Settings = {'numUes': user_num, 'simDuration': sim_duration, 'updatePeriodicity': step_duration}

mempool_key = 1234  # memory pool key, arbitrary integer large than 1000
mem_size = 40960  # memory pool size in bytes
memblock_key = 2333  # memory block key, need to keep the same in the ns-3 script
exp = Experiment(mempool_key, mem_size, 'ran-ai', '../../')  # Set up the ns-3 environment

# Learning agent

state_dim = len(state_features) + len(pdr_features)  # State size

agent = Agent(state_dim=state_dim, action_num=action_num,
              step_num=step_num, episode_num=episode_num, user_num=user_num,
              state_labels=state_labels, action_labels=action_keys,
              state_normalization=state_normalization,
              gamma=0.9, batch_size=16, target_replace=200, memory_capacity=200,
              learning_rate=0.0001, eps=0.0001, weight_decay=0.0001)

data_folder = 'output/test/'  # Output folder
for user_idx in range(user_num):
    user_folder = data_folder + 'user_' + str(user_idx) + '/'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

simulation_time = 0

train = True

if train:

    try:
        for episode in range(episode_num):

            start_time = time.time()

            exp.reset()  # Reset the environment
            agent.reset()  # Reset the agent
            rl = Ns3AIRL(memblock_key, Env, Act)  # Link the shared memory block with ns-3 script

            ns3Settings['firstVehicleIndex'] = np.random.randint(50)

            pro = exp.run(setting=ns3Settings, show_output=True)  # Set and run the ns-3 script (sim.cc)

            states = None
            q_values = None
            action_indexes = None
            step = -1
            temp = temperatures[episode]

            while not rl.isFinish():
                with rl as data:
                    if data is None or step == step_num:
                        break

                    step += 1

                    new_states, state_imsi_list = state_process(data.env.imsiStatsMap,
                                                                state_feature_indexes,
                                                                state_feature_normalization,
                                                                pdr_indexes,
                                                                pdr_normalization,
                                                                state_dim,
                                                                user_num)

                    rewards, reward_imsi_list = reward_process(data.env.imsiStatsMap,
                                                               pdr_indexes,
                                                               last_action_indexes,
                                                               action_bonus,
                                                               user_num)

                    if states is not None:
                        agent.update(action_indexes, q_values, rewards, new_states, temp)

                    states = [np.copy(new_state) for new_state in new_states]

                    action_indexes, q_values = agent.get_action(states, temp)

                    for user_idx, action_idx in enumerate(action_indexes):
                        imsi = data.env.imsiStatsMap[user_idx][0]
                        action = action_keys[action_idx]
                        data.act.actions[user_idx][0] = int(imsi)
                        data.act.actions[user_idx][1] = action
                        last_action_indexes[user_idx] = action_idx

            pro.wait()  # Wait the ns-3 to stop

            end_time = time.time()

            episode_time = end_time - start_time

            print("Episode ", episode, "; time duration ", episode_time)

            simulation_time += episode_time

    finally:
        exp.kill()
        del exp
        FreeMemory()

    print("Total episode ", episode_num, "; time duration ", simulation_time)

    agent.save_data(data_folder)

agent.load_data(data_folder)
agent.plot_data(data_folder, episode_num)
