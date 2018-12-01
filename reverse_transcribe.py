#!/usr/bin/env python3

"""\
Reverse-transcribe RNA to cDNA.

Usage:
    reverse_transcribe.py [<rna_conc.tsv>] [options]

Arguments:
    <rna_conc.tsv>
        Concentrations of the RNAs, as exported from the Nanodrop.

Options:
    -d --dnase
        Add a DNase pre-treatment step to the beginning of the protocol.
"""

import docopt
import dirty_water
import pandas as pd

args = docopt.docopt(__doc__)

protocol = dirty_water.Protocol()
concs = ''

if args['<rna_conc.tsv>']:
    df = pd.read_csv(args['<rna_conc.tsv>'], sep='\t')
    df['conc'] = df[' Corrected (ng/uL)'].fillna(df['Nucleic Acid(ng/uL)'])

    concs = """\
───────────────────────────────────────────────────────
                           RNA Conc  RNA Vol  Water Vol
Construct                   (ng/uL)     (µL)       (µL)
───────────────────────────────────────────────────────
"""
    for i, row in df.iterrows():
        name = row['Sample Name']
        conc =  row['conc']
        vol = 1000 / conc
        ref = 8 if not args['--dnase'] else 4
        concs += f"{name:25s}    {conc:6.2f}   {vol:6.2f}    {ref-vol:6.2f}\n"
    concs += """\
───────────────────────────────────────────────────────
"""

if args['--dnase']:
    protocol += f"""\
Setup DNase reactions for each sample:

- 1 µL 10 ezDNase buffer
- 1 µL ezDNase enzyme (Invitrogen 11766051)
- 1 µg RNA
- Water to 6 µL

Consider preparing a 2x ezDNase master mix.
"""

    protocol += """\
Incubate at 37°C for 2 min.  Then briefly 
centrifuge and place on ice.
"""

    protocol += """\
Add 2 µL SuperScript IV VILO master mix 
(Invitrogen 11766050) and 2 µL water to each 
sample.

The master mix contains random hexamers, which 
will prime the reverse transcription of all RNAs 
in the sample.
"""
else:
    protocol += f"""\
Setup reverse transcription reactions for each 
sample:

- 1 µg RNA
- 2 µL SuperScript IV VILO master mix
  (Invitrogen 11766050)
- water to 10 µL

The master mix contains random hexamers, which 
will prime the reverse transcription of all RNAs 
in the sample.
"""

protocol += """\
Incubate at the following temperatures:

- 25°C for 10 min
- 50°C for 10 min (15 min)
- 85°C for 5 min
- hold at 4°C
"""

if __name__ == '__main__':
    print(protocol)
    if args['<rna_conc.tsv>']:
        print()
        print(concs)

