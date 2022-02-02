from agent.StateProcessing import state_process
from agent.RewardProcessing import reward_process
from agent.Agent import CentralizedAgent
from settings.StateSettings import state_feature_indexes, state_feature_normalization, combination_feature_indexes, \
    combination_feature_normalization
from settings.StateSettings import app_pdr_indexes, app_max_delay_index
import numpy as np


def run_online_episode(action_num: int,
                       user_num: int,
                       state_dim: int,
                       max_penalty: float,
                       reward_alpha: float,
                       temp: float,
                       agent_policy: str,
                       default_action_index: int,
                       action_labels: [],
                       action_penalties: [],
                       pdr_requirement: float,
                       delay_requirement: float,
                       algorithm_training: bool,
                       agent: CentralizedAgent,
                       experiment_instance,
                       qos_bonus: str,
                       step_num=None):

    action_indexes = list(np.random.randint(0, action_num, user_num))
    step = -1

    if step_num is None:
        step_num = np.infty

    while not experiment_instance.isFinish():
        with experiment_instance as data:

            step += 1

            if data is None or step >= step_num:
                break

            new_states, state_imsi_list = state_process(data.env.imsiStatsMap,
                                                        state_feature_indexes,
                                                        state_feature_normalization,
                                                        combination_feature_indexes,
                                                        combination_feature_normalization,
                                                        state_dim,
                                                        user_num,
                                                        online=True)

            rewards, qos_per_user, cd_per_user = reward_process(data.env.imsiStatsMap,
                                                                app_pdr_indexes,
                                                                app_max_delay_index,
                                                                pdr_requirement,
                                                                delay_requirement,
                                                                action_indexes,
                                                                action_penalties,
                                                                user_num,
                                                                max_penalty,
                                                                reward_alpha,
                                                                online=True,
                                                                qos_bonus=qos_bonus)

            states = [np.copy(new_state) for new_state in new_states]

            action_indexes, q_values = agent.get_action(states, temp)

            if agent_policy == 'random':

                action_indexes = list(np.random.randint(0, action_num, user_num))

            elif agent_policy != 'dql':

                action_indexes = [default_action_index] * user_num

            agent.update(action_indexes,
                         q_values,
                         rewards,
                         states,
                         qos_per_user,
                         cd_per_user,
                         temp,
                         algorithm_training)

            for user_idx, action_idx in enumerate(action_indexes):
                imsi = state_imsi_list[user_idx]
                action = action_labels[action_idx]
                data.act.actions[user_idx][0] = int(imsi)
                data.act.actions[user_idx][1] = action
