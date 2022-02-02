import numpy as np
import seaborn as sns
import pandas as pd
import tikzplotlib
import matplotlib
matplotlib.use('Agg')
matplotlib.use('Agg')
matplotlib.rcParams['mathtext.fontset'] = 'stix'
matplotlib.rcParams['font.family'] = 'STIXGeneral'
matplotlib.rcParams['font.size'] = 12
import matplotlib.pyplot as plt
plt.title(r'ABC123 vs $\mathrm{ABC123}^{123}$')


def multi_histplot(distribution_data: [np.ndarray],
                   distribution_labels: [str],
                   distribution_legends: [str],
                   value_key: str,
                   label_key: str,
                   legend_key: str,
                   output_file: str,
                   palette=None,
                   lim=None,
                   plot_sizes=None,
                   plot_format='eps'
                   ):

    if plot_sizes is not None:
        fig = plt.figure(figsize=plot_sizes)
    else:
        fig = plt.figure()

    unique_labels = list(set(distribution_labels))

    if distribution_legends[0] is not None:

        unique_legends = list(set(distribution_legends))

        data_values = []
        data_labels = []

        for _ in unique_legends:
            data_values.append(np.array([], dtype=np.float32))
            data_labels.append([])

        if len(unique_legends) == 2:

            axes = [fig.add_subplot(211), fig.add_subplot(212)]

        elif len(unique_legends) == 3:

            axes = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223)]

        elif len(unique_legends) == 4:

            axes = [fig.add_subplot(221), fig.add_subplot(222), fig.add_subplot(223), fig.add_subplot(224)]

        else:
            raise ValueError

    else:

        unique_legends = None

        data_values = np.array([], dtype=np.float32)

        data_labels = []

        axes = [fig.add_subplot(111)]

    value_num = len(distribution_data[0])

    for values, label, legend in zip(distribution_data, distribution_labels, distribution_legends):

        if legend is None:

            data_values = np.concatenate((data_values, values))

            data_values = np.around(data_values, decimals=4)

            data_labels += [label] * value_num

        else:

            legend_idx = unique_legends.index(legend)

            data_values[legend_idx] = np.concatenate((data_values[legend_idx], values))

            data_values[legend_idx] = np.around(data_values[legend_idx], decimals=4)

            data_labels[legend_idx] += [label] * value_num

    for legend, ax in zip(unique_legends, axes):
        legend_idx = unique_legends.index(legend)

        data = pd.DataFrame({value_key: data_values[legend_idx], label_key: data_labels[legend_idx]})

        sns.histplot(data=data, ax=ax, multiple="stack", x=label_key, hue=value_key, shrink=.5, palette=palette)

        ax.grid(b=True, color='darkgrey', linestyle='-')
        ax.grid(b=True, which='minor', color='darkgrey', linestyle='-')

        ax.set_yticks([0, value_num / 4, value_num / 2, 3 * value_num / 4, value_num])
        ax.set_yticklabels([0, 25, 50, 75, 100])

        ax.set_ylabel('Percentage')

        if legend_idx == len(unique_legends)-1:

            ax.legend(handles=ax.legend_.legendHandles,
                      labels=[t.get_text() for t in ax.legend_.texts],
                      title=ax.legend_.get_title().get_text(),
                      ncol=len(unique_labels),
                      bbox_to_anchor=(0.5, -.15), loc='upper center')

        else:
            ax.get_legend().remove()

        ax.set_xlabel(None)

        if lim is not None:
            ax.set_ylim([lim[0], lim[1]])

        ax.set_title(legend_key + ' = ' + legend)

    plt.subplots_adjust(hspace=.4)

    plt.savefig(output_file.replace(" ", "_") + '.png', format='png', bbox_inches='tight')

    if plot_format == 'tex':
        tikzplotlib.save(output_file.replace(" ", "_") + '.tex')

    elif plot_format != 'png':
        plt.savefig(output_file.replace(" ", "_") + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()
