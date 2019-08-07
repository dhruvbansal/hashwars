from datetime import datetime, timedelta
from asyncio import sleep
from adaptive import Learner2D, Runner

from .utils import notify, format_timestamp, format_duration

def single_static_binary_simulation(namespace, name, distance, hashrate_ratio, simulator_argv):
    simulator = getattr(namespace, name)
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    notify("SIMULATION: {}".format(name))
    notify("DISTANCE: {}".format(distance))
    notify("HASHRATE RATIO: {}".format(hashrate_ratio))
    notify("ARGV: {}".format(simulator_argv))
    return simulator((distance, hashrate_ratio, simulator_argv))
    
async def many_static_binary_simulations(namespace, name, distance_bounds, hashrate_ratio_bounds, error_rate):
    simulator = getattr(namespace, name)
    notify("SIMULATION: {}".format(name))
    notify("DISTANCES: {} - {}".format(distance_bounds[0], distance_bounds[-1]))
    notify("HASHRATE RATIOS: {} - {}".format(hashrate_ratio_bounds[0], hashrate_ratio_bounds[-1]))
    notify("ERROR: {}".format(error_rate))

    learner = Learner2D(simulator, bounds=[distance_bounds, hashrate_ratio_bounds])

    notify("Starting simulation at {}...".format(format_timestamp(datetime.now())))
    runner = Runner(learner, goal=lambda l: l.loss() < error_rate)
    while not runner.task.done():
        await sleep(5)
        fraction_done = (error_rate / learner.loss())
        fraction_remaining = 1 - fraction_done
        now = datetime.now()
        runtime = runner.elapsed_time()
        overhead = (runner.overhead() / runtime if runtime > 0 else 0)
        remaining_time = ((runtime * fraction_remaining) / fraction_done if fraction_done > 0 else 0)
        eta = now + timedelta(seconds=remaining_time)
        
        notify("STATUS: {} samples | {:0.4f}% done | {:0.2f}% overhead | {} runtime | {} remaining | {} ETA".format(
            len(learner.data), 
            100 * fraction_done,
            100 * overhead,
            format_duration(runtime),
            format_duration(remaining_time),
            format_timestamp(eta),
        ))

    results = learner.data.values()
    notify("SAMPLED: {}".format(len(results)))
    return list(results)
