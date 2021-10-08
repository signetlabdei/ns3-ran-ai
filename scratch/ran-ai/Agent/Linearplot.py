# coding=utf-8
import numpy as np
import matplotlib

matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
matplotlib.rcParams['font.size'] = 12

import matplotlib.pyplot as plt

plt.title(r'ABC123 vs $\mathrm{ABC123}^{123}$')


def linear_plot(data: np.ndarray,
                x_range: int,
                y_label: str,
                x_label: str,
                plot_points: int,
                output_file: str,
                color='orangered',
                transparent_color='mistyrose',
                fill_between=True,
                y_limit=None,
                confidence='std',
                plot_format='png',
                plot_sizes=None,
                font_size=None):

    if font_size is not None:
        matplotlib.rcParams['font.size'] = font_size

    data_length = len(data)

    if plot_points > data_length:
        plot_points = data_length

    point_length = int(np.floor(data_length / plot_points))
    data = data[:point_length * plot_points]

    data = np.reshape(data, (plot_points, point_length))

    episode = (np.arange(1, plot_points + 1) * x_range / (plot_points + 1)).astype(int)

    data_avg = np.mean(data, axis=1)
    max_data = np.max(data)
    min_data = np.min(data)
    percentile_25 = np.percentile(data, 25, axis=1)
    percentile_75 = np.percentile(data, 75, axis=1)
    data_std = np.std(data, axis=1)

    upper_confidence = np.minimum(data_avg + data_std, max_data)
    lower_confidence = np.maximum(data_avg - data_std, min_data)

    if plot_sizes is not None:
        plt.figure(figsize=plot_sizes)
    else:
        plt.figure()

    if confidence == 'percent':

        plt.plot(episode, percentile_25, color=color)
        plt.plot(episode, percentile_75, color=color)
        if fill_between:
            plt.fill_between(episode, percentile_25, percentile_75, color=transparent_color)

        plt.plot(episode, data_avg, label='Mean', linewidth=0.8, marker='.', color=color)

    elif confidence == 'std':

        plt.plot(episode, upper_confidence, color=color)
        plt.plot(episode, lower_confidence, color=color)
        if fill_between:
            plt.fill_between(episode, lower_confidence, upper_confidence, color=transparent_color)
        plt.plot(episode, data_avg, label='Mean', linewidth=0.8, marker='.', color=color)

    else:

        plt.plot(episode, data_avg, label='Mean', linewidth=0.8, marker='.', color=color)

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    plt.xlim((episode[0], episode[-1]))

    if y_limit is not None:
        plt.ylim((y_limit[0], y_limit[1]))

    plt.grid()
    plt.legend()

    plt.savefig(output_file + '.png', bbox_inches='tight')

    if plot_format != 'png':
        plt.savefig(output_file + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()


def multi_linear_plot(multi_data: [np.ndarray],
                      data_keys: [str],
                      x_range: int,
                      y_label: str,
                      x_label: str,
                      plot_points: int,
                      output_file: str,
                      colors: [str] = None,
                      transparent_colors: [str] = None,
                      markers: [str] = None,
                      fill_between=True,
                      y_limit=None,
                      confidence='std',
                      plot_format='png',
                      plot_sizes=None,
                      font_size=None):

    if colors is None:
        colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
                  'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

    if transparent_colors is None:
        transparent_colors = ['lightcyan', 'linen', 'honeydew', 'mistyrose', 'thistle',
                              'seashell', 'lavenderblush', 'gainsboro', 'beige', 'aliceblue']

    if markers is None:
        markers = ['P', 'X', 'd', 'v', '1', 'D', 's', '*', '>', '<']

    if font_size is not None:
        matplotlib.rcParams['font.size'] = font_size

    for data_idx in range(len(multi_data)):

        data = multi_data[data_idx]
        data_length = len(data)
        if data_length < plot_points:
            plot_points = data_length

    episode = (np.arange(1, plot_points + 1) * x_range / (plot_points + 1)).astype(int)

    if plot_sizes is not None:
        plt.figure(figsize=plot_sizes)
    else:
        plt.figure()

    for data_idx in range(len(multi_data)):

        data = multi_data[data_idx]

        data_length = len(data)

        point_length = int(np.floor(data_length / plot_points))
        data = data[:point_length * plot_points]

        data = np.reshape(data, (plot_points, point_length))

        max_data = np.max(data)
        min_data = np.min(data)

        data_avg = np.mean(data, axis=1)
        percentile_25 = np.percentile(data, 25, axis=1)
        percentile_75 = np.percentile(data, 75, axis=1)
        data_std = np.std(data, axis=1)

        upper_confidence = np.minimum(data_avg + data_std, max_data)
        lower_confidence = np.maximum(data_avg - data_std, min_data)

        if confidence == 'percent':

            plt.plot(episode, percentile_25, color=colors[data_idx], zorder=1)
            plt.plot(episode, percentile_75, color=colors[data_idx], zorder=1)
            if fill_between:
                plt.fill_between(episode, percentile_25, percentile_75,
                                 color=transparent_colors[data_idx], zorder=0)
            plt.plot(episode, data_avg, label=data_keys[data_idx],
                     color=colors[data_idx], linewidth=0.8, marker=markers[data_idx], zorder=5)

        elif confidence == 'std':

            plt.plot(episode, upper_confidence, color=colors[data_idx], zorder=1)
            plt.plot(episode, lower_confidence, color=colors[data_idx], zorder=1)
            if fill_between:
                plt.fill_between(episode, lower_confidence, upper_confidence,
                                 color=transparent_colors[data_idx], zorder=0)

            plt.plot(episode, data_avg, label=data_keys[data_idx],
                     color=colors[data_idx], linewidth=0.8, marker=markers[data_idx], zorder=5)

        else:
            plt.plot(episode, data_avg, label=data_keys[data_idx],
                     color=colors[data_idx], linewidth=0.8, marker=markers[data_idx])

    plt.ylabel(y_label)
    plt.xlabel(x_label)

    plt.xlim((episode[0], episode[-1]))

    if y_limit is not None:
        plt.ylim((y_limit[0], y_limit[1]))

    plt.grid()
    plt.legend()

    plt.savefig(output_file + '.png', bbox_inches='tight')

    if plot_format != 'png':
        plt.savefig(output_file + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()
