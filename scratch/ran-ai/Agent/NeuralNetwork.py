from abc import ABC
import torch
from torch.nn import Module


class LinearNeuralNetwork(Module, ABC):

    """
    class LinearNeuralNetwork
    It defines a basic linear neural network to estimate the action q-values

    """

    def __init__(self,
                 input_dim: int,
                 output_dim: int
                 ):

        super(LinearNeuralNetwork, self).__init__()

        # Linear layers

        self.linear_1 = torch.nn.Linear(input_dim, 12)
        self.linear_2 = torch.nn.Linear(12, 6)
        self.linear_3 = torch.nn.Linear(6, output_dim)

        # Layer initialization

        torch.nn.init.kaiming_uniform_(self.linear_1.weight,
                                       nonlinearity='relu')
        torch.nn.init.kaiming_uniform_(self.linear_2.weight,
                                       nonlinearity='relu')
        torch.nn.init.uniform_(self.linear_3.weight)

        torch.nn.init.zeros_(self.linear_1.bias)
        torch.nn.init.zeros_(self.linear_2.bias)
        torch.nn.init.uniform_(self.linear_3.bias)

    def forward(self, x: torch.Tensor):
        """

        Compute the q values of the input tensor x
        """

        x = torch.nn.functional.relu(self.linear_1(x))
        x = torch.nn.functional.relu(self.linear_2(x))
        x = self.linear_3(x)

        return x
