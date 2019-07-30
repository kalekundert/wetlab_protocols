#!/usr/bin/env python3

"""\
Perform a Golden Gate assembly reaction.

Usage:
    golden_gate.py [<fragments>] [<num_reactions>] [options]

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
    -e --enzymes <type_IIS>
        The name(s) of the Type IIS restriction enzyme(s) to use for the 
        reaction.  To use more than one enzyme, enter comma-separated names.  
        The default is to use a single generic name.

    -m, --master-mix <bb,ins>  [default: ""]
        Indicate which fragments should be included in the master mix.  Valid 
        fragments are "bb" (for the backbone), "ins" (for all the inserts), 
        "1" (for the first insert), etc.

    -v, --reaction-volume <µL>  [default: 10]
        The volume of the complete Golden Gate reaction.  You might want bigger 
        reaction volumes if your DNA is dilute, or if you have a large number 
        of inserts.
        
    -d, --dna-volume <µL>
        The combined volume of backbone and insert DNA to use, in µL.  The 
        default is use the as much volume as possible, i.e. the full reaction 
        volume (see --reaction-volume) less the volumes of any enzymes and 
        buffers.  You might want to use less DNA if you're trying to conserve 
        material.

    -x, --excess-insert <ratio>  [default: 2]
        The fold-excess of each insert relative to the backbone.  The default 
        specifies that there will be twice as much of each insert as there 
        is backbone.
"""

import docopt
import dirty_water
from dataclasses import dataclass

def fragments_from_str(arg):
    """
    Parse fragments from a comma- and colon-separated string, i.e. that could 
    be specified on the command-line.

    See the usage text for a description of the syntax of this string.

    Note that if only two fields are specified, they could refer to a name and 
    a concentration, or a concentration and a size.  This is resolved by 
    attempting to interpret each field as a concentration.  Note that this will 
    break if given a name that could be interpreted as a concentration, so 
    don't do that.
    """

    fragments = []
    frag_strs = arg.split(':')

    if len(frag_strs) < 2:
        raise ValueError("must specify at least two fragments")

    for i, frag_str in enumerate(frag_strs):
        fields = frag_str.split(',')
        frag_name = default_fragment_name(i)
        frag_size = None

        if len(fields) == 3:
            frag_name = fields[0]
            frag_conc = conc_from_str(fields[1])
            frag_size = int(fields[2])

        elif len(fields) == 2:
            # Is this (name, conc) or (conc, size)?
            try:
                frag_conc = conc_from_str(fields[0])
                frag_size = int(fields[1])

            except ValueError:
                frag_name = fields[0]
                frag_conc = conc_from_str(fields[1])

        elif len(fields) == 1:
            frag_conc = conc_from_str(fields[0])

        else:
            raise ValueError("cannot parse fragment '{fragment_str}'")

        if frag_conc.unit == 'ng/µL' and frag_size is None:
            raise ValueError(f"'{frag_str}' specifies a concentration in ng/µL, so the size of the fragment must also be specified (e.g. '{frag_str},<size>')")

        frag_nM = nM_from_conc(frag_conc, frag_size)
        frag = Fragment(frag_name, frag_nM)
        frag.conc = frag_conc
        fragments.append(frag)

    return fragments

def fragments_from_input():
    import sys
    from builtins import print
    from functools import partial

    print = partial(print, file=sys.stderr)
    print("""\
Please provide names and concentrations for each fragment in the assembly, 
beginning with the backbone.  Concentrations are assumed to be in ng/µL, unless 
a unit is specified.  If necessary, you will be asked for the length of the 
insert.  Press Ctrl-D to finish, or Ctrl-C to abort.
    """)

    fragments = []

    while True:
        try:
            frag_name = default_fragment_name(len(fragments))
            print(f"{frag_name}:")
            print(f"  Name [optional]: ", end="")
            frag_name = input() or frag_name

            print(f"  Concentration: ", end="")
            frag_conc = conc_from_str(input())
            frag_size = None

            if frag_conc.unit == 'ng/µL':
                print(f"  Size [bp]: ", end="")
                frag_size = int(input())

            frag_nM = nM_from_conc(frag_conc, frag_size)

            frag = Fragment(frag_name, frag_nM)
            frag.conc = frag_conc
            fragments.append(frag)
            print()

        except ValueError as error:
            print("Error:", str(error).strip(':'))
            print()

        except EOFError:
            if len(fragments) < 2:
                print("Error: must provide at least two fragments")
                print()
            else:
                print(end='\r')
                break

        except KeyboardInterrupt:
            print()
            raise SystemExit

    return fragments

def calc_fragment_volumes(frags, vol_uL=5, excess_insert=2):
    import numpy as np

    num_fragments = n = len(frags)
    num_equations = m = n + 1

    # Construct the system of linear equations to 
    # solve for the amount of each fragment to add 
    # to the reaction.

    A = np.zeros((m, m))

    for i, f in enumerate(frags):
        A[i,i] = f.conc_nM

    A[:,n] =  excess_insert
    A[0,n] =  1
    A[n,:] =  1
    A[n,n] =  0

    B = np.zeros((m, 1))
    B[n] = vol_uL

    x = np.linalg.solve(A, B)

    for i, f in enumerate(frags):
        f.vol_uL = x[i,0]


def default_fragment_name(i):
    return "Backbone" if i == 0 else f"Insert #{i}"

def conc_from_str(x):
    import re

    if x.upper().strip() == 'PCR':
        return Concentration(50, 'ng/µL')

    value_pattern = '[0-9.]+'
    unit_pattern = 'ng/[uµ]L|[muµnpf]M'
    conc_pattern = rf'({value_pattern})(\s*({unit_pattern}))?$'

    match = re.match(conc_pattern, x.strip())
    if not match:
        raise ValueError(f"could not interpret '{x}' as a concentration.")

    value, _, unit = match.groups()
    unit = (unit or 'ng/µL').replace('u', 'µ')
    return Concentration(float(value), unit)

def nM_from_conc(conc, num_bp):
    multiplier = {
            'mM': 1e9 / 1e3,
            'µM': 1e9 / 1e6,
            'nM': 1e9 / 1e9,
            'pM': 1e9 / 1e12,
            'fM': 1e9 / 1e15,
    }

    # https://www.neb.com/tools-and-resources/usage-guidelines/nucleic-acid-data
    if num_bp:
        multiplier['ng/µL'] = 1e6 / (650 * num_bp)

    try:
        return conc.value * multiplier[conc.unit]
    except KeyError:
        raise ValueError(f"cannot convert '{conc.unit}' to nM.")

@dataclass
class Fragment:
    name: str
    conc_nM: float
    vol_uL: float = None

@dataclass
class Concentration:
    value: float
    unit: str

def test_conc_from_str():
    from pytest import approx, raises
    c = Concentration

    assert conc_from_str('1') == c(1.0, 'ng/µL')
    assert conc_from_str('10') == c(10.0, 'ng/µL')
    assert conc_from_str('1.0') == c(1.0, 'ng/µL')
    assert conc_from_str('1 ng/uL') == c(1.0, 'ng/µL')
    assert conc_from_str('1 ng/µL') == c(1.0, 'ng/µL')
    assert conc_from_str('1 fM') == c(1.0, 'fM')
    assert conc_from_str('1 pM') == c(1.0, 'pM')
    assert conc_from_str('1 nM') == c(1.0, 'nM')
    assert conc_from_str('1 uM') == c(1.0, 'µM')
    assert conc_from_str('1 µM') == c(1.0, 'µM')

    assert conc_from_str(' 1 ') == c(1.0, 'ng/µL')
    assert conc_from_str(' 1 nM') == c(1.0, 'nM')
    assert conc_from_str('1 nM ') == c(1.0, 'nM')
    assert conc_from_str(' 1  nM ') == c(1.0, 'nM')

    assert conc_from_str('PCR') == c(50.0, 'ng/µL')
    assert conc_from_str('pcr') == c(50.0, 'ng/µL')

    with raises(ValueError, match="''"):
        conc_from_str('')
    with raises(ValueError, match='xxx'):
        conc_from_str('1 xxx')

def test_nM_from_conc():
    from pytest import approx, raises
    c = Concentration

    assert nM_from_conc(c(1, 'mM'), None) == approx(1e6)
    assert nM_from_conc(c(1, 'µM'), None) == approx(1e3)
    assert nM_from_conc(c(1, 'nM'), None) == approx(1e0)
    assert nM_from_conc(c(1, 'pM'), None) == approx(1e-3)
    assert nM_from_conc(c(1, 'fM'), None) == approx(1e-6)

    assert nM_from_conc(c(1, 'ng/µL'), 100) == approx(1e6/(650 * 100))
    assert nM_from_conc(c(1, 'ng/µL'), 1000) == approx(1e6/(650 * 1000))

def test_fragments_from_str():
    from pytest import approx, raises
    f = Fragment

    ## 0 fragments
    with raises(ValueError):
        fragments_from_str('')

    ## 1 fragment
    with raises(ValueError):
        fragments_from_str('30nM')

    ## 2 fragments
     # 3 arguments
    assert fragments_from_str('30nM:Gene,60,1000') == [
            f('Backbone', 30),
            f('Gene', approx((60 * 1e6) / (650 * 1000))),
    ]
     # 2 arguments: name, conc
    assert fragments_from_str('30nM:Gene,60nM') == [
            f('Backbone', 30),
            f('Gene', 60),
    ]
    with raises(ValueError):
        fragments_from_str('30nM:Gene,60')

     # 2 arguments: conc, size
    assert fragments_from_str('30nM:60,1000') == [
            f('Backbone', 30.0),
            f('Insert #1', approx((60 * 1e6) / (650 * 1000))),
    ]
     # 1 argument: conc
    assert fragments_from_str('30nM:60nM') == [
            f('Backbone', 30),
            f('Insert #1', 60),
    ]
    with raises(ValueError):
        fragments_from_str('30nM:60')

    ## 3 fragments
    assert fragments_from_str('30nM:60nM:61nM') == [
            f('Backbone', 30),
            f('Insert #1', 60),
            f('Insert #2', 61),
    ]


if __name__ == '__main__':
    args = docopt.docopt(__doc__)

    # Work out the volumes specified in the arguments.
    enzymes = (args['--enzymes'] or 'Golden Gate enzyme').split(',')
    rxn_vol_uL = int(args['--reaction-volume'])
    max_dna_vol_uL = rxn_vol_uL - 1.5 - len(enzymes) * 0.5
    dna_vol_uL = int(args['--dna-volume'] or max_dna_vol_uL)

    if dna_vol_uL > max_dna_vol_uL:
        raise ValueError(f"Cannot fit {dna_vol_uL} µL of DNA in a {rxn_vol_uL} µL reaction.")

    if args['<fragments>'] and args['<fragments>'] != '-':
        frags = fragments_from_str(args['<fragments>'])
    else:
        frags = fragments_from_input()

    calc_fragment_volumes(
            frags,
            vol_uL=dna_vol_uL,
            excess_insert=float(args['--excess-insert']),
    )

    # Create the reaction table.
    golden_gate = dirty_water.Reaction()
    golden_gate.num_reactions = int(args['<num_reactions>'] or 1)

    if dna_vol_uL != max_dna_vol_uL:
        golden_gate['Water'].std_volume = max_dna_vol_uL - dna_vol_uL, 'µL'
        golden_gate['Water'].master_mix = True

    for i, frag in enumerate(frags):
        golden_gate[frag.name].std_volume = frag.vol_uL, 'µL'
        golden_gate[frag.name].std_stock_conc = frag.conc.value, frag.conc.unit
        golden_gate[frag.name].master_mix = (
                ('bb' in args['--master-mix'])
                if i == 0 else
                ('ins' in args['--master-mix'] or f'{i+1}' in args['--master-mix'])
        )

    golden_gate['T4 ligase buffer'].std_volume = 1.0, 'μL'
    golden_gate['T4 ligase buffer'].std_stock_conc = '10x'
    golden_gate['T4 ligase buffer'].master_mix = True

    golden_gate['T4 DNA ligase'].std_volume = 0.5, 'μL'
    golden_gate['T4 DNA ligase'].std_stock_conc = 400, 'U/μL'
    golden_gate['T4 DNA ligase'].master_mix = True

    for enzyme in enzymes:
        golden_gate[enzyme].std_volume = 0.5, 'μL'
        golden_gate[enzyme].master_mix = True

    # Create the protocol.
    protocol = dirty_water.Protocol()

    protocol += """\
Setup the Golden Gate reaction(s):

{golden_gate}
"""

    if len(frags) == 2:
        protocol += f"""\
Run the following thermocycler protocol:

- 37°C for 5 min

Or, to maximize the number of transformants:

- 37°C for 60 min
- 60°C for 5 min
"""
    elif len(frags) <= 4:
        protocol += f"""\
Run the following thermocycler protocol:

- 37°C for 60 min
- 60°C for 5 min
"""
    elif len(frags) <= 10:
        protocol += f"""\
Run the following thermocycler protocol:

- Repeat 30 times:
  - 37°C for 1 min
  - 16°C for 1 min
- 60°C for 5 min
"""
    else:
        protocol += f"""\
Run the following thermocycler protocol:

- Repeat 30 times:
  - 37°C for 5 min
  - 16°C for 5 min
- 60°C for 5 min
"""

    protocol.notes += """\
https://international.neb.com/protocols/2018/10/02/golden-gate-assembly-protocol-for-using-neb-golden-gate-assembly-mix-e1601
"""

    print(protocol)

# vim: tw=50

