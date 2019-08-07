from sys import stdout, stderr, stdin
from pickle import dumps, loads
from random import choice, random
from string import ascii_lowercase

from numpy import arange, array, concatenate
import matplotlib.pyplot as plt

from .duration import Duration

def random_string(length=10):
    return ''.join(choice(ascii_lowercase) for i in range(length))

def write_results(results, output_file):
    output = dumps(results)
    if output_file:
        output_file.write(output)
    else:
        if stdout.isatty():
            notify("ERROR: Attempting to write binary results data to STDOUT")
        else:
            stdout.buffer.write(output)

def read_results(input_file):
    if input_file is None and stdin.isatty():
        return []
    return loads((input_file or stdin.buffer).read())

def write_plot(output_file):
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()

# 0.1,0.5,0.8,1.0,1.2 => array([0.1, 0.5, 0.8, 1.0, 1.2])
# [1,5,1] => array([1.0, 2.0, 3.0, 4.0])
# [0.1,1,0.3][1,5,1] => array([0.1, 0.4, 0.7, 1.0, 2.0, 3.0, 4.0])
def array_glob(spec):
    if spec.startswith('['):
        subarray_specs = spec[1:-1].split('][')
        values = array([])
        for subarray_spec in subarray_specs:
            start, stop, step = subarray_spec.split(',')
            values = concatenate((values, arange(float(start), float(stop), float(step))))
        return values
    else:
        return array([float(n) for n in spec.split(',')])

def notify(string):
    stderr.write(string)
    stderr.write("\n")
    stderr.flush()

def format_timestamp(timestamp):
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

DAY = 86400
HOUR = 3600
MINUTE = 60

def format_duration(total_seconds):
    if total_seconds > DAY:
        days = (total_seconds // DAY)
        return "{}d{}".format(days, format_duration(total_seconds - (days * DAY)))
    elif total_seconds > HOUR:
        hours = (total_seconds // HOUR)
        return "{}h{}".format(hours, format_duration(total_seconds - (hours * HOUR)))
    elif total_seconds > MINUTE:
        minutes = (total_seconds // MINUTE)
        return "{}m{}".format(minutes, format_duration(total_seconds - (minutes * MINUTE)))
    else:
        return "{}s".format(int(total_seconds))
