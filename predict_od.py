#!/usr/bin/env python3

"""\
Predict how long it will take a culture to reach a certain OD.  The time 
estimate is updated as new (time, OD600) data points are collected.

Usage:
    predict_od.py start <target_od>
    predict_od.py update <time> <od> [options]
    predict_od.py show [options]
    predict_od.py <input_yml> [options]

Subcommands:
    start:
        Start keeping track of a new culture.  Subsequent calls to "update" 
        will update the time estimate for this culture.  Data recorded in 
        previous calls to "update" is forgotten.

    update:
        Record a new (time, OD600) data point for the current culture and 
        re-estimate how long it will take the culture to reach the target OD.

    show:
        Predict when the current culture will reach its target OD, without 
        recording any new data points.

Options:
    -v --visualize
        Plot the expected OD600 vs time.
"""

import os
import numpy as np

# The central data structure in this script is a dictionary called "params".  
# This dictionary is expected to have two keys:
#
# - target: The OD the user wants to get to.
# - time_vs_od: A list of (time, OD600) data points.  Times are represented as 
#   strings and are converted to numbers internally as necessary.  OD600s are 
#   represented as floats.

def params_from_yaml(yml_path):
    import yaml

    with open(yml_path) as yml_file:
        params = yaml.load(yml_file)

    if 'target' not in params:
        raise ValueError("'{}' does not have 'target' field.".format(yml_path))
    if 'time_vs_od' not in params:
        raise ValueError("'{}' does not have 'time_vs_od' field.".format(yml_path))

    return params

def params_to_yaml(params, yml_path):
    import yaml

    yml_dir = os.path.dirname(yml_path)
    if not os.path.exists(yml_dir):
        os.makedirs(yml_dir)

    with open(yml_path, 'w') as yml_file:
        return yaml.dump(params, yml_file)


def current_params_path():
    from appdirs import user_data_dir
    return os.path.join(user_data_dir('predict_od'), 'current_culture.yml')

def load_current_params():
    try:
        return params_from_yaml(current_params_path())
    except FileNotFoundError:
        return {}

def set_current_params(params):
    params_to_yaml(params, current_params_path())

def reset_current_params():
    update_current_params({})

def time_vs_od_from_params(params):
    times = [str_to_minutes(x[0]) for x in params['time_vs_od']]
    ods = [float(x[1]) for x in params['time_vs_od']]
    return times, ods


def minutes_to_str(minutes):
    return '{}h{:02d}'.format(int(minutes//60), int(minutes % 60))

def str_to_minutes(str):
    import re

    parsed_time = re.match('(\d+)h(\d+)?|(\d+)m', str)
    if not parsed_time:
        raise ValueError("can't interpret '{}' as a time.".format(str))

    hours = parsed_time.group(1) or 0
    minutes = parsed_time.group(2) or parsed_time.group(3) or 0

    return 60 * int(hours) + int(minutes)


def growth_curve(t, *fit):
    return fit[0] * np.exp(fit[1] * t)

def fit_growth_curve(params):
    from scipy.optimize import curve_fit
    times, ods = time_vs_od_from_params(params)
    initial_guess = 0.02267968, 0.02818784

    if len(times) == 0:
        return initial_guess

    elif len(times) == 1:
        times = [0] + times
        ods = [initial_guess[0]] + ods

    return curve_fit(growth_curve, times, ods, p0=initial_guess)[0]

def time_estimate(od, fit):
    return np.log(od/fit[0] + 1) / fit[1]

def print_time_estimate(params, fit):
    print("OD={} at {}".format(
        params['target'],
        minutes_to_str(time_estimate(params['target'], fit)),
    ))

def plot_growth_curve(params, fit):
    import matplotlib.pyplot as plt

    target_od = params['target']
    known_times, known_ods = time_vs_od_from_params(params)
    max_time = 1.1 * time_estimate(target_od, fit)
    fit_times = np.linspace(0, max_time)
    fit_ods = growth_curve(fit_times, *fit)

    plt.plot(known_times, known_ods, 'ko', fillstyle='none')
    plt.plot(fit_times, fit_ods, 'k-')
    plt.plot(fit_times, [target_od] * len(fit_times), '--', color='grey')
    plt.xlim(0, max_time)
    plt.xlabel('Time (min)')
    plt.ylabel('OD600')
    plt.show()


if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)
    params = None

    # Figure out which command the user called and do the basic action.

    if args['start']:
        set_current_params({
            'target': float(args['<target_od>']),
            'time_vs_od': [],
        })

    elif args['update']:
        params = load_current_params()
        params['time_vs_od'].append((
            [args['<time>'], float(args['<od>'])]
        ))
        set_current_params(params)

    elif args['show']:
        params = load_current_params()
        
    else:
        params = params_from_yaml(args['<input_yml>'])

    # Make a time estimate if we have new parameters to work with.

    if params is not None:
        fit = fit_growth_curve(params)
        print_time_estimate(params, fit)

        if args['--visualize']:
            plot_growth_curve(params, fit)

