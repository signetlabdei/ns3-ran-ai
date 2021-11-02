from Agent.Agent import CentralizedAgent
from Agent.Linearplot import multi_linear_plot
from Agent.Boxplot import multi_boxplot
from Agent.Violinplot import multi_violinplot
from Agent.Histplot import multi_histplot
from Agent.Densityplot import multi_density_plot
from settings import *
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-user', '--user_num', type=int, default=1)
parser.add_argument('-penalty', '--reward_penalty', type=float, default=0)
parser.add_argument('-episode', '--episode_num', type=int, default=500)
parser.add_argument('-step', '--step_num', type=int, default=500)
parser.add_argument('-update', '--update', type=str, default='real')
args = vars(parser.parse_args())

plot_points: int = 100
step_num: int = args['step_num']
episode_num: int = args['episode_num']
reward_penalty: float = args['reward_penalty']
state_dim: int = state_dim
user_num: int = args['user_num']
state_labels: [str] = state_labels
action_labels: [str] = [1150, 2, 1450, 1452]
action_num: int = len(action_labels)
state_normalization: [[]] = state_normalization
update_folder = args['update'] + '_update/'

plot_state = True
plot_reward = False
plot_qoe = False
plot_qos = False

policies: [str] = ['random', '1150', '1450', '2', '1452', 'dql']
policy_labels: [str] = ['Random', '1150', '1450', '2', '1452', 'DQL']

data_folders: [str] = []

scenario_name = update_folder + str(user_num) + '_user/' + \
                'penalty=' + str(reward_penalty) + '/' \
                + str(episode_num) + '_episode/' \
                + str(step_num) + '_step/'

output_folder = 'output/multi_test/' + scenario_name  # Output folder

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for policy in policies:
    policy_folder = 'output/test/' + policy + '/' + scenario_name
    data_folders.append(policy_folder)

policy_num = len(data_folders)
agents = []

for i in range(policy_num):
    agent = CentralizedAgent(step_num,
                             episode_num,
                             state_dim,
                             action_num,
                             user_num,
                             state_labels,
                             action_labels,
                             state_normalization,
                             state_mask=state_mask,
                             gamma=1,
                             batch_size=1,
                             target_replace=1,
                             memory_capacity=1,
                             learning_rate=1,
                             eps=1,
                             weight_decay=1)

    agent.load_data(data_folders[i])

    agents.append(agent)

# States

if plot_state:

    for i in range(state_dim):

        multi_data = []
        multi_keys = []
        state_label = state_labels[i]
        min_value, max_value = state_normalization[i]

        for j in range(policy_num):
            agent = agents[j]
            policy_label = policy_labels[j]

            state_data = np.mean(agent.state_data, axis=0) * (max_value - min_value) + min_value
            data_idx = agent.data_idx

            multi_data.append(state_data[i, :data_idx])
            multi_keys.append(policy_label)

        multi_boxplot(multi_data,
                      multi_keys,
                      state_label,
                      output_folder + state_label + ' box')

        multi_violinplot(multi_data,
                         multi_keys,
                         state_label,
                         output_folder + state_label + ' violin')

        multi_density_plot(multi_data, multi_keys, state_label, output_folder + state_label + ' density')

# Reward

if plot_reward:

    multi_data = []
    multi_keys = []

    for j in range(policy_num):
        agent = agents[j]
        policy_label = policy_labels[j]

        reward_data = np.mean(agent.reward_data, axis=0)
        data_idx = agent.data_idx

        multi_data.append(reward_data[:data_idx])
        multi_keys.append(policy_label)

    multi_boxplot(multi_data,
                  multi_keys,
                  'Reward',
                  output_folder + 'reward box')

    multi_violinplot(multi_data,
                     multi_keys,
                     'Reward',
                     output_folder + 'reward violin')

    multi_density_plot(multi_data, multi_keys, 'Reward', output_folder + 'reward density')

# QoS

if plot_qos:

    multi_data = []
    multi_keys = []

    for j in range(policy_num):
        agent = agents[j]
        policy_label = policy_labels[j]

        qos_data = np.mean(agent.qos_data, axis=0)
        data_idx = agent.data_idx

        multi_data.append(qos_data[:data_idx])
        multi_keys.append(policy_label)

    multi_boxplot(multi_data,
                  multi_keys,
                  'QoS',
                  output_folder + 'qos box')

    multi_violinplot(multi_data,
                     multi_keys,
                     'QoS',
                     output_folder + 'qos violin')

    multi_histplot(multi_data,
                     multi_keys,
                     'QoS',
                     output_folder + 'qos hist')

    multi_density_plot(multi_data, multi_keys, 'QoS', output_folder + 'qos density')

# QoE

if plot_qoe:

    multi_data = []
    multi_keys = []

    for j in range(policy_num):
        agent = agents[j]
        policy_label = policy_labels[j]

        qoe_data = np.mean(agent.qoe_data, axis=0)
        data_idx = agent.data_idx

        multi_data.append(qoe_data[:data_idx])
        multi_keys.append(policy_label)

    multi_boxplot(multi_data,
                  multi_keys,
                  'Chamfer Distance',
                  output_folder + 'qoe box')

    multi_violinplot(multi_data,
                     multi_keys,
                     'Chamfer Distance',
                     output_folder + 'qoe violin')

    multi_histplot(multi_data,
                   multi_keys,
                   'Chamfer Distance',
                   output_folder + 'qoe hist')

    multi_density_plot(multi_data, multi_keys, 'Chamfer Distance', output_folder + 'qoe density')
