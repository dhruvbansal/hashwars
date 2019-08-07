from argparse import ArgumentParser

from numpy import nan, array, arange

import matplotlib.pyplot as plt

from hashwars import write_plot

_parser = ArgumentParser(description="Plots bitcoin money supply.")

def money_supply(results, output_file, argv):
    (
        heights,
        times,
        supplies,
        inflations,
    ) = results
    args = _parser.parse_args(argv)

    fig, ax1 = plt.subplots(nrows=1)
    ax1.set_title('Bitcoin Money Supply')
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total BTC Created')
    #ax1.set_yscale('log')
        
    supply_line = ax1.plot(times, supplies, label="Total BTC")

    ax2 = ax1.twinx()
    ax2.set_ylabel('Inflation/Block')
    inflation_line = ax2.plot(times, inflations, label="Inflation/Block", color='red')
    ax2.axhline(y=0)
    ax2.set_yscale('log')
    ax2.set_ylim((0, 50))

    ax3 = ax1.twiny()
    ax3.set_xlim((heights[0], heights[-1]))
    height_major_ticks = arange(0,7000000,1000000)
    height_minor_ticks = arange(0,7000000,100000)
    ax3.set_xticks(height_major_ticks)
    ax3.set_xticks(height_minor_ticks, minor=True)
    ax3.set_xticklabels(["{}M".format(tick//1000000) for tick in height_major_ticks])
    ax3.set_xlabel("Block")

    lines  = supply_line + inflation_line
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower center')

    write_plot(output_file)
