#!/usr/bin/env python3

"""\
Display a protocol for running in vitro transcription reactions.

Usage:
    ivt <reactions> [options]

Options:
    -d --dna-conc NG_PER_UL  [default: 500]
        The concentration of the template DNA (in ng/µL).

    -D --dna-ng NANOGRAMS    [default: 1000]
        How much template DNA to use (in ng).  The default is 1 µg, as 
        recommended by both the HiScribe and Ampliscribe kits.  Lower amounts 
        will give proportionately lower yield, but will otherwise work fine.  

        If the template is not concentrated enough to reach the given quantity, 
        the reaction will just contain as much DNA as possible instead.

    -V --dna-vol UL
        The volume of DNA to add to the reaction.  If specified, the --dna-conc
        and --dna-ng arguments will be ignored.

    -k --kit BRAND   [default: hiscribe]
        Which in vitro transcription kit to use.  Valid options are 'hiscribe'
        and 'ampliscribe'.

    -i --incubate HOURS
        How long to incubate the transcription reaction.  The default depends
        on which kit you're using.

    -x --extra PERCENT      [default: 10]
        How much extra master mix to create.

    -R --no-rntp-mix
        Indicate that each you're not using a rNTP mix and that you need to add 
        each rNTP individually to the reaction.

    -c --cleanup METHOD     [default: zymo]
        Choose the method for removing free nucleotides from the RNA:
        'none': Carry on the crude reaction mix.
        'zymo': Zymo spin kits.
        'ammonium': Ammonium acetate precipitation.

    -g --gel
        Print detailed instructions on how to do RNA PAGE.

    -v --verbose
        Print out more detailed tips and tricks related to various steps of the
        protocol.

"""

import docopt
import dirty_water
import stepwise
from inform import warn, plural

args = docopt.docopt(__doc__)
protocol = stepwise.Protocol()

## Calculate reagent volumes.

ivt = dirty_water.Reaction()
ivt.num_reactions = eval(args['<reactions>'])
ivt.extra_master_mix = float(args['--extra'])

if args['--dna-vol']:
    dna_uL = float(args['--dna-vol'])
    dna_ng_uL = float(args['--dna-conc'])
    err = {
            'desired_dna': f'{dna_uL} µL',
            'max_dna': lambda x: f'{x} µL',
    }
else:
    dna_ng = float(args['--dna-ng'])
    dna_ng_uL = float(args['--dna-conc'])
    dna_uL = dna_ng / dna_ng_uL
    err = {
            'desired_dna': f'{dna_ng} ng',
            'max_dna': lambda x: f'{x * dna_ng_uL} ng',
    }

if 'hiscribe'.startswith(args['--kit'].lower()):
    incubation_time = args['--incubate'] or 2
    incubation_temp = '37'

    non_reagent_uL = 20 - 12.5
    water_uL = non_reagent_uL - dna_uL

    if water_uL <= 0:
        warn = f"Cannot reach the recommended {err['desired_dna']} of DNA, using {err['max_dna'](non_reagent_uL)} instead."
        dna_uL = non_reagent_uL
    else:
        ivt['nuclease-free water'].std_volume = water_uL, 'μL'
        ivt['nuclease-free water'].master_mix = True

    ivt['reaction buffer'].std_volume = 2.0, 'μL'
    ivt['reaction buffer'].std_stock_conc = '10x'
    ivt['reaction buffer'].master_mix = True

    ivt['RNase inhibitor'].std_volume = 0.5, 'μL'
    ivt['RNase inhibitor'].master_mix = True
    ivt['RNase inhibitor'].std_stock_conc = 40, 'U/μL'
    ivt['RNase inhibitor'].product_number = 'NEB M0307S'

    if args['--no-rntp-mix']:
        ivt['ATP'].std_volume = 2.0, 'μL'
        ivt['ATP'].master_mix = True
        ivt['ATP'].std_stock_conc = 100, 'mM'

        ivt['CTP'].std_volume = 2.0, 'μL'
        ivt['CTP'].master_mix = True
        ivt['CTP'].std_stock_conc = 100, 'mM'

        ivt['GTP'].std_volume = 2.0, 'μL'
        ivt['GTP'].master_mix = True
        ivt['GTP'].std_stock_conc = 100, 'mM'

        ivt['UTP'].std_volume = 2.0, 'μL'
        ivt['UTP'].master_mix = True
        ivt['UTP'].std_stock_conc = 100, 'mM'
    else:
        ivt['rNTP mix'].std_volume = 8.0, 'μL'
        ivt['rNTP mix'].std_stock_conc = 100, 'mM'
        ivt['rNTP mix'].master_mix = True

    ivt['HiScribe T7'].std_volume = 2.0, 'μL'
    ivt['HiScribe T7'].std_stock_conc = '10x'
    ivt['HiScribe T7'].master_mix = True
    ivt['HiScribe T7'].product_number = 'NEB E2040S'

    ivt['DNA template'].std_volume = dna_uL, 'μL'
    ivt['DNA template'].std_stock_conc = dna_ng_uL, 'ng/μL'

elif 'ampliscribe'.startswith(args['--kit'].lower()):
    incubation_time = args['--incubate'] or 1
    incubation_temp = '42'

    non_reagent_uL = 20 - 2.0 - 7.2 - 2.0 - 0.5 - 2.0
    water_uL = non_reagent_uL - dna_uL

    if water_uL <= 0:
        warn = f"Cannot reach the recommended {err['desired_dna']} of DNA, using {err['max_dna'](non_reagent_uL)} instead."
        dna_uL = non_reagent_uL
    else:
        ivt['nuclease-free water'].std_volume = water_uL, 'μL'
        ivt['nuclease-free water'].master_mix = True

    ivt['reaction buffer'].std_volume = 2.0, 'μL'
    ivt['reaction buffer'].std_stock_conc = '10x'
    ivt['reaction buffer'].master_mix = True

    if args['--no-rntp-mix']:
        ivt['ATP'].std_volume = 1.8, 'μL'
        ivt['ATP'].std_stock_conc = 100, 'mM'
        ivt['ATP'].master_mix = True
        ivt['CTP'].std_volume = 1.8, 'μL'
        ivt['CTP'].std_stock_conc = 100, 'mM'
        ivt['CTP'].master_mix = True
        ivt['GTP'].std_volume = 1.8, 'μL'
        ivt['GTP'].std_stock_conc = 100, 'mM'
        ivt['GTP'].master_mix = True
        ivt['UTP'].std_volume = 1.8, 'μL'
        ivt['UTP'].std_stock_conc = 100, 'mM'
        ivt['UTP'].master_mix = True
    else:
        ivt['rNTP mix'].std_volume = 7.2, 'μL'
        ivt['rNTP mix'].std_stock_conc = 100, 'mM'
        ivt['rNTP mix'].master_mix = True

    ivt['DTT'].std_volume = 2.0, 'μL'
    ivt['DTT'].std_stock_conc = 100, 'mM'
    ivt['DTT'].master_mix = True
    ivt['RiboGuard RNase innhibitor'].std_volume = 0.5, 'μL'
    ivt['RiboGuard RNase innhibitor'].std_stock_conc = '40x'
    ivt['RiboGuard RNase innhibitor'].master_mix = True
    ivt['Ampliscribe T7 (Epicentre)'].std_volume = 2.0, 'μL'
    ivt['Ampliscribe T7 (Epicentre)'].std_stock_conc = '10x'
    ivt['Ampliscribe T7 (Epicentre)'].master_mix = True
    ivt['DNA template'].std_volume = dna_uL, 'μL'
    ivt['DNA template'].std_stock_conc = dna_ng_uL, 'ng/μL'

else:
    print("Unknown in vitro transcription kit: '{}'".format(args['--kit']))
    print("Known kits are: 'hiscribe' or 'ampliscribe'")
    raise SystemExit

## Clean your bench

protocol += """\
Wipe down your bench and anything you'll touch 
(pipets, racks, pens, etc.) with RNaseZap."""

## In vitro transcription

protocol += """\
Setup {:# in vitro transcription reaction/s} by 
mixing the following reagents at room temperature 
in the order given{}.

{}""".format(
        plural(ivt.num_reactions), ' [1]' if warn else '', ivt)

if warn:
    from textwrap import fill
    protocol.footnotes[1] = fill(warn, width=49)

protocol += """\
Incubate at {}°C (thermocycler) for {:# hour/s}.""".format(
        incubation_temp, plural(incubation_time))

## Purify product

if args['--cleanup'] == 'zymo':
    protocol += """\
Remove unincorporated ribonucleotides using Zymo 
RNA Clean & Concentrator 25 spin columns."""

elif args['--cleanup'] == 'ammonium':
    protocol += """\
Remove unincorporated ribonucleotides using
ammonium acetate precipitation.

Note that ammonium acetate precipitation only 
works for constructs that are longer than 100 bp.

Ammonium Acetate Precipitation
──────────────────────────────
a. Add 1 volume (20 μL) 5M ammonium acetate to 
   each reaction.

b. Incubate on ice for 15 min.

c. Centrifuge at >10,000g for 15 min at 4°C.

d. Wash pellet with 70% ethanol.

e. Dissolve pellet in 20μL nuclease-free water."""

elif args['--cleanup'] == 'none':
    raise SystemExit

else:
    raise ValueError("unknown RNA clean-up method: '{}'".format(args['--cleanup']))

## Nanodrop concentration

protocol += """\
Nanodrop to determine the RNA concentration."""

## Aliquot

protocol += """\
Dilute (if desired) enough RNA to make several 
10 μM aliquots and to run a gel.  Keep any left- 
over RNA undiluted.  Flash-freeze in liquid N₂ and 
store at -80°C."""

## Gel electrophoresis

if not args['--gel']:
    protocol += """\
Run the RNA on a denaturing gel to make sure it's 
homogeneous and of the right size."""

else:
    import tbe_urea_gel
    protocol += tbe_urea_gel.protocol


print(protocol)

if args['--verbose']:
    print("""\
Comments
========
- I've found that T7 kits which have been in the 
  freezer for more than ≈4 weeks seem to produce 
  more degraded RNA.""")

# vim: tw=50
