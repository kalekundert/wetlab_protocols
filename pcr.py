#!/usr/bin/env python3

"""\
Usage:
    pcr.py <num_reactions> [options]

Options:
    -t --annealing-temp <celsius>   [default: 62]
        The annealing temperature for the PCR reaction.  I typically use NEB's 
        online "Tm Calculator" to determine this parameter.

    -x --extension-time <secs>      [default: 120]
        The length of the annealing step in seconds.  The rule of thumb is 30 
        sec/kb, perhaps longer if you're amplifying a whole plasmid.

    -v --reaction-volume <μL>       [default: 25]
        The volume of the PCR reaction.  The recommended volumes for Q5 are 25
        and 50 μL.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)

pcr = dirty_water.Pcr()
pcr.num_reactions = eval(args['<num_reactions>'])
pcr.annealing_temp = int(args['--annealing-temp'])
pcr.extension_time = int(args['--extension-time'])
pcr.reaction.volume = float(args['--reaction-volume'])
pcr.make_primer_mix = True

print(pcr)
