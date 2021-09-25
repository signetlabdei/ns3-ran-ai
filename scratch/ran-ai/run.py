from ctypes import *
from py_interface import *
import numpy as np
import time
import os
from Agent.Agent import Agent
from Agent.StateProcessing import state_process


# The environment is shared between ns-3
# and python with the same shared memory
# using the ns3-ai model.

class Env(Structure):
    _pack_ = 1
    _fields_ = [
        ('mcs', c_double),
        ('symbols', c_double),
        ('sinr', c_double),
        ('rlcTxPackets', c_int16),
        ('rlcTxData', c_int32),
        ('rlcRxPackets', c_int16),
        ('rlcRxData', c_int32),
        ('rlcDelayMean', c_double),
        ('rlcDelayStdev', c_double),
        ('rlcDelayMin', c_double),
        ('rlcDelayMax', c_double),
        ('pdcpTxPackets', c_int16),
        ('pdcpTxData', c_int32),
        ('pdcpRxPackets', c_int16),
        ('pdcpRxData', c_int32),
        ('pdcpDelayMean', c_double),
        ('pdcpDelayStdev', c_double),
        ('pdcpDelayMin', c_double),
        ('pdcpDelayMax', c_double),
        ('appTxBursts', c_int16),
        ('appTxData', c_int32),
        ('appRxBursts', c_int16),
        ('appRxData', c_int32),
        ('appDelayMean', c_double),
        ('appDelayStdev', c_double),
        ('appDelayMin', c_double),
        ('appDelayMax', c_double)
    ]


env_normalization = {'mcs': (0, 28),
                     'symbols': (0, 12),
                     'sinr': (0, 50),
                     'rlcTxPackets': (0, 1),
                     'rlcTxData': (0, 1),
                     'rlcRxPackets': (0, 1),
                     'rlcRxData': (0, 1),
                     'pdcpTxPackets': (0, 1),
                     'pdcpTxData': (0, 1),
                     'pdcpRxPackets': (0, 1),
                     'pdcpRxData': (0, 1),
                     'pdcpDelayMean': (0, 0.1),
                     'pdcpDelayStdev': (0, 0.1),
                     'pdcpDelayMin': (0, 0.1),
                     'pdcpDelayMax': (0, 0.1),
                     'rlcDelayMean': (0, 0.1),
                     'rlcDelayStdev': (0, 0.1),
                     'rlcDelayMin': (0, 0.1),
                     'rlcDelayMax': (0, 0.1),
                     'pdcpRatio': (0, 1),
                     'rlcRatio': (0, 1)}


# The result is calculated by python
# and put back to ns-3 with the shared memory.

class Act(Structure):
    _pack_ = 1
    _fields_ = [
        ('action', c_int)
    ]


episode_num = 1000  # Number of episodes
step_num = 100  # Number of steps per episode
temperatures = np.flip(np.arange(episode_num)) / episode_num  # Temperatures (for the epsilon greedy policy)
step_duration = 100  # Duration of a step [ms]
sim_duration = step_num * step_duration / 1000  # Duration of the simulation [s]
state_features = ['mcs', 'symbols', 'sinr', 'rlcRatio', 'pdcpRatio', 'pdcpDelayMean', 'pdcpDelayMax', 'rlcDelayMean', 'rlcDelayMax']
state_normalization = [env_normalization[feature] for feature in state_features]
# actions = [0, 1, 2, 1450, 1451, 1452]
actions = [1, 2, 1452]

# Python-ns3 interface

ns3Settings = {'numUes': 1, 'simDuration': sim_duration, 'updatePeriodicity': step_duration}

mempool_key = 1234  # memory pool key, arbitrary integer large than 1000
mem_size = 4096  # memory pool size in bytes
memblock_key = 2333  # memory block key, need to keep the same in the ns-3 script
exp = Experiment(mempool_key, mem_size, 'ran-ai', '../../')  # Set up the ns-3 environment

# Learning agent

state_dim = len(state_features)  # State size
action_num = len(actions)  # Number of actions

agent = Agent(state_dim=state_dim, action_num=action_num,
              step_num=step_num, episode_num=episode_num,
              state_labels=state_features, action_labels=actions,
              state_normalization=state_normalization,
              gamma=0.9, batch_size=16, target_replace=200, memory_capacity=200,
              learning_rate=0.0001, eps=0.0001, weight_decay=0.0001)

data_folder = 'output/test/'  # Output folder
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

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

            state = None
            q_values = None
            action_idx = None
            step = -1
            temp = temperatures[episode]

            while not rl.isFinish():
                with rl as data:
                    if data is None or step == step_num:
                        break

                    step += 1

                    new_state, reward = state_process(data.env, env_normalization, state_features, state_dim)

                    if state is not None:
                        agent.update(action_idx, q_values, reward, new_state, temp)

                    state = np.copy(new_state)
                    action_idx, q_values = agent.get_action(state, temp)

                    action = actions[action_idx]
                    data.act.action = action

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

    # Plot the output data

    agent.save_data(data_folder)

agent.load_data(data_folder)
agent.plot_data(data_folder, episode_num)
