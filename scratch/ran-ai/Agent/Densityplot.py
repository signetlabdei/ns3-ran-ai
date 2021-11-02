import numpy as np
import matplotlib
import seaborn as sns
import pandas as pd
import tikzplotlib
import matplotlib.pyplot as plt


def multi_density_plot(distribution_data: [np.ndarray],
                       distribution_labels: [str],
                       x_label: str,
                       output_file: str,
                       distribution_color=None,
                       lim=None,
                       plot_sizes=None,
                       plot_format='eps'
                       ):
    """

    """

    if distribution_color is not None:
        sns.color_palette(distribution_color)

    if plot_sizes is not None:
        fig = plt.figure(figsize=plot_sizes)
    else:
        fig = plt.figure()

    ax = fig.add_subplot(111)

    data = pd.DataFrame(data=np.asarray(distribution_data).T, columns=distribution_labels)

    sns.kdeplot(data=data, fill=True, common_grid=True, ax=ax, shade=True, legend=True)

    ax.grid(b=True, color='darkgrey', linestyle='-')
    ax.grid(b=True, which='minor', color='darkgrey', linestyle='-')

    ax.set_xlabel(x_label)

    if lim is not None:
        ax.set_xlim([lim[0], lim[1]])

    plt.savefig(output_file.replace(" ", "_") + '.png', format='png', bbox_inches='tight')
    tikzplotlib.save(output_file.replace(" ", "_") + '.tex')

    if plot_format != 'png':
        plt.savefig(output_file.replace(" ", "_") + '.' + plot_format, format=plot_format, bbox_inches='tight')

    plt.close()
