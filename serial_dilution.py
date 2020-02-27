#!/usr/bin/env python3

"""\
Perform a serial dilution.

Usage:
    serial_dilution.py <volume> <high> <low> <steps> [options]

Options:
    -d --diluent NAME   [default: water]
        The substance to dilute into.

    -m --material NAME  [default: material]
        The substance being diluted.
"""

import docopt
import stepwise
from inform import plural
from tabulate import tabulate

args = docopt.docopt(__doc__)
volume = eval(args['<volume>'])
high = eval(args['<high>'])
low = eval(args['<low>'])
steps = eval(args['<steps>'])

dilution = (low / high)**(1 / (steps - 1))
transfer = volume * dilution / (1 - dilution)
initial_volume = volume + transfer

protocol = stepwise.Protocol()
protocol += f"""\
Perform a serial dilution [1]:

- Put {initial_volume:.2f} μL {args['--material']} in the first tube.
- Add {volume:.2f} μL {args['--diluent']} in the {plural(steps):# remaining tube/s}.
- Transfer {transfer:.2f} μL between each tube.
"""
protocol.footnotes[1] = f"""\
The final concentrations will be:
{tabulate(
    [[i+1, high * dilution**i] for i in range(steps)],
    tablefmt='plain',
    floatfmt='.2e',
)}
"""
print(protocol)

# vim: tw=53
