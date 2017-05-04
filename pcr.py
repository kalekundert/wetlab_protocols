#!/usr/bin/env python3

"""\
Usage:
    pcr.py <num_reactions> <annealing_temp> [options]

Arguments:
    <num_reactions>
        The number of reactions to set up.

    <annealing_temp>
        The annealing temperature for the PCR reaction (in °C).  I typically 
        use NEB's online "Tm Calculator" to determine this parameter.

Options:
    -x --extension-time <secs>      [default: 120]
        The length of the annealing step in seconds.  The rule of thumb is 30 
        sec/kb, perhaps longer if you're amplifying a whole plasmid.

    -v --reaction-volume <μL>       [default: 10]
        The volume of the PCR reaction.  The recommended volumes for Q5 are 25
        and 50 μL.

    -m --master-mix <dna,primers,additives>      [default: dna]
        Indicate which reagents should be included in the master mix.  Valid 
        reagents are 'dna', 'primers', and 'additives',

    -a --additives <dmso,betaine>   [default: '']
        Indicate which additives should be included in the reaction.  Valid
        additives are 'dmso' and 'betaine'.

    -P --no-primer-mix
        Don't show how to prepare the 10x primer mix.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)

pcr = dirty_water.Pcr(nc=25)
pcr.num_reactions = eval(args['<num_reactions>'])
pcr.annealing_temp = int(args['<annealing_temp>'])
pcr.extension_time = int(args['--extension-time'])
pcr.dmso = 'dmso' in args['--additives']
pcr.betaine = 'betaine' in args['--additives']
pcr.template_in_master_mix = 'dna' in args['--master-mix']
pcr.primers_in_master_mix = 'primers' in args['--master-mix']
pcr.additives_in_master_mix = 'additives' in args['--master-mix']
pcr.make_primer_mix = not args['--no-primer-mix']
pcr.reaction.volume = float(args['--reaction-volume'])

print(pcr)
