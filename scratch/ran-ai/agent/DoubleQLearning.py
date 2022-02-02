import torch
from torch.nn import Module
from agent.NeuralNetwork import LinearNeuralNetwork
import numpy as np
import random


class DQL(object):
    """
    class DQL
    It implements the Double Q Learning algorithm

    """

    def __init__(self,
                 primary_net: Module,
                 target_net: Module,
                 optimizer,
                 action_num: int,
                 gamma: float,
                 batch_size: int,
                 target_replace: int,
                 memory_capacity: int):

        # Target and evaluation networks used in the training

        self.primary_net: LinearNeuralNetwork = primary_net  # Choose new actions
        self.target_net: LinearNeuralNetwork = target_net  # Estimate the future q values

        # Learning weights optimizer

        self.optimizer = optimizer

        # Action num

        self.action_num: int = action_num

        # Counters of the number of learning steps and the number of transition inserted in the memory replay

        self.learn_step: int = 0
        self.memory_step: int = 0

        # Learning parameters

        self.batch_size: int = batch_size
        self.target_replace: int = target_replace
        self.gamma: float = gamma  # Should be close to 1

        # Memory replay

        self.memory_capacity: int = memory_capacity
        self.memory = []
        self.memory_probs = []
        self.memory_indexes = range(self.memory_capacity)

    def store_transition(self, state: np.ndarray, action: int, reward: float, new_state: np.ndarray):

        """
        Insert a new transition (state, action, reward, new state) in the memory replay
        """

        if self.memory_step < self.memory_capacity:
            self.memory.append([state, action, reward, new_state])  # Transition
            self.memory_probs.append(0)  # Probability of pick the transition (in case of a prioritize memory replay)
        else:
            index: int = int(self.memory_step % self.memory_capacity)  # Index of the transition
            self.memory[index] = [state, action, reward, new_state]  # Transition
            self.memory_probs[index] = 0  # Probability of pick the transition (in case of a prioritize memory replay)

        self.memory_step += 1  # Increase the number of total transition

    def ready(self):

        # Return true if the memory is full

        return self.memory_step >= self.memory_capacity

    def step(self):

        """
        Take a batch from the memory replay and perform a training step
        """

        self.learn_step += 1

        # Prioritize memory replay
        # batch_indexes = random.choices(self.memory_indexes, k=self.batch_size, weights=self.memory_probs)

        # Random sampling the indexes of the transition inserted in the batch used for the training

        batch_transitions = random.sample(self.memory, self.batch_size)

        batch_states = torch.stack(
            [torch.tensor(transition[0], dtype=torch.float32) for transition in batch_transitions])
        batch_actions = torch.tensor(
            [transition[1] for transition in batch_transitions], dtype=torch.int64).view(-1, 1)
        batch_rewards = torch.tensor(
            [transition[2] for transition in batch_transitions], dtype=torch.float32)
        batch_new_states = torch.stack(
            [torch.tensor(transition[3], dtype=torch.float32) for transition in batch_transitions])

        actual_q_values = self.primary_net.forward(batch_states).gather(1, batch_actions).squeeze(1)

        with torch.no_grad():
            next_q_values: torch.FloatTensor = self.primary_net.forward(batch_new_states)

            next_actions = torch.argmax(next_q_values, dim=1).view(-1, 1)

            target_q_values = batch_rewards + self.gamma * \
                              self.target_net.forward(batch_new_states).gather(1, next_actions).squeeze(
                                  1).numpy()

        losses = (actual_q_values - target_q_values) ** 2

        # Compute the mean loss of the batch

        loss_mean = losses.mean()

        # Optimization step

        self.optimizer.zero_grad()
        loss_mean.backward()
        self.optimizer.step()

        # Periodically, replace the weights of the target network with those of the primary network

        if self.learn_step % self.target_replace == 0:
            self.target_net.load_state_dict(self.primary_net.state_dict())

        loss_mean = loss_mean.item()

        return loss_mean

    def load_model(self, output_folder: str):

        """
        Load the learning weights of the neural network
        """

        print("Load learning model from: ", output_folder)

        params = torch.load(output_folder + 'model')
        self.primary_net.load_state_dict(params)
        self.target_net.load_state_dict(params)

    def save_model(self, output_folder: str):

        """
        Save the learning weights of the neural network
        """

        params = self.primary_net.state_dict()
        torch.save(params, output_folder + 'model')
