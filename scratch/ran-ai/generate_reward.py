from settings import *
import numpy as np
import os
from Agent.RewardProcessing import get_reward_per_action
import argparse
from distutils.dir_util import copy_tree

parser = argparse.ArgumentParser()
parser.add_argument('-policy', '--agent_policy', type=str, default='dql')
parser.add_argument('-user', '--user_num', type=int, default=1)
parser.add_argument('-penalty', '--reward_penalty', type=float, default=0)
parser.add_argument('-input_penalty', '--input_reward_penalty', type=float, default=0)
parser.add_argument('-episode', '--episode_num', type=int, default=1000)
parser.add_argument('-step', '--step_num', type=int, default=500)
parser.add_argument('-update', '--update', type=str, default='real')

args = vars(parser.parse_args())

agent_policy = args['agent_policy']

assert agent_policy != 'dql'

user_num = args['user_num']  # Number of users
reward_penalty = args['reward_penalty']  # Reward penalty when QoS is violated
input_reward_penalty = args['input_reward_penalty']  # Input reward penalty when QoS is violated
episode_num = args['episode_num']  # Number of episodes
step_num = args['step_num']  # Number of steps per episode
# Determine if the agent actions are updated through a ideal update
if args['update'] == 'ideal':
    ideal_update = True
elif args['update'] == 'real':
    ideal_update = False
else:
    raise ValueError

step_duration = 100  # Duration of a step [ms]
sim_duration = step_num * step_duration / 1000  # Duration of the simulation [s]

action_keys = [1150, 2, 1450, 1452]

action_num = len(action_keys)

action_indexes = range(action_num)
action_chamfer_distances = [cf_mean_per_action[action] for action in action_keys]
last_action_indexes = [0] * user_num

max_penalty = reward_penalty + np.max(action_chamfer_distances)

if ideal_update:
    scenario_name = 'ideal_update/'
    input_scenario_name = 'real_update/'
else:
    scenario_name = 'real_update/'
    input_scenario_name = 'real_update/'

scenario_name += str(user_num) + '_user' + '/penalty=' + str(reward_penalty) + '/' + str(
    episode_num) + '_episode/' + str(step_num) + '_step/'

input_scenario_name += str(user_num) + '_user' + '/penalty=' + str(input_reward_penalty) + '/' + str(
    episode_num) + '_episode/' + str(step_num) + '_step/'

data_folder = 'output/test/' + agent_policy + '/' + scenario_name  # Output folder

input_data_folder = 'output/test/' + agent_policy + '/' + input_scenario_name  # Output folder

copy_tree(input_data_folder, data_folder)

for user_idx in range(user_num):
    user_folder = data_folder + str(user_idx) + '/'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

action_rewards = get_reward_per_action(action_chamfer_distances, reward_penalty)

if agent_policy != 'random':
    default_chamfer_distance = action_chamfer_distances[action_keys.index(int(agent_policy))]
    default_reward = action_rewards[action_keys.index(int(agent_policy))]
else:
    default_chamfer_distance = np.mean(action_chamfer_distances)
    default_reward = np.mean(action_rewards)

qos = np.load(data_folder + 'qos.npy')

reward_data = np.zeros((user_num, len(qos[0])), dtype=np.float32)

print("Action: ", action_keys)
print("Chamfer distance per action: ", action_chamfer_distances)
print("reward per action: ", action_rewards)

print("Policy: ", agent_policy)
print("Policy reward: ", default_reward)

print(data_folder)

for user_idx in range(user_num):

    reward_data[user_idx] = qos[user_idx] * default_reward + (1-qos[user_idx]) * -1

np.save(data_folder + 'rewards.npy', reward_data)


