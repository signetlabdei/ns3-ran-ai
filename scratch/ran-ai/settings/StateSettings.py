import numpy as np

env_normalization = {'IMSI': None,
                     'MCS': (0, 25),
                     'OFDM symbols': (8, 12),
                     'SINR [dB]': (0, 40),

                     'RLC tx pckts': (0, 1),
                     'RLC tx bytes': (0, 1),
                     'RLC rx pckts': (0, 1),
                     'RLC rx bytes': (0, 1),

                     'RLC avg delay': (0, 100000000),
                     'RLC std delay': (0, 100000000),
                     'RLC min delay': (0, 100000000),
                     'RLC max delay': (0, 100000000),

                     'PDCP tx pckts': (0, 1),
                     'PDCP tx bytes': (0, 1),
                     'PDCP rx pckts': (0, 1),
                     'PDCP rx bytes': (0, 1),

                     'PDCP avg delay': (0, 100000000),
                     'PDCP std delay': (0, 100000000),
                     'PDCP min delay': (0, 100000000),
                     'PDCP max delay': (0, 100000000),

                     'APP tx pckts': (0, 1),
                     'APP tx bytes': (0, 1),
                     'APP rx pckts': (0, 1),
                     'APP rx bytes': (0, 1),

                     'APP avg delay': (0, 100000000),
                     'APP std delay': (0, 100000000),
                     'APP min delay': (0, 100000000),
                     'APP max delay': (0, 100000000)
                     }

env_features = list(env_normalization.keys())

state_normalization = [
    (0, 25),
    (8, 12),
    (0, 40),
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

state_features = ['MCS',
                  'OFDM symbols',
                  'SINR [dB]',
                  'PDCP avg delay',
                  'PDCP std delay',
                  'PDCP min delay',
                  'PDCP max delay',
                  'APP avg delay',
                  'APP std delay',
                  'APP min delay',
                  'APP max delay']

combination_features = [
    ('PDCP rx bytes', 'PDCP tx bytes'),
    ('APP rx bytes', 'APP tx bytes')]

state_full_labels = [
    'MCS',
    'OFDM Symbols',
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

state_labels = [
    'MCS',
    'OFDM Symbols',
    'SINR',
    'Mean delay [ms]',
    'Stdev delay [ms]',
    'Min delay [ms]',
    'Max delay [ms]',
    'Mean delay [ms]',
    'Stdev delay [ms]',
    'Min delay [ms]',
    'Max delay [ms]',
    'PRR',
    'PRR']

state_dim = len(state_features) + len(combination_features)

state_mask = np.array([True] * 7 + [False] * 4 + [True] + [False])

app_pdr_labels = [('APP rx bytes', 'APP tx bytes')]

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

for num, den in app_pdr_labels:
    app_pdr_indexes.append((env_features.index(num), env_features.index(den)))

app_max_delay_label = 'APP max delay'
app_mean_delay_label = 'APP avg delay'

app_max_delay_index = env_features.index(app_max_delay_label)
app_mean_delay_index = env_features.index(app_mean_delay_label)
