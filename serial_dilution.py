#!/usr/bin/env python3

"""\
Usage:
    serial_dilution.py <volume> <high> <low> <steps> [options]

Options:
    -v --verbose
        Print out the concentration for each step of the dilution.
"""

if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)
    volume = eval(args['<volume>'])
    high = eval(args['<high>'])
    low = eval(args['<low>'])
    steps = eval(args['<steps>'])

    dilution = (low / high)**(1 / (steps - 1))
    transfer = volume * dilution / (1 - dilution)
    initial_volume = volume + transfer

    print("""\
1. Put {initial_volume:.2f} μL material in the first tube.
2. Add {volume:.2f} μL water in the remaining tubes.
3. Perform a serial dilution, transferring {transfer:.2f} μL
   each time.
""".format(**locals()))
    
    if args['--verbose']:
        from tabulate import tabulate
        print('Final concentrations:')
        print(tabulate([
            [i+1, high * dilution**i]
            for i in range(steps)
        ], tablefmt='plain', floatfmt='.2e'))

# vim: tw=53
