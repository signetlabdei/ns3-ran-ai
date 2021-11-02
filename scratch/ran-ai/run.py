from py_interface import *
from settings import *
import numpy as np
import time
import os
from Agent.Agent import CentralizedAgent
from Agent.StateProcessing import state_process
from Agent.RewardProcessing import reward_process
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-train', '--train', action='store_const', const=True, default=False)
parser.add_argument('-test', '--test', action='store_const', const=True, default=False)
parser.add_argument('-run', '--run', action='store_const', const=True, default=False)
parser.add_argument('-policy', '--agent_policy', type=str, default='dql')

parser.add_argument('-input_user', '--input_user_num', type=int, default=None)

parser.add_argument('-input_penalty', '--input_reward_penalty', type=float, default=None)
parser.add_argument('-input_episode', '--input_episode_num', type=int, default=None)
parser.add_argument('-input_step', '--input_step_num', type=int, default=None)
parser.add_argument('-input_update', '--input_update', type=float, default=None)

parser.add_argument('-user', '--user_num', type=int, default=1)
parser.add_argument('-penalty', '--reward_penalty', type=float, default=0)
parser.add_argument('-episode', '--episode_num', type=int, default=1000)
parser.add_argument('-step', '--step_num', type=int, default=500)
parser.add_argument('-update', '--update', type=str, default='real')

args = vars(parser.parse_args())

algorithm_training = args['train']
algorithm_testing = args['test']
agent_policy = args['agent_policy']
if algorithm_training:
    assert agent_policy == 'dql'

user_num = args['user_num']  # Number of users
reward_penalty = args['reward_penalty']  # Reward penalty when QoS is violated
episode_num = args['episode_num']  # Number of episodes
step_num = args['step_num']  # Number of steps per episode
# Determine if the agent actions are updated through a ideal update
if args['update'] == 'ideal':
    ideal_update = True
elif args['update'] == 'real':
    ideal_update = False
else:
    raise ValueError

if args['input_user_num'] is None:
    input_user_num = user_num
else:
    input_user_num = args['input_user_num']
if args['input_reward_penalty'] is None:
    input_reward_penalty = reward_penalty
else:
    input_reward_penalty = args['input_reward_penalty']
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
    elif args['update'] == 'real':
        input_ideal_update = False
    else:
        raise ValueError

st = 0.95
a = int(episode_num / 10)
b = episode_num + a

temperatures = (np.flip(np.arange(a, b))) / (b + b * (1 - st ** 2) / (st ** 2))
temperatures[:int(episode_num / 3)] **= 0.5
temperatures[int(episode_num / 3):int(2 * episode_num / 3)] **= 0.75
temperatures[int(2 * episode_num / 3):] **= 1

step_duration = 100  # Duration of a step [ms]
sim_duration = step_num * step_duration / 1000  # Duration of the simulation [s]

action_keys = [1150, 2, 1450, 1452]

default_action_index = None

if agent_policy != 'dql':

    if agent_policy != 'random':
        default_action_index = action_keys.index(int(agent_policy))

action_num = len(action_keys)

action_indexes = range(action_num)
action_penalties = [cf_mean_per_action[action] for action in action_keys]
last_action_indexes = [0] * user_num

max_penalty = reward_penalty + np.max(action_penalties)

if user_num > 1:
    delay_requirement = mapsharing_delay_requirement
else:
    delay_requirement = teleoperated_delay_requirement

# Learning agent

agent = CentralizedAgent(state_dim=state_dim, action_num=action_num,
                         step_num=step_num, episode_num=episode_num, user_num=user_num,
                         state_labels=state_labels, action_labels=action_keys,
                         state_normalization=state_normalization, state_mask=state_mask,
                         gamma=0.95, batch_size=10, target_replace=step_num * 10, memory_capacity=10000,
                         learning_rate=0.00001, eps=0.001, weight_decay=0.0001)

if ideal_update:
    scenario_name = 'ideal_update/'
else:
    scenario_name = 'real_update/'

scenario_name += str(user_num) + '_user' + '/penalty=' + str(reward_penalty) + '/' + str(
    episode_num) + '_episode/' + str(step_num) + '_step/'

if algorithm_training:

    print("TRAINING")

    data_folder = 'output/train/' + scenario_name  # Output folder

elif algorithm_testing:

    print("TESTING")

    data_folder = 'output/test/' + agent_policy + '/' + scenario_name  # Output folder

    if agent_policy == 'dql':

        if input_ideal_update:
            input_scenario_name = 'ideal_update/'
        else:
            input_scenario_name = 'real_update/'

        input_scenario_name += str(input_user_num) + '_user' + '/penalty=' + str(input_reward_penalty) + '/' + str(
            input_episode_num) + '_episode/' + str(input_step_num) + '_step/'

        input_folder = 'output/train/' + input_scenario_name  # Input folder
        agent.load_model(input_folder)  # Load the learning architecture

else:

    raise ValueError

for user_idx in range(user_num):
    user_folder = data_folder + str(user_idx) + '/'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

simulation_time = 0

if args['run']:

    # Python-ns3 interface

    ns3Settings = {'numUes': user_num, 'simDuration': sim_duration, 'updatePeriodicity': step_duration,
                   'idealActionUpdate': ideal_update}

    mempool_key = 1234  # memory pool key, arbitrary integer large than 1000
    mem_size = 40960  # memory pool size in bytes
    memblock_key = 2333  # memory block key, need to keep the same in the ns-3 script
    exp = Experiment(mempool_key, mem_size, 'ran-ai', '../../')  # Set up the ns-3 environment

    print("Running...")

    try:
        for episode in range(episode_num):

            if episode > 0 and episode % int(episode_num / 10) == 0:
                agent.save_data(data_folder)
                agent.save_model(data_folder)
                agent.plot_data(data_folder, episode_num)

            episode_start_time = time.time()

            exp.reset()  # Reset the environment
            agent.reset()  # Reset the agent
            rl = Ns3AIRL(memblock_key, Env, Act)  # Link the shared memory block with ns-3 script

            ns3Settings['firstVehicleIndex'] = np.random.randint(1, 50)

            pro = exp.run(setting=ns3Settings, show_output=True)  # Set and run the ns-3 script (sim.cc)

            states = None
            q_values = None
            action_indexes = None
            step = -1

            if algorithm_training:
                temp = temperatures[episode]
            else:
                temp = 0

            while not rl.isFinish():
                with rl as data:
                    if data is None or step == step_num:
                        break

                    step += 1

                    new_states, state_imsi_list = state_process(data.env.imsiStatsMap,
                                                                state_feature_indexes,
                                                                state_feature_normalization,
                                                                combination_feature_indexes,
                                                                combination_feature_normalization,
                                                                state_dim,
                                                                user_num)

                    rewards, qos_per_user, qoe_per_user, reward_imsi_list = reward_process(data.env.imsiStatsMap,
                                                                                           app_pdr_indexes,
                                                                                           app_delay_mean_index,
                                                                                           delay_requirement,
                                                                                           last_action_indexes,
                                                                                           action_penalties,
                                                                                           user_num,
                                                                                           max_penalty)

                    if states is not None:
                        agent.update(action_indexes,
                                     q_values,
                                     rewards,
                                     new_states,
                                     qos_per_user,
                                     qoe_per_user,
                                     temp,
                                     algorithm_training)

                    states = [np.copy(new_state) for new_state in new_states]

                    action_indexes, q_values = agent.get_action(states, temp)

                    if agent_policy != 'dql':

                        if default_action_index is not None:

                            action_indexes = [default_action_index] * user_num

                        else:

                            action_indexes = list(np.random.randint(0, action_num, user_num))

                    for user_idx, action_idx in enumerate(action_indexes):
                        imsi = data.env.imsiStatsMap[user_idx][0]
                        action = action_keys[action_idx]
                        data.act.actions[user_idx][0] = int(imsi)
                        data.act.actions[user_idx][1] = action
                        last_action_indexes[user_idx] = action_idx

            episode_end_time = time.time()

            useful_time = episode_end_time - episode_start_time

            pro.wait()  # Wait the ns-3 to stop

            episode_end_time = time.time()

            total_time = episode_end_time - episode_start_time

            print("Episode ", episode, "; time duration ", useful_time, "; total time ", total_time)

            simulation_time += total_time

    finally:
        exp.kill()
        del exp
        FreeMemory()

    print("Total episode ", episode_num, "; time duration ", simulation_time)

    agent.save_data(data_folder)
    agent.save_model(data_folder)

agent.load_data(data_folder)
agent.plot_data(data_folder, episode_num)
