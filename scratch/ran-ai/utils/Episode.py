from py_interface import Ns3AIRL
import numpy as np
import time
from agent.Agent import CentralizedAgent
from settings.GeneralSettings import memblock_key, Env, Act


def initialize_online_episode(episode: int,
                              episode_num: int,
                              agent: CentralizedAgent,
                              data_folder: str,
                              algorithm_training: bool,
                              temperatures: np.ndarray,
                              exp,
                              ns3Settings):

    episode_start_time = time.time()

    # Periodically save the episode date

    if episode > 0 and episode % int(episode_num / 10) == 0:
        agent.save_data(data_folder)
        agent.save_model(data_folder)
        agent.plot_data(data_folder, episode_num)

    # Get the temperature of the episode

    if algorithm_training:
        temp = temperatures[episode]
    else:
        temp = 0

    exp.reset()  # Reset the environment
    rl = Ns3AIRL(memblock_key, Env, Act)  # Link the shared memory block with ns-3 script
    ns3Settings['firstVehicleIndex'] = np.random.randint(1, 51)  # Randomly set the first vehicle
    ns3Settings['RngRun'] = np.random.randint(1, 10)  # Randomly set the simulation seed
    pro = exp.run(setting=ns3Settings, show_output=True)  # Set and run the ns-3 script (sim.cc)

    return temp, episode_start_time, rl, pro


def initialize_offline_episode(episode: int,
                               episode_num: int,
                               agent: CentralizedAgent,
                               data_folder: str):

    episode_start_time = time.time()

    # Periodically save the episode date

    if episode_num > 10 and episode > 0 and episode % int(episode_num / 10) == 0:
        agent.save_data(data_folder)
        agent.save_model(data_folder)
        agent.plot_data(data_folder, episode_num)

    return episode_start_time


def finalize_episode(episode_start_time: float, simulation_time: float, episode: int, episode_num: int):

    episode_end_time = time.time()
    episode_time = episode_end_time - episode_start_time
    simulation_time += episode_time
    average_episode_time = simulation_time / (episode + 1)
    missing_episode_num = episode_num - episode - 1

    print("Episode ", episode, "; episode duration [s]", episode_time, "; expected residual time [min]", average_episode_time * missing_episode_num / 60)

    return simulation_time

