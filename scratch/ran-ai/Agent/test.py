import numpy as np
import random
import os
import sys
import time
from Agent.Agent import Agent


# Vanilla environment to test the framework

class test_environment(object):
    """

    """
    def __init__(self):
        self.states = [np.array([0]), np.array([1]), np.array([2])]
        self.actions = [0, 1, 2]
        self.state_normalization = np.array([2])
        self.state_dim = 1
        self.state_num = len(self.states)
        self.action_num = len(self.actions)
        self.rewards = [-1, 1, -1]
        self.penalty = -1

        self.state = None
        self.reward = None

    def reset(self):
        """

        """
        self.state = np.copy(random.sample(self.states, 1)[0])

    def get_data(self):
        """

        :return:
        :rtype:
        """
        return np.copy(self.state), self.reward

    def take_action(self, action: int):
        """

        :param action:
        :type action:
        :return:
        :rtype:
        """
        if action == 0:
            self.state = np.copy(self.state)
        elif action == 1:
            self.state -= 1
        elif action == 2:
            self.state += 1
        else:
            raise ValueError

        if self.state[0] < 0:
            self.state = np.copy(self.states[0])
            self.reward = self.penalty
        elif self.state[0] > 2:
            self.state = np.copy(self.states[2])
            self.reward = self.penalty
        else:
            self.reward = self.rewards[self.state[0]]


# Training example

env = test_environment()

# Initialize the agent

episode_num = 100  # Number of episodes
step_num = 100  # Number of steps per episode
temperatures = np.flip(np.arange(episode_num)) / episode_num  # Temperatures (for the epsilon greedy policy)

agent = Agent(state_dim=env.state_dim, action_num=env.action_num,
              step_num=step_num, episode_num=episode_num,
              gamma=0.9, batch_size=16, target_replace=200, memory_capacity=200,
              learning_rate=0.0001, eps=0.0001, weight_decay=0.0001)

# Output folder

data_folder = 'scratch/ran-ai/Agent/test/'

if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Training cycles

start_time = time.time()

for episode in range(episode_num):

    print("Episode ", episode, "; ", end="")
    print('\r', end="")

    # Initialize learning variables

    action = None
    state = None
    q_values = None

    # Initialize environment and agent

    env.reset()
    agent.reset()
    temp = temperatures[episode]

    for step in range(step_num):
        new_state, reward = env.get_data()
        if state is not None:
            agent.update(action, q_values, reward, new_state, temp, step, episode)
        state = np.copy(new_state)
        action, q_values = agent.get_action(state, temp)

        env.take_action(action)

end_time = time.time()

# Plot the output data

agent.save_data(data_folder)
agent.load_data(data_folder)

agent.plot_data(data_folder, episode_num)
