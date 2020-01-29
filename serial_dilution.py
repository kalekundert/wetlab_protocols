#!/usr/bin/env python3

"""\
Perform a serial dilution.

Usage:
    serial_dilution.py <volume> <high> <low> <steps> [options]
"""

if __name__ == '__main__':
    import docopt
    import stepwise
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

- Put {initial_volume:.2f} μL material in the first tube.
- Add {volume:.2f} μL water in the remaining tubes.
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
