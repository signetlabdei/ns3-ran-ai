import numpy as np
import matplotlib
import seaborn as sns
import pandas as pd
import tikzplotlib
import matplotlib.pyplot as plt


def multi_histplot(distribution_data: [np.ndarray],
                   distribution_labels: [str],
                   y_label: str,
                   output_file: str,
                   distribution_color=None,
                   lim=None,
                   plot_sizes=None,
                   plot_format='eps'
                   ):

    if distribution_color is not None:
        sns.color_palette(distribution_color)

    if plot_sizes is not None:
        fig = plt.figure(figsize=plot_sizes)
    else:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    data_values = np.array([], dtype=np.float32)

    data_labels = []

    for values, label in zip(distribution_data, distribution_labels):

        value_num = len(values)

        data_values = np.concatenate((data_values, values.astype(np.int)))

        data_labels += [str(label)] * value_num

    data = pd.DataFrame({y_label: data_values, 'Label': data_labels})

    sns.histplot(data=data, ax=ax, multiple="stack", x='Label', hue=y_label, shrink=.5, stat='count')

    sns.move_legend(ax, "upper left")

    ax.grid(b=True, color='darkgrey', linestyle='-')
    ax.grid(b=True, which='minor', color='darkgrey', linestyle='-')

    ax.set_yticks([0, value_num / 4, value_num / 2, 3 * value_num / 4, value_num])
    ax.set_yticklabels([0, 25, 50, 75, 100])

    ax.set_ylabel('Percentage')
    ax.set_xlabel(None)

    if lim is not None:
        ax.set_ylim([lim[0], lim[1]])

    plt.savefig(output_file.replace(" ", "_") + '.png', format='png', bbox_inches='tight')
    tikzplotlib.save(output_file.replace(" ", "_") + '.tex')

    if plot_format != 'png':
        plt.savefig(output_file.replace(" ", "_") + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()
