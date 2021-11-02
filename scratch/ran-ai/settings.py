from ctypes import *
import numpy as np


# The environment is shared between ns-3
# and python with the same shared memory
# using the ns3-ai model.

class Env(Structure):
    _pack_ = 1
    _fields_ = [
        ('imsiStatsMap', (c_double * 28) * 50)
    ]


# The result is calculated by python
# and put back to ns-3 with the shared memory.

class Act(Structure):
    _pack_ = 1
    _fields_ = [
        ('actions', (c_int16 * 2) * 50)
    ]


cf_mean_per_action = {1150: 0.002492,
                      1450: 0.000044,
                      1451: 5.476881,
                      1452: 35.634660,
                      0: 0,
                      1: 5.476811,
                      2: 35.634485}


env_features = ['imsi',
                'mcs',
                'symbols',
                'sinr',

                'rlc_tx_pkt',
                'rlc_tx_data',
                'rlc_rx_pkt',
                'rlc_rx_data',

                'rlc_delay_mean',
                'rlc_delay_stdev',
                'rlc_delay_min',
                'rlc_delay_max',

                'pdcp_tx_pkt',
                'pdcp_tx_data',
                'pdcp_rx_pkt',
                'pdcp_rx_data',

                'pdcp_delay_mean',
                'pdcp_delay_stdev',
                'pdcp_delay_min',
                'pdcp_delay_max',

                'app_tx_pkt',
                'app_tx_data',
                'app_rx_pkt',
                'app_rx_data',

                'app_delay_mean',
                'app_delay_stdev',
                'app_delay_min',
                'app_delay_max'
                ]

env_normalization = {'imsi': None,
                     'mcs': (0, 28),
                     'symbols': (0, 12),
                     'sinr': (0, 60),

                     'rlc_tx_pkt': (0, 1),
                     'rlc_tx_data': (0, 1),
                     'rlc_rx_pkt': (0, 1),
                     'rlc_rx_data': (0, 1),

                     'rlc_delay_mean': (0, 100000000),
                     'rlc_delay_stdev': (0, 100000000),
                     'rlc_delay_min': (0, 100000000),
                     'rlc_delay_max': (0, 100000000),

                     'pdcp_tx_pkt': (0, 1),
                     'pdcp_tx_data': (0, 1),
                     'pdcp_rx_pkt': (0, 1),
                     'pdcp_rx_data': (0, 1),

                     'pdcp_delay_mean': (0, 100000000),
                     'pdcp_delay_stdev': (0, 100000000),
                     'pdcp_delay_min': (0, 100000000),
                     'pdcp_delay_max': (0, 100000000),

                     'app_tx_pkt': (0, 1),
                     'app_tx_data': (0, 1),
                     'app_rx_pkt': (0, 1),
                     'app_rx_data': (0, 1),

                     'app_delay_mean': (0, 100000000),
                     'app_delay_stdev': (0, 100000000),
                     'app_delay_min': (0, 100000000),
                     'app_delay_max': (0, 100000000)
                     }

state_labels = [
    'MCS',
    'Symbols',
    'SINR',
    'Mean delay (PDCP) [ms]',
    'Stdev delay (PDCP) [ms]',
    'Min delay (PDCP) [ms]',
    'Max delay (PDCP) [ms]',
    'Mean delay (App) [ms]',
    'Stdev delay (App) [ms]',
    'Min delay (App) [ms]',
    'Max delay (App) [ms]',
    'PRR (PDCP)',
    'PRR (App)']

state_normalization = [
    (0, 28),
    (0, 12),
    (0, 60),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 100),
    (0, 1),
    (0, 1)]

state_features = ['mcs',
                  'symbols',
                  'sinr',
                  'pdcp_delay_mean',
                  'pdcp_delay_stdev',
                  'pdcp_delay_min',
                  'pdcp_delay_max',
                  'app_delay_mean',
                  'app_delay_stdev',
                  'app_delay_min',
                  'app_delay_max']

combination_features = [
    ('pdcp_rx_data', 'pdcp_tx_data'),
    ('app_rx_data', 'app_tx_data')]

state_dim = len(state_features) + len(combination_features)

state_mask = np.array([True] * 7 + [False] * 4 + [True] + [False])

app_pdr_features = [('app_rx_data',
                     'app_tx_data')]

assert len(state_labels) == len(state_features) + len(combination_features)

state_feature_normalization = [env_normalization[feature] for feature in state_features]

combination_feature_normalization = [(0, 1), (0, 1)]

state_feature_indexes = []

for feature in state_features:
    state_feature_indexes.append(env_features.index(feature))

combination_feature_indexes = []

for num, den in combination_features:
    combination_feature_indexes.append((env_features.index(num), env_features.index(den)))

app_pdr_indexes = []

for num, den in app_pdr_features:
    app_pdr_indexes.append((env_features.index(num), env_features.index(den)))

app_delay_max_index = env_features.index('app_delay_max')
app_delay_mean_index = env_features.index('app_delay_mean')
teleoperated_delay_requirement = 50000000  # [ns]  for tele-operated driving applications
mapsharing_delay_requirement = 50000000  # [ns]  for tele-operated driving applications
