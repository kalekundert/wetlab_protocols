#!/usr/bin/env python3

"""\
Reverse-transcribe RNA to cDNA.

Usage:
    reverse_transcribe.py [<rna_conc.tsv>]

Arguments:
    <rna_conc.tsv>
        Concentrations of the RNAs, as exported from the Nanodrop.
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
        concs += f"{name:25s}    {conc:6.2f}   {vol:6.2f}    {8-vol:6.2f}\n"
    concs += """\
───────────────────────────────────────────────────────
"""

protocol += f"""\
Setup reverse transcription reactions for each 
sample:

- 1 µg RNA
- 2 µL SuperScript VILO master mix (Invitrogen 
  11755050)
- water to 10 µL

The master mix contains random hexamers, which 
will prime the reverse transcription of all RNAs 
in the sample.

{concs}
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

