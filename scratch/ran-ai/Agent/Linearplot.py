# coding=utf-8
import numpy as np
import pandas as pd
import seaborn as sns
import tikzplotlib
import matplotlib.pyplot as plt


def linear_plot(distribution_data: np.ndarray,
                      x_label: str,
                      y_label: str,
                      max_time: int,
                      output_file: str,
                      distribution_color: [str] = None,
                      lim: [] = None,
                      plot_format='eps',
                      plot_sizes=None):

    if distribution_color is not None:
        sns.color_palette(distribution_color)

    if plot_sizes is not None:
        fig = plt.figure(figsize=plot_sizes)
    else:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    data_values = np.array(distribution_data, dtype=np.float32)

    value_num = len(data_values)

    discarded_value_num = value_num % 100

    value_num -= discarded_value_num

    data_values = data_values[:value_num]

    data_times = (np.arange(0, value_num) * 100 / value_num).astype(np.int) * max_time / 100

    data_times += + 1

    data = pd.DataFrame({'Value': data_values, 'Time': data_times})

    sns.lineplot(data=data, ax=ax, x='Time', y='Value', markers=True, dashes=False, ci=None)

    ax.grid(b=True, color='darkgrey', linestyle='-')
    ax.grid(b=True, which='minor', color='darkgrey', linestyle='-')

    ax.set_xlabel(x_label)

    ax.set_ylabel(y_label)

    if lim is not None:
        ax.set_ylim([lim[0], lim[1]])

    plt.savefig(output_file.replace(" ", "_") + '.png', bbox_inches='tight')
    tikzplotlib.save(output_file.replace(" ", "_") + '.tex')

    if plot_format != 'png':
        plt.savefig(output_file.replace(" ", "_") + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()


def multi_linear_plot(distribution_data: [np.ndarray],
                      distribution_labels: [str],
                      x_label: str,
                      y_label: str,
                      max_time: int,
                      output_file: str,
                      distribution_color: [str] = None,
                      lim: [] = None,
                      plot_format='eps',
                      plot_sizes=None):

    if distribution_color is not None:
        sns.color_palette(distribution_color)

    if plot_sizes is not None:
        fig = plt.figure(figsize=plot_sizes)
    else:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    data_values = np.array([], dtype=np.float32)

    data_labels = []

    data_times = np.array([], dtype=np.int)

    for values, label in zip(distribution_data, distribution_labels):

        value_num = len(values)

        discarded_value_num = value_num % 100

        value_num -= discarded_value_num

        values = values[:value_num]

        data_values = np.concatenate((data_values, values))

        data_labels += [str(label)] * value_num

        times = (np.arange(0, value_num) * 100 / value_num).astype(np.int) * max_time / 100

        times += 1

        data_times = np.concatenate((data_times, times))

    data = pd.DataFrame({'Value': data_values, 'Label': data_labels, 'Time': data_times})

    plot = sns.lineplot(data=data, ax=ax, x='Time', y='Value', hue='Label', markers=True, dashes=False, ci=None)


    ax.grid(b=True, color='darkgrey', linestyle='-')
    ax.grid(b=True, which='minor', color='darkgrey', linestyle='-')

    plot.legend_.set_title(None)

    ax.set_xlabel(x_label)

    ax.set_ylabel(y_label)

    if lim is not None:
        ax.set_ylim([lim[0], lim[1]])

    plt.savefig(output_file.replace(" ", "_") + '.png', bbox_inches='tight')
    tikzplotlib.save(output_file.replace(" ", "_") + '.tex')

    if plot_format != 'png':
        plt.savefig(output_file.replace(" ", "_") + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()
