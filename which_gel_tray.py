#!/usr/bin/env python3

"""\
Figure out which gel tray to use given the number and volume of your samples, 
then print out a protocol for casting that gel.

Usage:
    which_gel_tray.py <num_samples> <sample_μL> [<percent_agarose>] [options]
    which_gel_tray.py list

Subcommands:
    list
        Print out all the known trays and combs.

Options:
    -x --extra PERCENT          [default: 50]
        How much extra volume each well should accommodate beyond the volume 
        specified by <sample_μL>.

    -r --round NEAREST_ML       [default: 10]
        Round the volume of TAE to use to the nearest multiple of the given 
        value.

    -t --tray TRAY
        Specify a particular tray to use.  The program will just calculate the 
        recipe to fill the tray sufficiently for your samples.

    -c --comb COMB
        Specify a particular comb to use.  The program will just calculate the 
        recipe to fill the tray sufficiently for your samples.
"""

import re
import nonstdlib

class Tray:
    
    def __init__(self, name, width_mm, length_mm, max_depth_mm, num_slots, combs):
        self.name = name
        self.width_mm = width_mm
        self.length_mm = length_mm
        self.max_depth_mm = max_depth_mm
        self.num_slots = num_slots
        self.combs = combs
        
    @property
    def max_volume_mL(self):
        return self.width_mm * self.length_mm * self.max_depth_mm / 1e3

    @property
    def area_mm2(self):
        return self.width_mm * self.length_mm


class Comb:

    def __init__(self, name, num_teeth, tooth_width_mm, tooth_length_mm, below_tooth_mm):
        self.name = name
        self.num_teeth = num_teeth
        self.tooth_width_mm = tooth_width_mm
        self.tooth_length_mm = tooth_length_mm
        self.below_tooth_mm = below_tooth_mm

    @property
    def area_mm2(self):
        return self.tooth_width_mm * self.tooth_length_mm


class Config:

    def __init__(self, tray, comb):
        self.tray = tray
        self.comb = comb

    @property
    def num_wells(self):
        return self.tray.num_slots * self.comb.num_teeth

    @property
    def max_well_volume_uL(self):
        tray, comb = self.tray, self.comb
        well_depth_mm = tray.max_depth_mm - comb.below_tooth_mm
        return comb.tooth_width_mm * comb.tooth_length_mm * well_depth_mm

    def gel_volume_mL(self, sample_uL, unit_mL):
        tray, comb = self.tray, self.comb
        well_depth_mm = sample_uL / comb.tooth_width_mm / comb.tooth_length_mm 
        gel_depth_mm = well_depth_mm + comb.below_tooth_mm
        gel_volume_mL = tray.width_mm * tray.length_mm * gel_depth_mm / 1e3

        if unit_mL > 0:
            multiplier = gel_volume_mL // unit_mL + 1
            gel_volume_mL = unit_mL * multiplier

        return gel_volume_mL



trays = [
    Tray('Owl Easycast B1A', 
        width_mm=71.0,
        length_mm=83.0,
        max_depth_mm=13.0,
        num_slots=2,
        combs=[
            Comb('B1A-10 (1.0 mm)',
                num_teeth=10,
                tooth_width_mm=4.5,
                tooth_length_mm=1.0,
                below_tooth_mm=2.0,
            ),
            Comb('B1A-10 (1.5 mm)',
                num_teeth=10,
                tooth_width_mm=4.5,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
            Comb('B1A-6 (1.0 mm)',
                num_teeth=6,
                tooth_width_mm=9.0,
                tooth_length_mm=1.0,
                below_tooth_mm=2.0,
            ),
            Comb('B1A-6 (1.5 mm)',
                num_teeth=6,
                tooth_width_mm=9.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
        ],
    ),
    Tray('Owl Easycast B2',
        width_mm=120.0,
        length_mm=138.5,
        max_depth_mm=13.0,
        num_slots=4,
        combs=[
            Comb('B2-25',
                num_teeth=25,
                tooth_width_mm=2.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
            Comb('B2-20 (1.0 mm)',
                num_teeth=20,
                tooth_width_mm=4.0,
                tooth_length_mm=1.0,
                below_tooth_mm=2.0,
            ),
            Comb('B2-20 (1.5 mm)',
                num_teeth=20,
                tooth_width_mm=4.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
            Comb('B2-12 (1.0 mm)',
                num_teeth=12,
                tooth_width_mm=7.0,
                tooth_length_mm=1.0,
                below_tooth_mm=2.0,
            ),
            Comb('B2-12 (1.5 mm)',
                num_teeth=12,
                tooth_width_mm=7.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
            Comb('B2-8',
                num_teeth=8,
                tooth_width_mm=12.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
        ],
    ),
    Tray('Owl D4',
        width_mm=156.0,
        length_mm=173.0,
        max_depth_mm=13.0,
        num_slots=3,
        combs=[
            Comb('D4-17',
                num_teeth=17,
                tooth_width_mm=7.0,
                tooth_length_mm=1.5,
                below_tooth_mm=2.0,
            ),
        ]
    ),
    Tray('Shelton MP-1015',
        width_mm=104.0,
        length_mm=150.0,
        max_depth_mm=18.0,
        num_slots=3,    # The tray has 4 slots, but the lab only has 3 combs.
        combs=[
            Comb('16',
                num_teeth=16,
                tooth_width_mm=3.5,
                tooth_length_mm=2.0,
                below_tooth_mm=1.0,
            ),
        ],
    ),
    Tray('Biorad Mini-Sub Cell GT (7 cm)',
        width_mm=62.0,
        length_mm=70.0,
        max_depth_mm=10.0,
        num_slots=1,
        combs=[
            Comb('15',
                num_teeth=15,
                tooth_width_mm=2.5,
                tooth_length_mm=1.5,
                below_tooth_mm=1.5,
            ),
        ],
    ),
    Tray('Biorad Mini-Sub Cell GT (10 cm)',
        width_mm=62.0,
        length_mm=100.0,
        max_depth_mm=10.0,
        num_slots=2,
        combs=[
            Comb('15',
                num_teeth=15,
                tooth_width_mm=2.5,
                tooth_length_mm=1.5,
                below_tooth_mm=1.5,
            ),
        ],
    ),
]
            


if __name__ == '__main__':
    import docopt
    args = docopt.docopt(__doc__)

    if args['list']:
        for tray in trays:
            print(tray.name)
            for comb in tray.combs:
                print(' ', comb.name)
        raise SystemExit

    num_samples = int(args['<num_samples>'])
    sample_uL = float(args['<sample_μL>']) * (1 + float(args['--extra']) / 100)
    percent_agarose = float(args['<percent_agarose>'] or 1)
    unit_mL = int(args['--round'])
    user_tray = re.compile(args['--tray'], re.I) if args['--tray'] else None
    user_comb = re.compile(args['--comb'], re.I) if args['--comb'] else None

    # Find the smallest tray that can fit all the samples.

    best_config = None

    for tray in trays:
        for comb in tray.combs:
            config = Config(tray, comb)

            if user_tray and not user_tray.search(tray.name):
                continue
            if user_comb and not user_comb.search(comb.name):
                continue
            if config.num_wells < num_samples:
                continue
            if config.gel_volume_mL(sample_uL, unit_mL) > tray.max_volume_mL:
                continue

            if best_config is None or tray.area_mm2 < best_config.tray.area_mm2:
                best_config = config
            if best_config.tray is tray and comb.area_mm2 < best_config.comb.area_mm2:
                best_config = config
            
    if best_config is None:
        print("No tray found.")
        raise SystemExit

    # Print a protocol for casting the gel.

    tae_needed_mL = best_config.gel_volume_mL(sample_uL, unit_mL)
    agarose_needed_g = percent_agarose * tae_needed_mL / 100
    gelred_needed_uL = tae_needed_mL / 10

    print('1. Assemble the gel tray.')
    print()
    print('   Tray: ' + best_config.tray.name)
    print('   Comb: ' + best_config.comb.name)
    print()
    print('2. Use the following recipe to pour the gel:')
    print()
    print('   TAE: {} mL'.format(tae_needed_mL))
    print('   Agarose: {} g'.format(agarose_needed_g))
    print('   GelRed: {} μL'.format(gelred_needed_uL))
    print()
