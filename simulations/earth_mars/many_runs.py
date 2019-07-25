from sys import argv, stderr, stdout
from pickle import dumps
from concurrent.futures import ProcessPoolExecutor
from random import shuffle

from math import ceil
from numpy import arange, array, concatenate

from simulations.earth_mars.single_run import *

# 0.1,0.4,0.5,0.8,1.0,2.0,3.0,4.0
#
# [0.1,4.0,0.1]
def _parse_array(spec):
    if spec.startswith('['):
        subarray_specs = spec[1:-1].split('][')
        values = array([])
        for subarray_spec in subarray_specs:
            start, stop, step = subarray_spec.split(',')
            values = concatenate((values, arange(float(start), float(stop), float(step))))
        return values
    else:
        return array([float(n) for n in spec.split(',')])

def _single_run(hours, distance, hashrate_ratio):
    (distance,
    mars_miners,
    earth_miners,
    times, 
    mars_miners_mars_blocks,
    mars_miners_earth_blocks,
    earth_miners_mars_blocks,
    earth_miners_earth_blocks) = single_run(hours, distance, hashrate_ratio)
    mars_blocks_ratio = mars_miners_mars_blocks[-1]/(mars_miners_mars_blocks[-1]+mars_miners_earth_blocks[-1])
    return mars_blocks_ratio

def _single_population(params):
    hours, distance, hashrate_ratio, sample_size, relative_error, max_runs = params
    hours = int(hours)
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    sample_size = int(sample_size)
    relative_error = float(relative_error)
    max_runs = int(max_runs)

    n = sample_size
    sample = array([_single_run(hours, distance, hashrate_ratio) for sample_trial in range(int(sample_size))])
    miu = sample.mean()
    sigma = sample.std()

    W = abs(relative_error * miu)
    if W > 0:
        N = ceil(16 * (pow(sigma, 2) / pow(W, 2))) # https://en.wikipedia.org/wiki/Sample_size_determination
    else: 
        N = 1
    if N > max_runs:
        N = max_runs
    if N < sample_size:
        N = sample_size
    population = array([_single_run(hours, distance, hashrate_ratio) for trial in range(N)])
    Miu = population.mean()
    Sigma = population.std()
    
    stderr.write("L={} D={:0.0f} HR={:0.4f} => {} {:0.4f} ERROR {:0.4f}\n".format(
        hours, distance, hashrate_ratio,
        N, Miu,
        abs(Sigma - sigma)/Sigma if Sigma != 0 else 0.0,
    )); stderr.flush()
    return (distance, hashrate_ratio, concatenate((population, sample)))
    
def many_runs(hours, sample_size, relative_error, max_runs, distances, hashrate_ratios):
    stderr.write("HOURS: {}\n".format(hours))
    stderr.write("SAMPLE SIZE: {} RELATIVE ERROR: {} MAX RUNS: {}\n".format(sample_size, relative_error, max_runs))
    stderr.write("DISTANCES: {} - {} ({} total)\n".format(distances[0], distances[-1], len(distances)))
    stderr.write("HASHRATE RATIOS: {} - {} ({} total)\n".format(hashrate_ratios[0], hashrate_ratios[-1], len(hashrate_ratios)))
    stderr.flush()
    populations = []
    for distance in distances:
        for hashrate_ratio in hashrate_ratios:
            populations.append((hours, distance, hashrate_ratio, sample_size, relative_error, max_runs))
    stderr.write("POPULATIONS: {}\n".format(len(populations))); stderr.flush()
    stderr.write("Randomizing populations...\n")
    shuffle(populations)
    stderr.write("Opening process pool executor...\n"); stderr.flush()

    with ProcessPoolExecutor() as executor:
        results = list(executor.map(_single_population, populations))
        stderr.write("Obtained results...\n"); stderr.flush()
        mars_blocks_ratios = []
        for distance in distances:
            mars_blocks_ratios_at_distance = []
            results_at_distance = [result for result in results if result[0] == distance]
            for hashrate_ratio in hashrate_ratios:
                mars_blocks_ratios_at_distance_and_hashrate_ratio = [result for result in results_at_distance if result[1] == hashrate_ratio][0][2]
                mars_blocks_ratios_at_distance.append(mars_blocks_ratios_at_distance_and_hashrate_ratio)
            mars_blocks_ratios.append(mars_blocks_ratios_at_distance)
        stderr.write("Collated results...\n"); stderr.flush()
        return (distances, hashrate_ratios, mars_blocks_ratios)

if __name__ == '__main__':
    if len(argv) < 7:
        stderr.write("usage: many_runs.py HOURS SAMPLE_SIZE RELATIVE_ERROR MAX_RUNS DISTANCES HASHRATE_RATIOS [OUTPUT_PATH]\n")
        exit(1)
    hours, sample_size, relative_error, max_runs, distances, hashrate_ratios = argv[1:7]
    results = many_runs(int(hours), int(sample_size), float(relative_error), int(max_runs), _parse_array(distances), _parse_array(hashrate_ratios))
    output = dumps(results)

    if len(argv) > 7:
        with open(argv[7], 'wb') as f:
            f.write(output)
    else:
        stdout.buffer.write(output)
