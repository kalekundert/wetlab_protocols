#!/usr/bin/env python3

"""
Print out the preferred enzymes for use in Golden Gate assemblies.

Usage:
    golden_gate_enzymes.py
"""

import docopt

docopt.docopt(__doc__)

# https://www.neb.com/applications/cloning-and-synthetic-biology/dna-assembly-and-cloning/golden-gate-assembly 
print("""\
BsaI-HFv2
BbsI-HF
Esp3I
""".strip())
