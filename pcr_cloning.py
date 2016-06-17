#!/usr/bin/env python3
# vim: tw=50

"""\
Make a small modification to a plasmid by amplifying it with primers that have 
overhangs with your desired change.

Usage:
    pcr_cloning.py <num_reactions> [options]

Options:
    -t --annealing-temp <celsius>   [default: 62]
        The annealing temperature for the PCR reaction.  I typically use NEB's 
        online "Tm Calculator" to determine this parameter.

    -x --extension-time <secs>      [default: 120]
        The length of the annealing step in seconds.  The rule of thumb is 30 
        sec/kb, perhaps longer if you're amplifying a whole plasmid.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
protocol = dirty_water.Protocol()

## PCR

pcr = dirty_water.Pcr()
pcr.num_reactions = eval(args['<num_reactions>'])
pcr.annealing_temp = int(args['--annealing-temp'])
pcr.extension_time = int(args['--extension-time'])

protocol += pcr

protocol += """\
Purify the amplified DNA.

A PCR cleanup is enough if the reaction worked 
well.  Otherwise do a gel extraction."""

## Phosphorylation

pnk = dirty_water.Reaction('''\
Reagent                Conc  Each Rxn  Master Mix
================  =========  ========  ==========
water                           13 μL         yes
T4 ligase buffer        10x      2 μL         yes
T4 PNK              10 U/μL      1 μL         yes
PCR product       ≈50 ng/μL      3 μL
''')

pnk.num_reactions = pcr.num_reactions
pnk.extra_master_mix = 50

protocol += """\
Setup {pnk.num_reactions} phosphorylation reactions:

{pnk}

- Incubate at 37°C for 1h."""

## Ligation

protocol += """\
Add 1 μL T4 DNA ligase to each reaction.

- Incubate at 16°C overnight, or at 25°C for 1h if 
  you're in a hurry."""

## Transformation

protocol += """\
Transform the ligated DNA into Top10 cells."""

## Miniprep and sequence

protocol += """\
Pick individual colonies to grow overnight in 5 mL 
selective media."""

protocol += """\
Miniprep the overnight culture to isolate pure 
plasmid and send it for sequencing.  Store the 
remaining DNA at -20°C."""


print(protocol)
