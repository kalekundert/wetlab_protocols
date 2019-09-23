#!/usr/bin/env python3

"""\
Perform a Gibson assembly reaction, using the NEB master mix (E2611).

Usage:
    gibson_assembly.py [<fragments>] [<num_reactions>] [options]

Arguments:
    <fragments>
        The DNA fragments to assemble.  For each fragment, the following 
        information can be specified:
        
        - A name (optional): This is how the fragment will be referred to in 
          the protocol, but will not have any effect other than that.  By 
          default, a generic name like "Insert #1" will be chosen.

        - A concentration (required): This is used to calculate how much of 
          each fragment needs to be added to get the ideal backbone:insert 
          ratio.  You may specify a unit (e.g. nM), but ng/µL will be assumed 
          if you don't.  You may also specify the concentration as just "PCR" 
          (no other value or units).  This indicates that the fragment is the 
          product of an unpurified PCR reaction, and is assumed to be 50 ng/μL.

        - A length (required if concentration is in ng/µL): The length of the 
          fragment in bp.  This is used to convert the above concentration into
          a molarity.

        For each individual fragment, specify whichever of the above fields are 
        relevant, separated by commas.  In other words:
        
            [<name>,]<conc>[,<length>]

        Separate different fragments from each other with ":".  The first 
        fragment is taken to be the backbone (which is typically present at 
        half the concentration of the inserts, see --excess-insert).  There 
        must be at least two fragments.

        Putting everything together, this is how you would specify an assembly 
        between a backbone that is 70 ng/µL and 1800 bp long, and an insert 
        that is 34 nM:

            70,1800:34nM

        By default, or if this argument is "-", you will be asked to provide 
        the requisite fragment information via stdin. 

    <num_reactions>
        The number of reactions to setup.  The default is 1.

Options:
    -m, --master-mix <bb,ins>  [default: ""]
        Indicate which fragments should be included in the master mix.  Valid 
        fragments are "bb" (for the backbone), "ins" (for all the inserts), 
        "1" (for the first insert), "2", "3", etc.

    -v, --reaction-volume <µL>  [default: 10]
        The volume of the complete Gibson reaction.  You might want bigger 
        reaction volumes if your DNA is dilute, or if you have a large number 
        of inserts.
        
    -d, --dna-volume <µL>
        The maximum combined volume of backbone and insert DNA to use, in µL.  
        The default is use the quantities of DNA recommended by NEB, i.e. 0.2 
        pmol/fragment for 3 or fewer fragments, or as much as possible if those 
        quantities can't be reached.  You might want to use less DNA if you're 
        trying to conserve material.
"""

import docopt
import dirty_water
import golden_gate

def uL_from_pmol(pmol, conc_nM):
    return 1e3 * pmol / conc_nM

def pmol_from_uL(uL, conc_nM):
    return uL * conc_nM / 1e3

if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    rxn_vol_uL = eval(args['--reaction-volume'])
    mm_vol_uL = rxn_vol_uL / 2
    max_dna_vol_uL = rxn_vol_uL - mm_vol_uL
    dna_vol_uL = int(args['--dna-volume'] or max_dna_vol_uL)

    # Get the fragments to assemble.

    if args['<fragments>'] and args['<fragments>'] != '-':
        frags = golden_gate.fragments_from_str(args['<fragments>'])
    else:
        frags = golden_gate.fragments_from_input()

    # Decide how much DNA of each fragment is needed.
    # https://www.neb.com/protocols/2012/09/25/gibson-assembly-master-mix-assembly#

    if len(frags) <= 3:
        max_pmol_per_frag = 0.5
        min_pmol_per_frag = 0.02
        incubation_time = '15 min'
    else:
        max_pmol_per_frag = 1
        min_pmol_per_frag = 0.2
        incubation_time = '1h'

    golden_gate.calc_fragment_volumes(
            frags,
            vol_uL=dna_vol_uL,
    )

    # Build the reaction table.
    
    gibson = dirty_water.Reaction()
    water_uL = max_dna_vol_uL

    for i, frag in enumerate(frags):
        # If possible, use the amount of DNA recommended by NEB.  Otherwise,
        # issue a warning and use as much as possible.
        target_uL = uL_from_pmol(max_pmol_per_frag, frag.conc.value)
        best_uL = min(frag.vol_uL, target_uL)
        best_pmol = pmol_from_uL(best_uL, frag.conc.value)
        water_uL -= best_uL

        if best_pmol < min_pmol_per_frag:
            print(f"Warning: Using {best_pmol:.3f} pmol of {frag.name}, {min_pmol_per_frag:.3f} pmol recommended.")
            print()

        gibson[frag.name].std_volume = best_uL, 'μL'
        gibson[frag.name].std_stock_conc = frag.conc.value, frag.conc.unit
        gibson[frag.name].master_mix = (
                ('bb' in args['--master-mix'])
                if i == 0 else
                ('ins' in args['--master-mix'] or f'{i+1}' in args['--master-mix'])
        )

    gibson['Gibson master mix (NEB E2611)'].std_volume = mm_vol_uL, 'μL'
    gibson['Gibson master mix (NEB E2611)'].master_mix = True

    if water_uL > 0:
        gibson['Water'].std_volume = water_uL, 'μL'
        gibson['Water'].master_mix = True

    # Display the protocol.

    import dirty_water

    protocol = dirty_water.Protocol()

    protocol += f"""\
Prepare the Gibson assembly reaction:

{gibson}"""

    protocol += f"""\
Incubate at 50°C for {incubation_time}."""

    protocol += f"""\
Dilute reaction 4x in water before transfroming 
into chemically competent cells (e.g. MACH1)."""

    print(protocol)

# vim: tw=50
