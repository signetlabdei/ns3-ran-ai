from ctypes import *
import numpy as np


def reward_process(env_features: Structure,
                   pdr_feature_indexes: [],
                   app_delay_mean_index: int,
                   app_delay_requirement: float,
                   last_actions: [int],
                   penalty_per_action: [float],
                   user_num: int,
                   reward_penalty: float):

    qos_per_user = [0] * user_num
    qoe_per_user = [0] * user_num

    rewards = [-reward_penalty / 2] * user_num
    imsi_list = []

    for user_idx in range(user_num):

        imsi_list.append(int(env_features[user_idx][0]))

        for state_idx, comb_indexes in enumerate(pdr_feature_indexes):

            num_idx, den_idx = comb_indexes
            num, den = env_features[user_idx][num_idx], env_features[user_idx][den_idx]
            delay = env_features[user_idx][app_delay_mean_index]

            qoe_per_user[user_idx] = penalty_per_action[last_actions[user_idx]]

            if delay < app_delay_requirement and (den <= 0 or num / den >= 1):

                qos_per_user[user_idx] = 1
                rewards[user_idx] = reward_penalty / 2 - penalty_per_action[last_actions[user_idx]]

    rewards /= reward_penalty / 2  # Force the reward to be in [-1, 1]
                
    return rewards, qos_per_user, qoe_per_user, imsi_list


def get_reward_per_action(penalty_per_action: [float], reward_penalty: float):

    reward_penalty += np.max(penalty_per_action)

    reward_per_action = np.array([reward_penalty / 2 - penalty for penalty in penalty_per_action]) / (reward_penalty / 2)

    return reward_per_action
