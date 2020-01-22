#!/usr/bin/env python3

"""\
Cast an 8% TBE/urea gel.

Usage:
    tbe_urea_gel.py [<num>] [-b]
    
Arguments:
    <num>               [default: 1]
        The number of gels to cast.  Each gel has 15 lanes, which is enough for 
        14 samples and one ladder.

Options:
    -b --buffer
        Include the recipe for TBE.
"""

import docopt
import dirty_water
from nonstdlib import plural, round_up

args = docopt.docopt(__doc__)
protocol = dirty_water.Protocol()
M = eval(args['<num>']) if args['<num>'] else 1
N = round_up(M * 7/10, 0.1)
gels = f"{plural(M):gel/s}"

if args['--buffer']:
    protocol += f"""\
Prepare 1L 5x TBE:

- 54 g Tris base
- 27.5 g boric acid
- 20 mL 0.5 M EDTA (pH=8.0)"""

protocol += f"""\
Cast {M} 8% TBE/urea polyacrylamide {gels}.

- Setup the gel cast and check for leaks.
  
- Combine the following reagents in a Falcon tube 
  and mix until the urea dissolves (~5 min).

  Reagent         Conc       Amount
  ─────────────────────────────────
  urea                     {N*4.2:5.2f} g
  TBE               5x     {N*2.0:5.2f} mL
  acrylamide/bis   30%     {N*2.67:5.2f} mL
  water                 to {N*10:5.2f} mL

- Add {N*10:.2f} uL TEMED and {N*10:.2f} μL 0.4 mg/μL APS
  (freshly prepared), invert once or twice to mix, 
  then immediately pipet into the gel cast.

- Let the {gels} set for 1h.
  
- Either use the {gels} immediately, or wrap {plural(N):/them/it} in a
  wet paper towel and store at 4°C overnight to 
  use the next day."""

protocol += """\
Load and run the {gels}.

- Mix 2 μL of RNA with 2 μL of loading dye.

- Denature at 95°C for 2 min.

- Wash out any urea that's leached into the wells, 
  then quickly load all of the samples.

- Run at 180V for 30 min.
  
- Soak in 3x GelRed for ~15 min to stain."""

if __name__ == '__main__':
    print(protocol)
