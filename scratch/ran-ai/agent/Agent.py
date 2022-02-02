import torch
import copy
import numpy as np
from torch.nn import Module
from agent.DoubleQLearning import DQL
from agent.NeuralNetwork import LinearNeuralNetwork
from plot.Linearplot import linear_plot, multi_linear_plot
import seaborn as sns


class CentralizedAgent(object):
    """
    class Agent
    It implements a learning Agent that has to manage a certain environment
    in order to maximize the expected discounted return
    """

    def __init__(self,
                 step_num: int,
                 episode_num: int,
                 state_dim: int,
                 action_num: int,
                 user_num: int,
                 state_labels: [str],
                 action_labels: [str],
                 state_normalization: [[]],
                 state_mask: np.ndarray,
                 gamma: float,
                 batch_size: int,
                 target_replace: int,
                 memory_capacity: int,
                 learning_rate: float,
                 eps: float,
                 weight_decay: float,
                 format=None):

        # Number of steps and episodes

        self.format = format
        self.step_num, self.episode_num = step_num, episode_num

        # State dimension

        self.state_dim: int = state_dim
        self.learning_state_dim: int = np.sum(state_mask)
        self.state_mask: np.ndarray = state_mask

        # Number of possible actions in each state

        self.action_num: int = action_num

        # Number of users controlled by the learner

        self.user_num: int = user_num

        # State and action labels

        self.state_labels = state_labels
        self.action_labels = action_labels
        self.state_normalization = state_normalization
        self.max_penalty = None

        # Primary and target networks used in the training
        # The primary network is used to choose new actions
        # The target network is used to predict the future q values

        self.primary_net: Module = LinearNeuralNetwork(self.learning_state_dim, self.action_num)
        target_net: Module = LinearNeuralNetwork(self.learning_state_dim, self.action_num)
        target_net.load_state_dict(self.primary_net.state_dict())

        # Learning weights optimizer

        optimizer = torch.optim.Adam(self.primary_net.parameters(),
                                     lr=learning_rate, eps=eps, weight_decay=weight_decay)

        # Double Q Learning Algorithm

        self.dql = DQL(self.primary_net,
                       target_net,
                       optimizer,
                       self.action_num,
                       gamma,
                       batch_size,
                       target_replace,
                       memory_capacity)

        # Initialize learning transition (state, action, reward, new_state)

        self.states = [None] * self.user_num
        self.actions = [None] * self.user_num
        self.rewards = [None] * self.user_num
        self.old_states = [None] * self.user_num
        self.old_actions = [None] * self.user_num

        self.data_idx = -1

        # Learning data

        self.state_data = np.zeros((self.user_num, self.state_dim, step_num * episode_num), dtype=np.float32)
        self.action_data = np.zeros((self.user_num, self.action_num, step_num * episode_num), dtype=np.float32)
        self.q_value_data = np.zeros((self.user_num, self.action_num, step_num * episode_num), dtype=np.float32)

        self.chamfer_data = np.zeros((self.user_num, step_num * episode_num), dtype=np.float32)
        self.qos_data = np.zeros((self.user_num, step_num * episode_num), dtype=np.float32)
        self.reward_data = np.zeros((self.user_num, step_num * episode_num), dtype=np.float32)
        self.temperature_data = np.zeros(step_num * episode_num, dtype=np.float32)
        self.loss_data = np.zeros(step_num * episode_num, dtype=np.float32)

    def reset(self):

        self.states = [None] * self.user_num
        self.actions = [None] * self.user_num
        self.rewards = [None] * self.user_num
        self.old_states = [None] * self.user_num
        self.old_actions = [None] * self.user_num

    def get_action(self,
                   states: [np.ndarray],
                   temp: float):

        """
        Choose an action according to the epsilon-greedy policy
        """

        assert 0 <= temp <= 1

        actions, q_values = [], []

        for user_idx, state in enumerate(states):

            x = torch.tensor(state[self.state_mask], dtype=torch.float32)

            # Estimate the q values of the input state

            with torch.no_grad():
                user_q_values = self.primary_net.forward(x).detach().numpy()

            # Choose an action according to the epsilon greedy policy

            if np.random.uniform() - temp > 0:
                user_action = np.argmax(user_q_values, 0)  # Greedy action
            else:
                user_action = np.random.randint(0, self.action_num)  # Random action

            actions.append(user_action)
            q_values.append(user_q_values)

        return actions, q_values

    def update(self,
               action_indexes: [int],
               q_values: [np.ndarray],
               rewards: [float],
               states: [np.ndarray],
               qos_per_user: [float],
               cd_per_user: [float],
               temp: float,
               train: bool):

        """
        Update the learning data of the agent
        """

        self.data_idx += 1

        self.temperature_data[self.data_idx] = temp

        for user_idx in range(self.user_num):

            # Update the learning data

            action_vector = np.zeros(self.action_num)
            action_vector[action_indexes[user_idx]] = 1
            self.action_data[user_idx, :, self.data_idx] = action_vector

            self.q_value_data[user_idx, :, self.data_idx] = q_values[user_idx]

            self.reward_data[user_idx, self.data_idx] = rewards[user_idx]
            self.state_data[user_idx, :, self.data_idx] = states[user_idx]
            self.qos_data[user_idx, self.data_idx] = qos_per_user[user_idx]
            self.chamfer_data[user_idx, self.data_idx] = cd_per_user[user_idx]

        # Update the transition variables

        self.old_states = [copy.copy(new_state) for new_state in self.states]
        self.old_actions = [copy.copy(new_state) for new_state in self.actions]

        self.actions = [action for action in action_indexes]
        self.rewards = [reward for reward in rewards]
        self.states = [new_state[self.state_mask] for new_state in states]

        if train:

            # If the state variable is not None, store the new transition in the replay memory

            if self.states[0] is not None:
                for user_idx in range(self.user_num):
                    self.dql.store_transition(np.copy(self.old_states[user_idx]),
                                              self.old_actions[user_idx],
                                              self.rewards[user_idx],
                                              np.copy(self.states[user_idx]))

            # If the replay memory is full, perform a learning step

            if self.dql.ready():
                loss = self.dql.step()

                # Update the algorithm loss

                self.loss_data[self.data_idx] = loss

    def save_data(self, data_folder: str):

        """
        Save the learning data
        """

        np.save(data_folder + 'states.npy', self.state_data)
        np.save(data_folder + 'rewards.npy', self.reward_data)
        np.save(data_folder + 'actions.npy', self.action_data)
        np.save(data_folder + 'q_values.npy', self.q_value_data)
        np.save(data_folder + 'temperatures.npy', self.temperature_data)
        np.save(data_folder + 'losses.npy', self.loss_data)
        np.save(data_folder + 'qos.npy', self.qos_data)
        np.save(data_folder + 'chamfer_distances.npy', self.chamfer_data)
        np.save(data_folder + 'data_idx.npy', self.data_idx)

    def save_model(self, data_folder: str):

        self.dql.save_model(data_folder)

    def load_data(self, data_folder: str):

        """
        Load the learning data
        """

        self.data_idx = np.load(data_folder + 'data_idx.npy')

        self.state_data = np.load(data_folder + 'states.npy')
        self.reward_data = np.load(data_folder + 'rewards.npy')
        self.action_data = np.load(data_folder + 'actions.npy')
        self.q_value_data = np.load(data_folder + 'q_values.npy')
        self.temperature_data = np.load(data_folder + 'temperatures.npy')
        self.loss_data = np.load(data_folder + 'losses.npy')

        self.qos_data = np.load(data_folder + 'qos.npy')
        self.chamfer_data = np.load(data_folder + 'chamfer_distances.npy')

    def load_model(self, data_folder: str):

        self.dql.load_model(data_folder)

    def plot_data(self, data_folder: str, episode_num: int):

        """
        Plot the learning data
        """

        state_palette = sns.color_palette('rocket', n_colors=np.sum(self.state_mask))
        action_palette = sns.color_palette('rocket_r', n_colors=3)
        single_palette = sns.color_palette('rocket', n_colors=1)

        for user_idx in range(self.user_num):

            ### LEARN PLOT ###

            user_folder = data_folder + '/learn/' + str(user_idx) + '/'

            # States

            multi_data = [self.state_data[user_idx, i, :self.data_idx] for i in range(self.state_dim) if
                          self.state_mask[i]]

            multi_keys = np.array(self.state_labels)[self.state_mask]

            multi_linear_plot(multi_data,
                              multi_keys,
                              'Episode',
                              'State',
                              episode_num,
                              user_folder + 'states',
                              palette=state_palette,
                              plot_format=self.format)

            # Q values

            multi_data = [self.q_value_data[user_idx, i, :self.data_idx] for i in range(self.action_num)]
            multi_keys = self.action_labels

            multi_linear_plot(multi_data,
                              multi_keys,
                              'Episode',
                              'Q value',
                              episode_num,
                              user_folder + 'q_values',
                              palette=action_palette,
                              plot_format=self.format)

            # Actions

            multi_data = [self.action_data[user_idx, i, :self.data_idx] for i in range(self.action_num)]
            multi_keys = self.action_labels

            multi_linear_plot(multi_data,
                              multi_keys,
                              'Episode',
                              'Action probability',
                              episode_num,
                              user_folder + 'actions',
                              palette=action_palette,
                              plot_format=self.format)

            # Reward

            linear_plot(self.reward_data[user_idx, :self.data_idx],
                        'Episode',
                        'Reward',
                        episode_num,
                        user_folder + 'rewards',
                        palette=single_palette,
                        plot_format=self.format)

            ### SINGLE FEATURE PLOT ###

            user_folder = data_folder + '/state/' + str(user_idx) + '/'

            for i in range(self.state_dim):
                min_value, max_value = self.state_normalization[i]

                linear_plot(self.state_data[user_idx, i, :self.data_idx] * (max_value - min_value) + min_value,
                            'Episode',
                            self.state_labels[i],
                            episode_num,
                            user_folder + self.state_labels[i].replace(' ', '_'),
                            palette=single_palette,
                            plot_format=self.format)

            ### PERFORMANCE PLOT ###

            user_folder = data_folder + '/performance/' + str(user_idx) + '/'

            linear_plot(self.chamfer_data[user_idx, :self.data_idx],
                        'Episode',
                        'Chamfer Distance',
                        episode_num,
                        user_folder + 'chamfer_distances',
                        palette=single_palette,
                        plot_format=self.format)

            linear_plot(
                (self.max_penalty - self.chamfer_data[user_idx, :self.data_idx]) / self.max_penalty,
                'Episode',
                'QoE',
                episode_num,
                user_folder + 'qoe',
                palette=single_palette,
                plot_format=self.format)

        # States

        state_data = np.mean(self.state_data, axis=0)

        multi_data = [state_data[i, :self.data_idx] for i in range(self.state_dim) if self.state_mask[i]]
        multi_keys = np.array(self.state_labels)[self.state_mask]

        multi_linear_plot(multi_data,
                          multi_keys,
                          'Episode',
                          'State',
                          episode_num,
                          data_folder + 'learn/states',
                          palette=state_palette,
                          plot_format=self.format)

        # Q values

        q_value_data = np.mean(self.q_value_data, axis=0)

        multi_data = [q_value_data[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          'Episode',
                          'Q value',
                          episode_num,
                          data_folder + 'learn/q_values',
                          palette=action_palette,
                          plot_format=self.format)

        # Actions

        action_data = np.mean(self.action_data, axis=0)

        multi_data = [action_data[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          'Episode',
                          'Action probability',
                          episode_num,
                          data_folder + 'learn/actions',
                          palette=action_palette,
                          plot_format=self.format)

        # Rewards

        reward_data = np.mean(self.reward_data, axis=0)

        linear_plot(reward_data[:self.data_idx],
                    'Episode',
                    'Reward',
                    episode_num,
                    data_folder + 'learn/rewards',
                    palette=single_palette,
                    plot_format=self.format)

        # Loss

        linear_plot(self.loss_data[:self.data_idx],
                    'Episode',
                    'Loss',
                    episode_num,
                    data_folder + 'learn/losses',
                    palette=single_palette,
                    plot_format=self.format)

        # Temperature

        linear_plot(self.temperature_data[:self.data_idx],
                    'Episode',
                    'Temperature',
                    episode_num,
                    data_folder + 'learn/temperatures',
                    palette=single_palette,
                    plot_format=self.format)

        # Single feature

        for i in range(self.state_dim):
            min_value, max_value = self.state_normalization[i]

            state_data = np.mean(self.state_data, axis=0)

            linear_plot(state_data[i, :self.data_idx] * (max_value - min_value) + min_value,
                        'Episode',
                        self.state_labels[i],
                        episode_num,
                        data_folder + 'state/' + self.state_labels[i].replace(' ', '_'),
                        palette=single_palette,
                        plot_format=self.format)

        # QoS

        qos_data = np.mean(self.qos_data, axis=0)

        linear_plot(qos_data[:self.data_idx],
                    'Episode',
                    'QoS',
                    episode_num,
                    data_folder + 'performance/qos',
                    palette=single_palette,
                    plot_format=self.format)

        # QoE

        chamfer_data = np.mean(self.chamfer_data, axis=0)

        linear_plot(chamfer_data[:self.data_idx],
                    'Episode',
                    'Chamfer Distance',
                    episode_num,
                    data_folder + 'performance/chamfer_distances',
                    palette=single_palette,
                    plot_format=self.format)

        linear_plot((self.max_penalty - chamfer_data[:self.data_idx]) / self.max_penalty,
                    'Episode',
                    'QoE',
                    episode_num,
                    data_folder + 'performance/qoe',
                    palette=single_palette,
                    plot_format=self.format)
