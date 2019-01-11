#!/usr/bin/env python3

"""\
Usage:
    ./phusion_master_mix.py <volume> [options]

Options:
    -x --extra [PERCENT]
        How much extra master mix to create.
"""

import docopt
import math

args = docopt.docopt(__doc__)
volume = eval(args['<volume>']) * (1 + float(args['--extra'] or 0) / 100)
scale = lambda ref, name: (ref * volume / 160, name)

reagents = [
        scale(107.2, "nuclease-free water"),
        scale( 32.0, "5x Phusion buffer"),
        scale(  3.2, "10 mM dNTP mix"),
        scale(  8.0, "10 mM primer mix"),
        scale(  8.0, "10 ng/μL template"),
        scale(  1.6, "2 U/μL Phusion polymerase"),
]

longest_amount = 0
total_amount = 0

for amount, reagent in reagents:
    longest_amount = max(longest_amount, int(math.ceil(math.log10(amount))))
    total_amount += amount

for amount, reagent in reagents:
    row = '{{:{}.1f}} μL  {{}}'.format(longest_amount + 2)
    print(row.format(amount, reagent))

print (30  *'-')
print(row.format(total_amount, 'total master mix'))
