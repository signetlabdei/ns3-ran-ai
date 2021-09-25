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

        self.state = None
        self.action = None
        self.reward = None
        self.new_state = None

        self.data_idx = -1

        # Learning data

        self.states = np.zeros((self.state_dim, step_num * episode_num), dtype=np.float32)
        self.actions = np.zeros((self.action_num, step_num * episode_num), dtype=np.float32)
        self.rewards = np.zeros(step_num * episode_num, dtype=np.float32)
        self.temperatures = np.zeros(step_num * episode_num, dtype=np.float32)
        self.losses = np.zeros(step_num * episode_num, dtype=np.float32)
        self.q_values = np.zeros((self.action_num, step_num * episode_num), dtype=np.float32)

    def reset(self):

        self.state = None
        self.action = None
        self.reward = None
        self.new_state = None

    def get_action(self,
                   state: np.ndarray,
                   temp: float):

        """
        Choose an action according to the epsilon-greedy policy
        """

        assert 0 <= temp <= 1

        x = torch.tensor(state, dtype=torch.float32)

        # Estimate the q values of the input state

        with torch.no_grad():
            q_values = self.primary_net.forward(x).detach().numpy()

        # Choose an action according to the epsilon greedy policy

        if np.random.uniform() - temp > 0:
            action = np.argmax(q_values, 0)  # Greedy action
        else:
            action = np.random.randint(0, self.action_num)  # Random action

        return action, q_values

    def update(self,
               action: int,
               q_values: np.ndarray,
               reward: float,
               new_state: np.ndarray,
               temp: float):

        """
        Update the learning data of the agent
        """

        self.data_idx += 1

        # Update the learning data

        self.q_values[:, self.data_idx] = q_values
        action_vector = np.zeros(self.action_num)
        action_vector[action] = 1
        self.actions[:, self.data_idx] = action_vector
        self.rewards[self.data_idx] = reward
        self.states[:, self.data_idx] = new_state

        self.temperatures[self.data_idx] = temp

        # Update the transition variables

        self.state = copy.copy(self.new_state)
        self.action = action
        self.reward = reward
        self.new_state = new_state

        # If the state variable is not None, store the new transition in the replay memory

        if self.state is not None:
            self.dql.store_transition(np.copy(self.state),
                                      self.action,
                                      self.reward,
                                      np.copy(self.new_state))

        # If the replay memory is full, perform a learning step

        if self.dql.ready():
            loss = self.dql.step()

            # Update the algorithm loss

            self.losses[self.data_idx] = loss

    def save_data(self, data_folder: str):

        """
        Save the learning data
        """

        np.save(data_folder + 'states.npy', self.states)
        np.save(data_folder + 'rewards.npy', self.rewards)
        np.save(data_folder + 'actions.npy', self.actions)
        np.save(data_folder + 'q_values.npy', self.q_values)
        np.save(data_folder + 'temperatures.npy', self.temperatures)
        np.save(data_folder + 'losses.npy', self.losses)
        np.save(data_folder + 'data_idx.npy', self.data_idx)

    def save_model(self, data_folder: str):

        self.dql.save_model(data_folder)

    def load_data(self, data_folder: str):

        """
        Load the learning data
        """

        self.states = np.load(data_folder + 'states.npy')
        self.rewards = np.load(data_folder + 'rewards.npy')
        self.actions = np.load(data_folder + 'actions.npy')
        self.q_values = np.load(data_folder + 'q_values.npy')
        self.temperatures = np.load(data_folder + 'temperatures.npy')
        self.losses = np.load(data_folder + 'losses.npy')
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

        # States

        multi_data = [self.states[i, :self.data_idx] for i in range(self.state_dim)]
        multi_keys = self.state_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'State',
                          xlabel,
                          plot_points,
                          data_folder + 'states')

        # Q values

        multi_data = [self.q_values[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'Q value',
                          xlabel,
                          plot_points,
                          data_folder + 'q_values')

        # Actions

        multi_data = [self.actions[i, :self.data_idx] for i in range(self.action_num)]
        multi_keys = self.action_labels

        multi_linear_plot(multi_data,
                          multi_keys,
                          x_num,
                          'Action probbility',
                          xlabel,
                          plot_points,
                          data_folder + 'actions')

        # Single feature

        for i in range(self.state_dim):

            shift, factor = self.state_normalization[i]

            linear_plot(self.states[i, :self.data_idx] * factor + shift,
                        x_num,
                        self.state_labels[i],
                        xlabel,
                        plot_points,
                        data_folder + str(self.state_labels[i]))

        # Rewards

        linear_plot(self.rewards[ :self.data_idx],
                    x_num,
                    'Reward',
                    xlabel,
                    plot_points,
                    data_folder + 'rewards')

        # Loss

        linear_plot(self.losses[ :self.data_idx],
                    x_num,
                    'Loss',
                    xlabel,
                    plot_points,
                    data_folder + 'losses')

        # Temperature

        linear_plot(self.temperatures[ :self.data_idx],
                    x_num,
                    'Temperature',
                    xlabel,
                    plot_points,
                    data_folder + 'temperatures')
