from os import environ
from sys import argv, stderr, stdout, stdin
from pickle import loads

import matplotlib.pyplot as plt
from numpy import array, mean, std

from simulations.earth_mars.single_run import *

def _show_populations(ax, population_distances, population_hashrate_ratios):
    show_populations = environ.get("POPULATIONS")
    if show_populations:
        ax.scatter(population_distances, population_hashrate_ratios, s=5, color='black', linewidths=0.01, alpha=0.25)

def plot_contour(distances, hashrate_ratios, mars_blocks_ratios):

    fig, (ax_means, ax_counts, ax_std_devs) = plt.subplots(nrows=3, sharex=True)
    fig.suptitle('Fraction Blocks Mined on Mars')

    population_distances = []
    population_hashrate_ratios = []
    for distance in distances:
        for hashrate_ratio in hashrate_ratios:
            population_distances.append(distance)
            population_hashrate_ratios.append(hashrate_ratio)

    mars_blocks_ratios_counts = []
    mars_blocks_ratios_means = []
    mars_blocks_ratios_std_devs = []
    for distance_index, distance in enumerate(distances):
        mars_blocks_ratios_counts_at_distance = []
        mars_blocks_ratios_means_at_distance = []
        mars_blocks_ratios_std_devs_at_distance = []
        for hashrate_ratio_index, hashrate_ratio in enumerate(hashrate_ratios):
            mars_blocks_ratios_at_distance_and_hashrate = mars_blocks_ratios[distance_index][hashrate_ratio_index]
            mars_blocks_ratios_counts_at_distance.append(len(mars_blocks_ratios_at_distance_and_hashrate))
            mars_blocks_ratios_means_at_distance.append(mars_blocks_ratios_at_distance_and_hashrate.mean())
            mars_blocks_ratios_std_devs_at_distance.append(mars_blocks_ratios_at_distance_and_hashrate.std())
        mars_blocks_ratios_counts.append(mars_blocks_ratios_counts_at_distance)
        mars_blocks_ratios_means.append(mars_blocks_ratios_means_at_distance)
        mars_blocks_ratios_std_devs.append(mars_blocks_ratios_std_devs_at_distance)
    mars_blocks_ratios_counts = array(mars_blocks_ratios_counts)
    mars_blocks_ratios_means = array(mars_blocks_ratios_means)
    mars_blocks_ratios_std_devs = array(mars_blocks_ratios_std_devs)

    ax_means.set_title("Mean")
    ax_means.set_ylabel('Earth/Mars Hashrate')
    means_mappable = ax_means.contourf(distances, hashrate_ratios, mars_blocks_ratios_means.transpose(), cmap="coolwarm")
    plt.colorbar(means_mappable, ax=ax_means)
    _show_populations(ax_means, population_distances, population_hashrate_ratios)

    ax_counts.set_title("Counts")
    ax_counts.set_ylabel('Earth/Mars Hashrate')
    ax_counts.set_xlabel("Seconds")
    counts_mappable = ax_counts.contourf(distances, hashrate_ratios, mars_blocks_ratios_counts.transpose(), cmap="Greys")
    plt.colorbar(counts_mappable, ax=ax_counts)
    _show_populations(ax_counts, population_distances, population_hashrate_ratios)

    ax_std_devs.set_title("Std. Deviation")
    ax_std_devs.set_ylabel('Earth/Mars Hashrate')
    ax_std_devs.set_xlabel("Seconds")
    std_devs_mappable = ax_std_devs.contourf(distances, hashrate_ratios, mars_blocks_ratios_std_devs.transpose(), cmap="Greys")
    plt.colorbar(std_devs_mappable, ax=ax_std_devs)
    _show_populations(ax_std_devs, population_distances, population_hashrate_ratios)

    plt.show()


if __name__ ==  '__main__':
    if len(argv) > 1:
        input_stream = open(argv[1], 'rb')
    else:
        input_stream = stdin.buffer
    results = loads(input_stream.read())
    plot_contour(*results)
