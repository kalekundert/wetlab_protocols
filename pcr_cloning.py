#!/usr/bin/env python3
# vim: tw=50

"""\
Make a small modification to a plasmid by amplifying it with primers that have 
overhangs with your desired change.

Usage:
    pcr_cloning.py <template> <fwd_primer> <rev_primer>
           <num_reactions> <annealing_temp> <extension_time> [options]

Arguments:
    <template>
        The name of the template.

    <primers>
        The name of the primers.

    <num_reactions>
        The number of reactions to set up.

    <annealing_temp>
        The annealing temperature for the PCR reaction (in °C).  I typically 
        use NEB's online "Tm Calculator" to determine this parameter.

    <extension_time>
        The length of the extension step in seconds.  The rule of thumb is 30 
        sec/kb, perhaps longer if you're amplifying a whole plasmid.

Options:
    -v --reaction-volume <μL>       [default: 10]
        The volume of the PCR reaction.  The recommended volumes for Q5 are 25
        and 50 μL.

    -m --master-mix <dna,primers,additives>      [default: dna]
        Indicate which reagents should be included in the master mix.  Valid 
        reagents are 'dna', 'primers', and 'additives',

    -M --nothing-in-master-mix
        Don't include anything but water and polymerase in the master mix.  
        This is an alias for: -m ''

    -p --polymerase <name>  [default: q5]
        The name of the polymerase being used.  Different polymerases also have 
        different thermocycler parameters, as recommended by the manufacturer.  
        Currently, the following polymerases are supported:

        q5: Q5 High-Fidelity DNA Polymerase (NEB)
        ssoadv: SsoAdvanced™ Universal SYBR® Green Supermix (Biorad)

    -a --additives <dmso,betaine>   [default: '']
        Indicate which additives should be included in the reaction.  Valid
        additives are 'dmso' and 'betaine'.

    -P --no-primer-mix
        Don't show how to prepare the 10x primer mix.

    -n --num-pcr <N>
        The number of PCR reactions to measure master mix for. By default this 
        is the same as the number of reactions, but may be different if you're 
        being clever about setting up master mixes.

    -L --skip-pcr
        Don't show how to setup the PCR reaction, just show how to ligate and
        transform the DNA.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
protocol = dirty_water.Protocol()

## PCR

if not args['--skip-pcr']:
    pcr = dirty_water.Pcr(
            template=args['<template>'],
            fwd_primer=args['<fwd_primer>'],
            rev_primer=args['<rev_primer>'],
            polymerase=args['--polymerase'],
    )
    pcr.num_reactions = eval(args['--num-pcr']) if args['--num-pcr'] else eval(args['<num_reactions>'])
    pcr.annealing_temp = args['<annealing_temp>']
    pcr.extension_time = int(eval(args['<extension_time>']))
    pcr.dmso = 'dmso' in args['--additives']
    pcr.betaine = 'betaine' in args['--additives']
    pcr.template_in_master_mix = 'dna' in args['--master-mix'] and not args['--nothing-in-master-mix']
    pcr.primers_in_master_mix = 'primers' in args['--master-mix'] and not args['--nothing-in-master-mix']
    pcr.additives_in_master_mix = 'additives' in args['--master-mix'] and not args['--nothing-in-master-mix']
    pcr.make_primer_mix = not args['--no-primer-mix']
    pcr.reaction.volume = float(args['--reaction-volume'])

    protocol += pcr

## Ligation

kld = dirty_water.Reaction('''\
Reagent                Conc  Each Rxn  Master Mix
================  =========  ========  ==========
water                         6.75 μL         yes
T4 ligase buffer        10x   1.00 μL         yes
T4 PNK              10 U/μL   0.25 μL         yes
T4 DNA ligase      400 U/μL   0.25 μL         yes
DpnI                20 U/μL   0.25 μL         yes
PCR product       ≈50 ng/μL   1.50 μL
''')

kld.num_reactions = eval(args['<num_reactions>'])
kld.extra_master_mix = 15
s = 's' if kld.num_reactions != 1 else ''

protocol += """\
Setup {kld.num_reactions} ligation reaction{s}:

{kld}

- Incubate at room temperature for 1h."""

## Transformation

protocol += """\
Transform 1 μL ligated DNA into 10 μL MACH1 
chemically-competent cells."""

print(protocol)
