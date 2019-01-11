#!/usr/bin/env python3

import docopt
import dirty_water

protocol = dirty_water.Protocol()

protocol += """\
Extract total cellular RNA:

- Pellet cells at 4100 rpm for 10 min.

- Resuspend each cell pellet in 1 mL TRIzol 
  (Invitrogen 15596026).

- Incubate 5 min at room temperature.

- Add 200 µL chloroform.

- Vortex vigorously.

- Centrifuge for 15 min at 20,000g and 4°C.

- Transfer aqueous phase (top, not pink, ~500 µL) 
  for each sample to a clean tube, taking care to 
  avoid transferring any of the organic phase.
"""

protocol += """\
Concentrate and purify the RNA by ethanol precipitation:

- Add 1 µL GlycoBlue (Invitrogen AM9516) to each 
  sample.

- Add 500 µL isopropanol.

- Incubate at room temperature for 10 min.

- Pellet for 20 min at 12,000g and 4°C.

- Carefully pipet off all supernatant.

- Resuspend pellet in 70% EtOH.

- Vortex briefly

- Pellet for 5 min at 7,500g and 4°C.

- Carefully pipet off all supernatant.

- Air dry for 10 min.

- Resuspend RNA in 10 µL water.
"""

protocol += """\
Measure the RNA concentration of each sample using the Nanodrop.
"""

if __name__ == '__main__':
    print(protocol)


