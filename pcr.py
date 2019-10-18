#!/usr/bin/env python3

"""\
Usage:
    pcr.py <template> <fwd_primer> <rev_primer>
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

    --dna-final-conc <pg_uL>
        The final concentration of the template DNA in units of pg/µL.

    --dna-stock-conc <pg_uL>  [default: 100]
        The stock concentration of the template DNA in units of pg/µL.

"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
pcr = dirty_water.Pcr(
        template=args['<template>'],
        fwd_primer=args['<fwd_primer>'],
        rev_primer=args['<rev_primer>'],
        polymerase=args['--polymerase'],
)
pcr.num_reactions = eval(args['<num_reactions>'])
pcr.annealing_temp = args['<annealing_temp>']
pcr.extension_time = args['<extension_time>']
pcr.dmso = 'dmso' in args['--additives']
pcr.betaine = 'betaine' in args['--additives']
pcr.template_in_master_mix = 'dna' in args['--master-mix'] and not args['--nothing-in-master-mix']
pcr.primers_in_master_mix = 'primers' in args['--master-mix'] and not args['--nothing-in-master-mix']
pcr.additives_in_master_mix = 'additives' in args['--master-mix'] and not args['--nothing-in-master-mix']
pcr.make_primer_mix = not args['--no-primer-mix']
pcr.reaction.volume = float(args['--reaction-volume'])
pcr.reaction[args['<template>']].stock_conc = float(args['--dna-stock-conc'])

if args['--dna-final-conc']:
    pcr.reaction[args['<template>']].conc = float(args['--dna-final-conc'])

print(pcr)
