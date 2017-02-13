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

    -v --reaction-volume <μL>       [default: 25]
        The volume of the PCR reaction.  The recommended volumes for Q5 are 25
        and 50 μL.

    -m --master-mix <reagents>      [default: dna]
        Indicate whether or not the primers and/or the DNA template should be 
        included in the master mix.  Valid reagents are 'dna' and 'primers'.  

    -P --no-primer-mix
        Don't show how to prepare the 10x primer mix.

    --skip-pcr
        Don't show how to setup the PCR reaction, just show how to ligate and
        transform the DNA.
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
pcr.reaction.volume = float(args['--reaction-volume'])
pcr.reaction['template DNA'].master_mix = 'dna' in args['--master-mix']
pcr.reaction['primer mix'].master_mix = 'primers' in args['--master-mix']
pcr.make_primer_mix = not args['--no-primer-mix']
s = 's' if pcr.num_reactions != 1 else ''



if not args['--skip-pcr']:
    protocol += pcr

## Phosphorylation

pnk = dirty_water.Reaction('''\
Reagent                Conc  Each Rxn  Master Mix
================  =========  ========  ==========
water                         13.5 μL         yes
T4 ligase buffer        10x    2.0 μL         yes
T4 PNK              10 U/μL    0.5 μL         yes
T4 DNA ligase      400 U/μL    0.5 μL         yes
DpnI                20 U/μL    0.5 μL         yes
PCR product       ≈50 ng/μL    3.0 μL
''')

pnk.num_reactions = pcr.num_reactions
pnk.extra_master_mix = 15

protocol += """\
Setup {pnk.num_reactions} ligation reaction{s}:

{pnk}

- Incubate at room temperature for 1h."""

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
