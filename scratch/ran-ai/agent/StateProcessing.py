import numpy as np


def state_process(step_data_per_user,
                  features: [],
                  feature_normalization: [],
                  combination_features: [],
                  combination_feature_normalization: [],
                  state_dim: int,
                  user_num: int,
                  online: bool):
    states = [np.zeros(state_dim) for _ in range(user_num)]

    feature_num = len(features)

    imsi_list = []

    # Repeat for each user in the scenario

    for user_idx in range(user_num):

        step_data = step_data_per_user[user_idx]

        if online:
            imsi_list.append(int(step_data[0]))

        else:

            imsi_list.append(step_data['IMSI'])

        # Add to the state the different features

        for state_idx, label in enumerate(features):

            feature = step_data[label]

            min_value = feature_normalization[state_idx][0]
            max_value = feature_normalization[state_idx][1]
            feature = np.max((min_value, feature))
            feature = np.min((max_value, feature))
            feature = (feature - min_value) / (max_value - min_value)

            states[user_idx][state_idx] = feature

        # Add to the state the PRR values

        for state_idx, comb_features in enumerate(combination_features):

            num, den = step_data[comb_features[0]], step_data[comb_features[1]]

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
