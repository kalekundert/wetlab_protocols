#!/usr/bin/env python3

"""\
Load, run and stain PAGE gels

Usage:
    page sds <n> [options]
    page native <n> [options]
    page urea <n> [options]

Arguments:
    <num_samples>
        The number of samples to prepare.

Options:
    -p --percent STR
        The percentage of polyacrylamide in the gel being run.

    -s --sample-types TYPES
        Indicate what kinds of sample are being loaded on the gel, so that 
        suggestions about how to dilute them can be shown.  The following types 
        are understood, use commas to specify multiple types:

            ivt:   RNA translated in vitro.
            pure:  Protein expressed using NEB PURExpress.
            s30:   Protein expressed using Promega S30 extract.

    -C --coomassie
        Add coomassie to the native PAGE gel.  Coomassie helps proteins migrate 
        uniformly by binding and providing a uniform negative charge (similar 
        to SDS, but without denaturing).  However, Coomassie can also interfere 
        with some applications, e.g. fluorescence imaging.
"""

import stepwise
import docopt

args = docopt.docopt(__doc__)

# Work out what to do based on the type of gel being run.
params = {}

def config_sds(params):
    params['title'] = 'SDS'
    params['sample_mix'] = stepwise.MasterMix.from_text("""\
Reagent             Stock   Volume  MM?
==============  =========  =======  ===
loading buffer         4x  3.85 µL  yes
reducing agent        10x  1.54 µL  yes
protein                      10 µL
""", solvent='protein')
    params['incubate'] = "70°C for 10 min"
    params['percent'] = "4−12%"
    params['load'] = params['sample_mix'].volume
    params['run'] = "165V for 42 min"

def config_native(params):
    params['title'] = 'native'
    params['sample_mix'] = stepwise.MasterMix.from_text("""\
Reagent             Stock   Volume  MM?
==============  =========  =======  ===
water                      2.25 µL  yes
sample buffer          4x   2.5 µL  yes
G-250 additive         5%  0.25 µL  yes
DNA/protein                1.25 µL
""")
    params['percent'] = "3−12%"
    params['load'] = '5 µL'
    params['run'] = '150V for 115 min'
    params['hints'] = """\
- For a DNA ladder, use 5 µL 50 ng/µL.
"""
    if not args['--coomassie']:
        del params['sample_mix']['G-250 additive']

def config_urea(params):
    params['title'] = 'TBE/urea'
    params['sample_mix'] = stepwise.MasterMix.from_text("""\
Reagent             Stock   Volume  MM?
==============  =========  =======  ===
water                         4 µL  yes
sample buffer          2x     5 µL  yes
RNA/DNA         200 ng/µL     1 µL
""")
    params['incubate'] = "70°C for 3 min"
    params['percent'] = '6%'
    params['load'] = '10 µL'
    params['run'] = '180V for 40 min'
    params['hints'] = """\
- Dilute IVT samples 10x (2000 ng/µL is a typical yield).
"""
    params['stain'] = """\
Stain in 1x PAGE GelRed for 30 min.
"""

if args['sds']:
    config_sds(params)
if args['native']:
    config_native(params)
if args['urea']:
    config_urea(params)

params['sample_mix'].num_reactions = eval(args['<n>'])
params['sample_mix'].extra_percent = 50

# Print the protocol.
protocol = stepwise.Protocol()

step = f"Prepare samples for {params['title']} PAGE:\n\n"
if 'sample_mix' in params:
    step += f"{params['sample_mix']}\n\n"
if 'hints' in params:
    step += f"{params['hints'].strip()}\n"
if 'incubate' in params:
    step += f"- Incubate at {params['incubate']}."

protocol += step

protocol += f"""\
Run the gel:

- Use a {args['--percent'] or params['percent']} {params['title']} PAGE gel.
- Load {params['load']} of each sample.
- Run at {params['run']}.
"""

if 'stain' in params:
    protocol += params['stain']

print(protocol)

