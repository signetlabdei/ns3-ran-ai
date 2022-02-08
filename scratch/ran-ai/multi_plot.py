from agent.Agent import CentralizedAgent
from plot.Boxplot import multi_boxplot
from plot.Violinplot import multi_violinplot
from plot.Histplot import multi_histplot
from settings.StateSettings import state_mask, state_dim, state_full_labels, state_labels, state_normalization
from settings.GeneralSettings import *
import numpy as np
import seaborn as sns
import os
import argparse

parser = argparse.ArgumentParser()

# Determine wheter to compare the outcomes of different simulation while varying alpha
parser.add_argument('-multi_alpha', '--multi_alpha', action='store_const', const=True, default=False)
# Determine wheter to compare the outcomes of different simulation while varying the number of users
parser.add_argument('-multi_user', '--multi_user', action='store_const', const=True, default=False)

# Parameters of the scenario analyzed
parser.add_argument('-user', '--user_num', type=int, default=1)
parser.add_argument('-policy', '--policy', type=str, default='dql')
parser.add_argument('-penalty', '--reward_penalty', type=float, default=10)
parser.add_argument('-episode', '--episode_num', type=int, default=100)
parser.add_argument('-step', '--step_num', type=int, default=800)
parser.add_argument('-power', '--power', type=int, default=23)
parser.add_argument('-alpha', '--alpha', type=float, default=1.0)
parser.add_argument('-update', '--update', type=str, default='real')
parser.add_argument('-format', '--format', type=str, default='png')
args = vars(parser.parse_args())

plot_points: int = 100
step_num: int = args['step_num']
episode_num: int = args['episode_num']
reward_penalty: float = args['reward_penalty']
state_dim: int = state_dim
plot_format: str = args['format']
action_labels: [str] = [1450, 1451, 1452]
action_num: int = len(action_labels)
state_normalization: [[]] = state_normalization

palette = sns.color_palette('rocket')

state_palette = sns.color_palette('rocket', 2)
reward_palette = sns.color_palette('rocket', 2)
qoe_palette = sns.color_palette('rocket', 3)
cd_palette = sns.color_palette('rocket_r', 3)
qos_palette = sns.color_palette('rocket', 2)

plot_state = True
plot_perf = True

test_folders: [str] = []
user_per_test: [int] = []
label_per_test: [str] = []
legend_per_test: [str] = []

label_key = None
legend_key = None

if args['multi_user'] and args['multi_alpha']:

    label_key = '$N_{u}$'
    legend_key = '$\\alpha$'

    policy = args['policy']

    users: [int] = [1, 5]
    labels: [str] = ['1', '5']
    alphas: [float] = [0.5, 1.0]
    legends: [str] = ['0.5', '1.0']

    scenario_name = args['update'] + '_update/'

    for label, user_num in zip(labels, users):

        for legend, alpha in zip(legends, alphas):
            policy_folder = 'output/test/' + scenario_name + 'user=' + str(user_num) + '/power='\
                            + str(args['power']) + '/penalty=' + str(reward_penalty) + '/alpha='\
                            + str(alpha) + '/episode=' + str(episode_num) + '/step='\
                            + str(step_num) + '/' + policy + '/'

            test_folders.append(policy_folder)
            user_per_test.append(user_num)
            label_per_test.append(label)
            legend_per_test.append(legend)

    output_folder = 'output/multi_test/' + scenario_name + 'multi_user/power=' + str(args['power'])\
                    + '/penalty=' + str(reward_penalty) + '/multi_alpha' + '/episode=' + str(episode_num)\
                    + '/step=' + str(step_num) + '/policy=' + args['policy'] + '/'

elif args['multi_alpha']:

    label_key = 'Policy'
    legend_key = '$\\alpha$'

    user_num: int = args['user_num']

    policies: [str] = ['0', '1450', '1451', '1452', 'dql']
    labels: [str] = ['0', '1450', '1451', '1452', 'DQL']
    alphas: [float] = [0.5, 1.0]
    legends: [str] = ['0.5', '1.0']

    scenario_name = args['update'] + '_update/user=' + str(user_num) + '/power=' + str(args['power']) + \
                    '/penalty=' + str(reward_penalty)

    output_folder = 'output/multi_test/' + scenario_name + '/multi_alpha' + '/episode=' \
                    + str(episode_num) + '/step=' + str(step_num) + '/multi_policy/'

    for label, policy in zip(labels, policies):
        for legend, alpha in zip(legends, alphas):
            policy_folder = 'output/test/' + scenario_name + '/alpha=' + str(alpha) + '/episode=' \
                        + str(episode_num) + '/step=' + str(step_num) + '/' + policy + '/'
            test_folders.append(policy_folder)
            user_per_test.append(user_num)
            label_per_test.append(label)
            legend_per_test.append(legend)

elif args['multi_user']:

    label_key = 'Policy'
    legend_key = '$N_{u}$'

    alpha = args['alpha']

    policies: [str] = ['0', '1450', '1451', '1452', 'dql']
    labels: [str] = ['0', '1450', '1451', '1452', 'DQL']

    users: [int] = [1, 5]
    legends: [str] = ['1', '5']

    scenario_name = args['update'] + '_update/'

    for label, policy in zip(labels, policies):
        for legend, user_num in zip(legends, users):
            policy_folder = 'output/test/' + scenario_name + 'user=' + str(user_num) + '/power=' \
                            + str(args['power']) + '/penalty=' + str(reward_penalty) + '/alpha=' \
                            + str(alpha) + '/episode=' + str(episode_num) + '/step=' \
                            + str(step_num) + '/' + policy + '/'

            test_folders.append(policy_folder)
            user_per_test.append(user_num)
            label_per_test.append(label)
            legend_per_test.append(legend)

    output_folder = 'output/multi_test/' + scenario_name + 'multi_user/power=' + str(args['power']) \
                    + '/penalty=' + str(reward_penalty) + '/alpha=' + str(alpha) + '/episode=' + str(episode_num) \
                    + '/step=' + str(step_num) + '/multi_policy/'

elif args['multi_policy']:

    label_key = 'Policy'

    user_num: int = args['user_num']

    policies: [str] = ['0', '1450', '1451', '1452', 'dql']
    labels: [str] = ['0', '1450', '1451', '1452', 'DQL']

    scenario_name = args['update'] + '_update/user=' + str(user_num) + '/power=' + str(args['power']) + \
                    '/penalty=' + str(reward_penalty)

    output_folder = 'output/multi_test/' + scenario_name + '/alpha='\
                    + str(args['alpha']) + '/episode=' + str(episode_num) + '/step=' + str(step_num) + '/multi_policy/' 
                    
    for label, policy in zip(labels, policies):
        policy_folder = 'output/test/' + scenario_name + policy + '/'
        test_folders.append(policy_folder)
        user_per_test.append(user_num)
        label_per_test.append(label)
        legend_per_test.append(None)

else:
    raise ValueError

for data_type in ['state', 'performance']:
    if not os.path.exists(output_folder + data_type + '/'):
        os.makedirs(output_folder + data_type + '/')

test_num = len(test_folders)
agents = []
max_penalty = reward_penalty + np.max([cf_mean_per_action[action] for action in action_labels])

for i, user_num in enumerate(user_per_test):
    agent = CentralizedAgent(step_num,
                             episode_num,
                             state_dim,
                             action_num,
                             user_num,
                             state_full_labels,
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

    agent.load_data(test_folders[i])

    agent.max_penalty = max_penalty

    agents.append(agent)

# States

if plot_state:

    for i in range(state_dim):

        multi_data = []
        multi_labels = []
        multi_legends = []
        state_key = state_labels[i]
        state_full_label = state_full_labels[i]
        min_value, max_value = state_normalization[i]

        data_idx = agents[0].data_idx

        for j in range(test_num):
            agent = agents[j]
            label = label_per_test[j]
            legend = legend_per_test[j]

            state_data = np.mean(agent.state_data, axis=0) * (max_value - min_value) + min_value

            multi_data.append(state_data[i, :data_idx])

            multi_labels.append(label)
            multi_legends.append(legend)

        multi_data = np.stack(multi_data)

        multi_boxplot(multi_data,
                      multi_labels,
                      multi_legends,
                      state_key,
                      label_key,
                      legend_key,
                      output_folder + 'state/' + state_full_label.replace(' ', '_') + '_box',
                      plot_format=plot_format,
                      palette=state_palette)

        multi_violinplot(multi_data,
                         multi_labels,
                         multi_legends,
                         state_key,
                         label_key,
                         legend_key,
                         output_folder + 'state/' + state_full_label.replace(' ', '_') + '_violin',
                         plot_format=plot_format,
                         palette=state_palette)

# Reward

if plot_perf:

    multi_data = []
    multi_labels = []
    multi_legends = []

    data_idx = agents[0].data_idx

    for j in range(test_num):
        agent = agents[j]
        label = label_per_test[j]
        legend = legend_per_test[j]

        reward_data = agent.reward_data.flatten()

        multi_data.append(reward_data[:data_idx])
        multi_labels.append(label)
        multi_legends.append(legend)

    multi_boxplot(multi_data,
                  multi_labels,
                  multi_legends,
                  'Reward',
                  label_key,
                  legend_key,
                  output_folder + 'performance/reward_box',
                  plot_format=plot_format,
                  palette=reward_palette)

    multi_violinplot(multi_data,
                     multi_labels,
                     multi_legends,
                     'Reward',
                     label_key,
                     legend_key,
                     output_folder + 'performance/reward_violin',
                     plot_format=plot_format,
                     palette=reward_palette)

# QoS

    multi_data = []
    multi_labels = []
    multi_legends = []

    data_idx = agents[0].data_idx

    for j in range(test_num):
        agent = agents[j]
        label = label_per_test[j]
        legend = legend_per_test[j]

        qos_data = agent.qos_data.flatten()

        multi_data.append(qos_data[:data_idx])
        multi_labels.append(label)
        multi_legends.append(legend)

    multi_violinplot(multi_data,
                     multi_labels,
                     multi_legends,
                     'Quality of Service',
                     label_key,
                     legend_key,
                     output_folder + 'performance/qos_violin',
                     plot_format=plot_format,
                     palette=qos_palette)

    multi_histplot(multi_data,
                   multi_labels,
                   multi_legends,
                   'Quality of Service',
                   label_key,
                   legend_key,
                   output_folder + 'performance/qos_hist',
                   plot_format=plot_format,
                   palette=qos_palette)

# Chamfer Distance

    multi_data = []
    multi_labels = []
    multi_legends = []

    data_idx = agents[0].data_idx

    for j in range(test_num):
        agent = agents[j]
        label = label_per_test[j]
        legend = legend_per_test[j]

        chamfer_data = agent.chamfer_data.flatten()

        multi_data.append(chamfer_data[:data_idx])
        multi_labels.append(label)
        multi_legends.append(legend)

    multi_violinplot(multi_data,
                     multi_labels,
                     multi_legends,
                     'Chamfer Distance',
                     label_key,
                     legend_key,
                     output_folder + 'performance/chamfer_violin',
                     plot_format=plot_format,
                     palette=cd_palette)

    multi_histplot(multi_data,
                   multi_labels,
                   multi_legends,
                   'Chamfer Distance',
                   label_key,
                   legend_key,
                   output_folder + 'performance/chamfer_hist',
                   plot_format=plot_format,
                   palette=cd_palette)

    # QoE

    multi_data = []
    multi_labels = []
    multi_legends = []

    data_idx = agents[0].data_idx

    for j in range(test_num):
        agent = agents[j]
        label = label_per_test[j]
        legend = legend_per_test[j]

        qoe_data = (max_penalty - agent.chamfer_data.flatten()) / max_penalty

        multi_data.append(qoe_data[:data_idx])
        multi_labels.append(label)
        multi_legends.append(legend)

    multi_violinplot(multi_data,
                     multi_labels,
                     multi_legends,
                     'QoE',
                     label_key,
                     legend_key,
                     output_folder + 'performance/qoe_violin',
                     plot_format=plot_format,
                     palette=qoe_palette)

    multi_histplot(multi_data,
                   multi_labels,
                   multi_legends,
                   'QoE',
                   label_key,
                   legend_key,
                   output_folder + 'performance/qoe_hist',
                   plot_format=plot_format,
                   palette=qoe_palette)
