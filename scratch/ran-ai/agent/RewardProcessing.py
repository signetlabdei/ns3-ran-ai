import numpy as np


def reward_process(step_data_per_user,
                   prr_features: [],
                   app_delay_label: str,
                   app_prr_requirement: float,
                   app_delay_requirement: float,
                   last_actions: [int],
                   cd_per_action: [float],
                   user_num: int,
                   max_penalty: float,
                   reward_alpha: float,
                   online: bool,
                   qos_bonus: str):

    qos_per_user = [None] * user_num
    cd_per_user = [None] * user_num
    rewards = [None] * user_num

    imsi_list = []

    # Repeat for each user in the scenario

    for user_idx in range(user_num):

        step_data = step_data_per_user[user_idx]

        if online:
            imsi_list.append(int(step_data[0]))

        else:
            imsi_list.append(step_data['IMSI'])

        # Compute PRR

        num, den = step_data[prr_features[0][0]], step_data[prr_features[0][1]]
        
        if den == 0:
            prr = 1
        else:
            prr = num / den
        
        delay = step_data[app_delay_label]
        cd_per_user[user_idx] = cd_per_action[last_actions[user_idx]]

        if delay < app_delay_requirement and prr >= app_prr_requirement:

            # If the communication KPI are addressed...

            qos_per_user[user_idx] = 1
            cd_penalty = cd_per_user[user_idx] / max_penalty

            if qos_bonus == 'delay':
                qos_penalty = delay / app_delay_requirement
            elif qos_bonus == 'prr':
                qos_penalty = app_prr_requirement / prr
            else:
                raise ValueError

        else:

            # If the communication KPI are not addressed...

            qos_per_user[user_idx] = 0
            cd_penalty = 1
            qos_penalty = 1

        # Assign the reward to the user

        rewards[user_idx] = 1 - reward_alpha * cd_penalty - (1 - reward_alpha) * qos_penalty

    rewards = np.asarray(rewards, dtype=float)

    # Normalize the reward in [-1, +1]

    rewards -= 0.5
    rewards *= 2

    return rewards, qos_per_user, cd_per_user


def get_reward_per_action(penalty_per_action: [float], reward_penalty: float):
    reward_penalty += np.max(penalty_per_action)

    reward_per_action = np.array([reward_penalty / 2 - penalty for penalty in penalty_per_action]) / (
            reward_penalty / 2)

    return reward_per_action
