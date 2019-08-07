from argparse import ArgumentParser

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from numpy import mean, std, where, full, array, percentile, arange, sqrt
from scipy.stats import binned_statistic
from scipy.interpolate import griddata

from hashwars import write_plot, array_glob

_DEFAULT_WIDTH = 8
_DEFAULT_HEIGHT = 6
_DEFAULT_DPI = 100

_parser = ArgumentParser(description="Plot of the hashrate/distance landscape.")
_parser.add_argument("-n", "--counts", action='store_true', help="show distribution of sampling counts")
_parser.add_argument("-s", "--stds", action='store_true', help="show distribution of standard deviations")
_parser.add_argument("-w", "--percentile-width", help="use this bin percentile width", metavar="PERCENT", type=float)
_parser.add_argument("-d", "--min-distance", help="ignore points closer than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-D", "--max-distance", help="ignore points further than this distance", metavar="DISTANCE", type=float)
_parser.add_argument("-r", "--min-ratio", help="ignore points with less than this ratio", metavar="RATIO", type=float)
_parser.add_argument("-R", "--max-ratio", help="ignore points with more than this ratio", metavar="RATIO", type=float)
_parser.add_argument("-l", "--levels", help="use this count or these explicit levels", metavar="COUNT|ARRAY", type=array_glob)
_parser.add_argument("-X", "--figure-width", help="figure width in inches", metavar="WIDTH", type=float, default=_DEFAULT_WIDTH)
_parser.add_argument("-Y", "--figure-height", help="figure height in inches", metavar="HEIGHT", type=float, default=_DEFAULT_HEIGHT)
_parser.add_argument("-Z", "--resolution", help="resolution in DPI", metavar="DPI", type=float, default=_DEFAULT_DPI)

def _format_percent(value, index):
    return '{:,.0%}'.format(value)

def hash_horizon(all_results, output_file, argv):

    args = _parser.parse_args(argv)

    distances = []
    hashrate_ratios = []
    weights = []

    for result in all_results:
        distance, hashrate_ratio, weight = result
        if args.min_distance and distance < args.min_distance: continue
        if args.max_distance and distance > args.max_distance: continue
        if args.min_ratio and hashrate_ratio < args.min_ratio: continue
        if args.max_ratio and hashrate_ratio > args.max_ratio: continue
        distances.append(distance)
        hashrate_ratios.append(hashrate_ratio)
        weights.append(weight)
        
    distances = array(distances)
    hashrate_ratios = array(hashrate_ratios)
    points = array(list(zip(distances, hashrate_ratios)))

    print("Distances", distances.shape)
    print("Hashrate Ratios", hashrate_ratios.shape)

    distance_percentiles = arange(0.0, 100.0, args.percentile_width if args.percentile_width else 100/sqrt(len(distances)))
    hashrate_ratio_percentiles = arange(0.0, 100.0, args.percentile_width if args.percentile_width else 100/sqrt(len(hashrate_ratios)))

    distance_bins_lower_limits = percentile(distances, distance_percentiles)
    hashrate_ratio_bins_lower_limits = percentile(hashrate_ratios, hashrate_ratio_percentiles)

    print("Distance Bins", distance_bins_lower_limits.shape, distance_bins_lower_limits)
    print("Hashrate Ratio Bins", hashrate_ratio_bins_lower_limits.shape, hashrate_ratio_bins_lower_limits)


    values = griddata(points, weights, (distance_bins_lower_limits, hashrate_ratio_bins_lower_limits))

    # values = [
    #     [[] for hashrate_ratio_bin_lower_limit in hashrate_ratio_bins_lower_limits] 
    #     for distance_bin_lower_limit in distance_bins_lower_limits]

    # for result in results:
    #     distance, hashrate_ratio, weight = result
        
    #     for distance_bin_index, distance_bin_lower_limit in enumerate(distance_bins_lower_limits):
    #         if distance < distance_bin_lower_limit: break
    #         for hashrate_ratio_bin_index, hashrate_ratio_bin_lower_limit in enumerate(hashrate_ratio_bins_lower_limits):
    #             if hashrate_ratio < hashrate_ratio_bin_lower_limit: break
    #     values[distance_bin_index][hashrate_ratio_bin_index].append(weight)

    nrows = 1
    if args.counts: nrows +=1 
    if args.stds: nrows += 1

    fig, axes = plt.subplots(
        figsize=(args.figure_width, args.figure_height),
        dpi=args.resolution,
        nrows=nrows,
        sharex=True)

    if args.levels is not None:
        levels = (args.levels if len(args.levels) > 1 else int(args.levels[0]))
    else:
        levels = int(sqrt(len(all_results)))
        
    print("LEVELS", levels)

    # means = array([
    #     [
    #         array(values[distance_bin_index][hashrate_ratio_bin_index]).mean()
    #         for hashrate_ratio_bin_index, hashrate_ratio_bin_lower_limit in enumerate(hashrate_ratio_bins_lower_limits)
    #     ]
    #     for distance_bin_index, distance_bin_lower_limit in enumerate(distance_bins_lower_limits)
    # ])

    print("distance_bins_lower_limits", distance_bins_lower_limits.shape)
    print("1/hashrate_ratio_bins_lower_limits", (1/hashrate_ratio_bins_lower_limits).shape)
    print("values", values.transpose().shape)

    ax_means = (axes if nrows == 1 else axes[0])
    title = 'Fraction blockchain weight mined by minority'
    ylabel = 'Minority Hashrate Fraction'
    xlabel = 'Minority Distance (light seconds)'
    if nrows == 1:
        ax_means.set_title(title)
    else:
        fig.suptitle(title)
        ax_means.set_title("Mean")

    ax_means.set_ylabel(ylabel)
    means_landscape = ax_means.tricontourf(
        distances, 
        1/hashrate_ratios, 
        weights,
        levels=levels,
        cmap="coolwarm")
    means_colorbar = plt.colorbar(means_landscape, ax=ax_means, format=ticker.FuncFormatter(_format_percent))
    ax_means.set_yticklabels(['{:,.0%}'.format(y) for y in ax_means.get_yticks()])
    if nrows == 1:
        ax_means.set_xlabel(xlabel)

    if args.stds:
        stds = array([
            [
                array(values[distance_bin_index][hashrate_ratio_bin_index]).std()
                for hashrate_ratio_bin_index, hashrate_ratio_bin_lower_limit in enumerate(hashrate_ratio_bins_lower_limits)
            ]
            for distance_bin_index, distance_bin_lower_limit in enumerate(distance_bins_lower_limits)
        ])

        ax_stds = axes[1]
        ax_stds.set_title("Standard Deviation")
        ax_stds.set_ylabel(ylabel)
        stds_landscape = ax_stds.tricontourf(
            distance_bins_lower_limits, 
            1/hashrate_ratio_bins_lower_limits, 
            stds.transpose(),
            levels,
            cmap="Greys")
        stds_colorbar = plt.colorbar(stds_landscape, ax=ax_stds)
        ax_stds.set_yticklabels(['{:,.0%}'.format(y) for y in ax_stds.get_yticks()])
        if nrows == 2:
            ax_stds.set_xlabel(xlabel)

    if args.counts:

        counts = array([
            [
                len(values[distance_bin_index][hashrate_ratio_bin_index])
                for hashrate_ratio_bin_index, hashrate_ratio_bin_lower_limit in enumerate(hashrate_ratio_bins_lower_limits)
            ]
            for distance_bin_index, distance_bin_lower_limit in enumerate(distance_bins_lower_limits)
        ])

        ax_counts = axes[2]
        ax_counts.set_title("Samples")
        ax_counts.set_ylabel(ylabel)
        counts_landscape = ax_counts.tricontourf(
            distance_bins_lower_limits, 
            1/hashrate_ratio_bins_lower_limits, 
            counts.transpose(),
            levels,
            cmap="Greys")
        counts_colorbar = plt.colorbar(counts_landscape, ax=ax_counts)
        ax_counts.set_yticklabels(['{:,.0%}'.format(y) for y in ax_counts.get_yticks()])
        ax_counts.set_xlabel(xlabel)

    write_plot(output_file)
