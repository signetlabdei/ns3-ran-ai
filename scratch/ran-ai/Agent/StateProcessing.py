import numpy as np
from ctypes import *


def state_process(env_features: Structure,
                  feature_indexes: [],
                  feature_normalization: [],
                  combination_feature_indexes: [],
                  combination_feature_normalization: [],
                  state_dim: int,
                  user_num: int):

    states = [np.zeros(state_dim) for _ in range(user_num)]
    imsi_list = []

    feature_num = len(feature_indexes)

    for user_idx in range(user_num):
        imsi_list.append(int(env_features[user_idx][0]))

        for state_idx, feature_idx in enumerate(feature_indexes):
            min_value = feature_normalization[state_idx][0]
            max_value = feature_normalization[state_idx][1]

            feature = env_features[user_idx][feature_idx]
            feature = np.max((min_value, feature))
            feature = np.min((max_value, feature))
            feature = (feature - min_value) / (max_value - min_value)

            states[user_idx][state_idx] = feature

        for state_idx, comb_indexes in enumerate(combination_feature_indexes):

            num_idx, den_idx = comb_indexes
            num, den = env_features[user_idx][num_idx], env_features[user_idx][den_idx]

            min_value = combination_feature_normalization[state_idx][0]
            max_value = combination_feature_normalization[state_idx][1]

            if den <= 0:
                feature = 1
            else:
                feature = num / den

            feature = np.max((min_value, feature))
            feature = np.min((max_value, feature))
            feature = (feature - min_value) / (max_value - min_value)

            states[user_idx][state_idx + feature_num] = feature

    return states, imsi_list
