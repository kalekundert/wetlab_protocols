#!/usr/bin/env python3

"""\
Purify DNA using magnetic beads.

Usage:
    dna_beads [-v UL] [-e ELUANT]

Options:
    -v --volume UL
        The volume of to elute in, in µL.  By default this is left unspecified.
    
    -e --eluant ELUANT  [default: EB]
        The eluant to use, e.g. EB or water.
"""

import docopt
import stepwise

args = docopt.docopt(__doc__)
elute_vol = f"{args['--volume']} µL" if args['--volume'] else 'any volume'

protocol = stepwise.Protocol()

protocol += f"""\
Purify DNA using magnetic beads [1].

- Gently resuspend the bead solution [2].
- Add 1 volume of bead solution to each sample.
- Incubate 5 min at room temperature.
- Apply magnet for >2 min and discard supernatant.
- Wash twice:
  - Add 200 µL 70% EtOH.
  - Incubate 30 sec at room temperature.
  - Apply to magnet and discard ethanol.
- Air-dry for 4-5 minutes [3].
- Add {elute_vol} of {args['--eluant']}.
- Apply magnet for >2 min.
- Transfer ≈95% of the eluant to a clean tube.
"""

protocol.footnotes[1] = """\
See "Magnetic Bead DNA Purification" in my Google 
Drive for more details.
"""

protocol.footnotes[2] = """\
Don't vortex; this damages the beads (somehow).
"""

protocol.footnotes[3] = """\
Be careful not to over-dry the beads.  Over-dried
beads will appear cracked and will be difficult 
to resuspend.  If this happens, heat and agitate 
for 10-15 minutes during elution to help 
resuspend the beads and release the DNA.  An 
alternative strategy is to add the eluant after a 
very short drying step, then leaving the tubes 
open for 10-15 minutes to allow the ethanol to 
evaporate.
"""

print(protocol)
