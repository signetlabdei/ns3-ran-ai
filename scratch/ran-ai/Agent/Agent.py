import torch
import copy
import numpy as np
from torch.nn import Module
from Agent.DoubleQLearning import DQL
from Agent.NeuralNetwork import LinearNeuralNetwork
from Agent.Linearplot import linear_plot, multi_linear_plot


class Agent(object):
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
                 gamma: float,
                 batch_size: int,
                 target_replace: int,
                 memory_capacity: int,
                 learning_rate: float,
                 eps: float,
                 weight_decay: float):

        # Number of steps and episodes

        self.step_num, self.episode_num = step_num, episode_num

        # State dimension

        self.state_dim: int = state_dim

        # Number of possible actions in each state

        self.action_num: int = action_num

        # Number of users controlled by the learner

        self.user_num: int = user_num

        # State and action labels

        self.state_labels = state_labels
        self.action_labels = action_labels
        self.state_normalization = state_normalization

        # Primary and target networks used in the training
        # The primary network is used to choose new actions
        # The target network is used to predict the future q values

        self.primary_net: Module = LinearNeuralNetwork(state_dim, self.action_num)
        target_net: Module = LinearNeuralNetwork(state_dim, self.action_num)
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
        self.new_states = [None] * self.user_num

        self.data_idx = -1

        # Learning data

        self.state_data = np.zeros((self.user_num, self.state_dim, step_num * episode_num), dtype=np.float32)
        self.action_data = np.zeros((self.user_num, self.action_num, step_num * episode_num), dtype=np.float32)
        self.q_value_data = np.zeros((self.user_num, self.action_num, step_num * episode_num), dtype=np.float32)

        self.reward_data = np.zeros((self.user_num, step_num * episode_num), dtype=np.float32)
        self.temperature_data = np.zeros(step_num * episode_num, dtype=np.float32)
        self.loss_data = np.zeros(step_num * episode_num, dtype=np.float32)

    def reset(self):

        self.states = [None] * self.user_num
        self.actions = [None] * self.user_num
        self.rewards = [None] * self.user_num
        self.new_states = [None] * self.user_num

    def get_action(self,
                   states: [np.ndarray],
                   temp: float):

        """
        Choose an action according to the epsilon-greedy policy
        """

        assert 0 <= temp <= 1

        actions, q_values = [], []

        for user_idx, state in enumerate(states):

            x = torch.tensor(state, dtype=torch.float32)

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
               actions: [int],
               q_values: [np.ndarray],
               rewards: [float],
               new_states: [np.ndarray],
               temp: float):

        """
        Update the learning data of the agent
        """

        self.data_idx += 1

        self.temperature_data[self.data_idx] = temp

        for user_idx in range(self.user_num):

            user_action = actions[user_idx]
            user_q_values = q_values[user_idx]
            user_reward = rewards[user_idx]
            user_new_state = new_states[user_idx]

            # Update the learning data

            self.q_value_data[user_idx, :, self.data_idx] = user_q_values
            action_vector = np.zeros(self.action_num)
            action_vector[user_action] = 1
            self.action_data[user_idx, :, self.data_idx] = action_vector
            self.reward_data[user_idx, self.data_idx] = user_reward
            self.state_data[user_idx, :, self.data_idx] = user_new_state

        # Update the transition variables

        self.states = [copy.copy(new_state) for new_state in new_states]
        self.actions = [action for action in actions]
        self.rewards = [reward for reward in rewards]
        self.new_states = [new_state for new_state in new_states]

        # If the state variable is not None, store the new transition in the replay memory

        if self.states[0] is not None:
            for user_idx in range(self.user_num):
                self.dql.store_transition(np.copy(self.states[user_idx]),
                                          self.actions[user_idx],
                                          self.rewards[user_idx],
                                          np.copy(self.new_states[user_idx]))

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
        np.save(data_folder + 'data_idx.npy', self.data_idx)

    def save_model(self, data_folder: str):

        self.dql.save_model(data_folder)

    def load_data(self, data_folder: str):

        """
        Load the learning data
        """

        self.state_data = np.load(data_folder + 'states.npy')
        self.reward_data = np.load(data_folder + 'rewards.npy')
        self.action_data = np.load(data_folder + 'actions.npy')
        self.q_value_data = np.load(data_folder + 'q_values.npy')
        self.temperature_data = np.load(data_folder + 'temperatures.npy')
        self.loss_data = np.load(data_folder + 'losses.npy')
        self.data_idx = np.load(data_folder + 'data_idx.npy')

    def load_model(self, data_folder: str):

        self.dql.load_model(data_folder)

    def plot_data(self, data_folder: str, episode_num: int, plot_points=50):

        """
        Plot the learning data
        """

        if episode_num >= plot_points:
            xlabel = 'Episode'
            x_num = episode_num
        else:
            xlabel = 'Step'
            x_num = self.step_num * self.episode_num

        for user_idx in range(self.user_num):
            user_folder = data_folder + 'user_' + str(user_idx) + '/'

            # States

            multi_data = [self.state_data[user_idx, i, :self.data_idx] for i in range(self.state_dim)]
            multi_keys = self.state_labels

            multi_linear_plot(multi_data,
                              multi_keys,
                              x_num,
                              'State',
                              xlabel,
                              plot_points,
                              user_folder + 'states')

            # Q values

            multi_data = [self.q_value_data[user_idx, i, :self.data_idx] for i in range(self.action_num)]
            multi_keys = self.action_labels

            multi_linear_plot(multi_data,
                              multi_keys,
                              x_num,
                              'Q value',
                              xlabel,
                              plot_points,
                              user_folder + 'q_values')

            # Actions

            multi_data = [self.action_data[user_idx, i, :self.data_idx] for i in range(self.action_num)]
            multi_keys = self.action_labels

            multi_linear_plot(multi_data,
                              multi_keys,
                              x_num,
                              'Action probability',
                              xlabel,
                              plot_points,
                              user_folder + 'actions')

            # Single feature

            for i in range(self.state_dim):

                min_value, max_value = self.state_normalization[i]

                linear_plot(self.state_data[user_idx, i, :self.data_idx] * (max_value - min_value) + min_value,
                            x_num,
                            self.state_labels[i],
                            xlabel,
                            plot_points,
                            user_folder + str(self.state_labels[i]))

            # Rewards

            linear_plot(self.reward_data[user_idx, :self.data_idx],
                        x_num,
                        'Reward',
                        xlabel,
                        plot_points,
                        user_folder + 'rewards')

        # States

        state_data = np.mean(self.state_data, axis=0)

        multi_data = [state_data[i, :self.data_idx] for i in range(self.state_dim)]
        multi_keys = self.state_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'State',
                          xlabel,
                          plot_points,
                          data_folder + 'states')

        # Q values

        q_value_data = np.mean(self.q_value_data, axis=0)

        multi_data = [q_value_data[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'Q value',
                          xlabel,
                          plot_points,
                          data_folder + 'q_values')

        # Actions

        action_data = np.mean(self.action_data, axis=0)

        multi_data = [action_data[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'Action probability',
                          xlabel,
                          plot_points,
                          data_folder + 'actions')

        # Single feature

        for i in range(self.state_dim):
            min_value, max_value = self.state_normalization[i]

            state_data = np.mean(self.state_data, axis=0)

            linear_plot(state_data[i, :self.data_idx] * (max_value - min_value) + min_value,
                        x_num,
                        self.state_labels[i],
                        xlabel,
                        plot_points,
                        data_folder + str(self.state_labels[i]))

        # Rewards

        reward_data = np.mean(self.reward_data, axis=0)

        linear_plot(reward_data[:self.data_idx],
                    x_num,
                    'Reward',
                    xlabel,
                    plot_points,
                    data_folder + 'rewards')

        # Loss

        linear_plot(self.loss_data[:self.data_idx],
                    x_num,
                    'Loss',
                    xlabel,
                    plot_points,
                    data_folder + 'losses')

        # Temperature

        linear_plot(self.temperature_data[:self.data_idx],
                    x_num,
                    'Temperature',
                    xlabel,
                    plot_points,
                    data_folder + 'temperatures')
