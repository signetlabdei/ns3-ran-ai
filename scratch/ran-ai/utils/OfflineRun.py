from agent.StateProcessing import state_process
from agent.RewardProcessing import reward_process
from agent.Agent import CentralizedAgent
from settings.StateSettings import state_features, state_feature_normalization, combination_features, \
    combination_feature_normalization
from settings.StateSettings import app_pdr_labels, app_max_delay_label
import numpy as np
import pickle5 as pickle


def run_offline_episode(user_num: int,
                        state_dim: int,
                        max_penalty: float,
                        reward_alpha: float,
                        default_action_index: int,
                        action_penalties: [],
                        pdr_requirement: float,
                        delay_requirement: float,
                        algorithm_training: bool,
                        agent: CentralizedAgent,
                        episode_data,
                        qos_bonus: str,
                        step_num=None):

    action_indexes = [default_action_index] * user_num

    with open(episode_data, "rb") as episode_data:
        episode_data = pickle.load(episode_data)

    imsi_indexes = episode_data['IMSI'].unique()

    episode_data_per_user = []

    for imsi in imsi_indexes:
        user_data = episode_data.loc[episode_data['IMSI'] == imsi]
        user_data = user_data.reset_index()
        episode_data_per_user.append(user_data)

    if step_num is None:
        step_num = len(episode_data_per_user[0])

    # Repeat per each step of the episode

    for step in range(step_num):

        step_data_per_user = [user_data.loc[step] for user_data in episode_data_per_user]

        # Process the agent state

        new_states, imsi_list = state_process(step_data_per_user,
                                              state_features,
                                              state_feature_normalization,
                                              combination_features,
                                              combination_feature_normalization,
                                              state_dim,
                                              user_num,
                                              online=False)

        # Process the agent reward

        rewards, qos_per_user, cd_per_user = reward_process(step_data_per_user,
                                                            app_pdr_labels,
                                                            app_max_delay_label,
                                                            pdr_requirement,
                                                            delay_requirement,
                                                            action_indexes,
                                                            action_penalties,
                                                            user_num,
                                                            max_penalty,
                                                            reward_alpha,
                                                            online=False,
                                                            qos_bonus=qos_bonus)

        states = [np.copy(new_state) for new_state in new_states]

        # Get the agent q values

        _, q_values = agent.get_action(states, 0)

        # Update the data of the agent

        agent.update(action_indexes,
                     q_values,
                     rewards,
                     states,
                     qos_per_user,
                     cd_per_user,
                     0,
                     algorithm_training)
