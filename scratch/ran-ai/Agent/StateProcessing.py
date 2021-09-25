import numpy as np
from ctypes import *


def state_process(env_features: Structure, env_normalization: {}, state_features: [], state_dim: int):

    state = np.zeros(state_dim)
    for i, feature in enumerate(state_features):

        if feature == 'mcs':
            state[i] = env_features.mcs

        elif feature == 'symbols':

            state[i] = float(env_features.symbols)

        elif feature == 'sinr':
            state[i] = env_features.sinr

        elif feature == 'rlcTxPackets':
            state[i] = env_features.rlcTxPackets

        elif feature == 'rlcTxData':
            state[i] = env_features.rlcTxData

        elif feature == 'rlcRxPackets':
            state[i] = env_features.rlcRxPackets

        elif feature == 'rlcRxData':
            state[i] = env_features.rlcRxData

        elif feature == 'pdcpTxPackets':
            state[i] = env_features.pdcpTxPackets

        elif feature == 'pdcpTxData':
            state[i] = env_features.pdcpTxData

        elif feature == 'pdcpRxPackets':
            state[i] = env_features.pdcpRxPackets

        elif feature == 'pdcpRxData':
            state[i] = env_features.pdcpRxData

        elif feature == 'pdcpDelayMean':
            state[i] = env_features.pdcpDelayMean

        elif feature == 'pdcpDelayMax':
            state[i] = env_features.pdcpDelayMax

        elif feature == 'rlcDelayMean':
            state[i] = env_features.rlcDelayMean

        elif feature == 'rlcDelayMax':
            state[i] = env_features.rlcDelayMax

        elif feature == 'pdcpRatio':
            if env_features.pdcpTxData > 0:
                state[i] = env_features.pdcpRxData / env_features.pdcpTxData
            else:
                state[i] = 1

        elif feature == 'rlcRatio':
            if env_features.rlcTxData > 0:
                state[i] = env_features.rlcRxData / env_features.rlcTxData
            else:
                state[i] = 1

        else:
            raise ValueError("Unknown state variable!")

        shift, norm = env_normalization[feature]
        state[i] -= np.min((state[i], shift))
        state[i] = np.min((1, state[i] / norm))

    if env_features.pdcpTxData > 0:
        reward = np.min((1, env_features.pdcpRxData / env_features.pdcpTxData))

    else:
        reward = 1

    reward -= env_features.pdcpDelayMean

    return state, reward
