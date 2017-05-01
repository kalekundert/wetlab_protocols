#!/usr/bin/env python3
# vim: tw=50

"""\
Make a small modification to a plasmid by amplifying it with primers that have 
overhangs with your desired change.

Usage:
    pcr_cloning.py <num_reactions> <annealing_temp> [options]

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

    -P --no-primer-mix
        Don't show how to prepare the 10x primer mix.

    -a --additives <dmso,betaine>
        Indicate which additives should be included in the reaction.  Valid
        additives are 'dmso' and 'betaine'.

    --skip-pcr
        Don't show how to setup the PCR reaction, just show how to ligate and
        transform the DNA.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
protocol = dirty_water.Protocol()

## PCR

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
Transform 2 μL ligated DNA into 20 μL CaCl₂ 
competent Top10 cells."""

## Miniprep and sequence

protocol += """\
Pick 2-6 individual colonies for each reaction to 
send for sequencing.  (You can pick fewer colonies 
for reactions with shorter primers.)  Resuspend 
the colonies in 30 μL EB, then send 15 μL for 
sequencing and keep the rest at 4°C."""

protocol += """\
Start 3.5 mL overnight cultures in selective media 
for each picked colony.  If the sequencing data 
isn't available by the next morning, pellet the 
cells and store the pellets at -20°C.  Miniprep 
the cultures with the right sequence."""

print(protocol)
