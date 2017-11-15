#!/usr/bin/env python3

"""\
Display a protocol for electrotransforming DNA into Top10 cells.

Usage:
    electrotransformation.py
"""

import dirty_water

protocol = dirty_water.Protocol()

protocol += """\
Desalt and concentrate the DNA to transform using 
a Zymo spin column with the Qiagen buffers:

- Add 285 μL PB to the ligation reaction.

- Transfer to a Zymo spin column.

- Wash with 200 μL PE.

- Wash with 200 μL PE again.

- Elute in 10 μL water."""

protocol += """\
Transform the DNA into Top10 cells by 
electroporation.  For each transformation:

- Pre-warm 1 mL SOC and a selective plate.

- Chill an electroporation cuvette and 2 μL (≈250 
  ng) of DNA on ice.  

- Thaw an aliquot of competent cells on ice for 
  ~10 min.

- Pipet once to mix the cells with the DNA, then 
  load into the cuvette.  Tap to remove bubbles.

- Shock at 1.8 kV with a 5 ms decay time (for 
  cuvettes with a 1 mm gap).

- Immediately add 1 mL pre-warmed SOC.  If you're 
  transforming multiple aliquots of cells with 
  the same DNA, combine them.

- Recover at 37°C for 1h.
  
- Plate several 10x dilutions of cells (e.g.  
  from 10⁻³ to 10⁻⁶) to count how many were 
  transformed.

- Transfer cells to 50 mL selective media and 
  grow overnight at 37°C."""

if __name__ == '__main__':
    import docopt
    print(protocol)

# vim: tw=49
