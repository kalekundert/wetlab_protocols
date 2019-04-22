#!/usr/bin/env python3

"""\
Usage:
    golden_gate.py <num_inserts> <num_reactions> [options]

Options:
    -e --enzymes <type_IIS>
        The name(s) of the Type IIS restriction enzyme(s) to use for the 
        reaction.  To use more than one enzyme, enter comma-separated names.  
        The default is to use a single generic name.

    -m, --master-mix <bb,ins>   [default: ""]
        Indicate which fragments should be included in the master mix.  Valid 
        fragments are "bb" (for the backbone), "ins" (for all the inserts), 
        "1" (for the first insert), etc.

    -q, --quick
        Use an shortened thermocycler protocol that completes in 1h, rather
        than 5h.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
num_inserts = int(args['<num_inserts>'])
enzymes = (args['--enzymes'] or 'Golden Gate enzyme').split(',')

golden_gate = dirty_water.Reaction()
golden_gate.num_reactions = int(args['<num_reactions>'])
golden_gate['Water'].std_volume = 7.0 - num_inserts * 0.5 - len(enzymes) * 0.5, 'μL'
golden_gate['Water'].master_mix = True
golden_gate['Backbone'].std_volume = 1.0, 'μL'
golden_gate['Backbone'].master_mix = 'bb' in args['--master-mix']

for i in range(num_inserts):
    name = f'Insert #{i+1}' if num_inserts > 1 else 'Insert'
    golden_gate[name].std_volume = 0.5, 'μL'
    golden_gate[name].master_mix = \
            'ins' in args['--master-mix'] or f'{i+1}' in args['--master-mix']

golden_gate['T4 ligase buffer'].std_volume = 1.0, 'μL'
golden_gate['T4 ligase buffer'].std_stock_conc = '10x'
golden_gate['T4 ligase buffer'].master_mix = True
golden_gate['T4 DNA ligase'].std_volume = 0.5, 'μL'
golden_gate['T4 DNA ligase'].std_stock_conc = 400, 'U/μL'
golden_gate['T4 DNA ligase'].master_mix = True
golden_gate['DpnI'].std_volume = 0.5, 'μL'
golden_gate['DpnI'].std_stock_conc = 20, 'U/μL'
golden_gate['DpnI'].master_mix = True
for enzyme in enzymes:
    golden_gate[enzyme].std_volume = 0.5, 'μL'
    golden_gate[enzyme].std_stock_conc = 10, 'U/μL'
    golden_gate[enzyme].master_mix = True

protocol = dirty_water.Protocol()

protocol += """\
Setup the Golden Gate reaction(s):

{golden_gate}
"""

protocol += f"""\
Run the following thermocycler protocol:

- Repeat 30 times:
    - 42°C for {'30 sec' if args['--quick'] else '5 min'}
    - 16°C for {'1 min' if args['--quick'] else '5 min'}
- 55°C for {'5 min' if args['--quick'] else '10 min'}
"""

protocol += """\
Transform all 10 μL of the Golden Gate reaction.
"""

protocol.notes += """\
There are two things worth noting about this 
protocol. The first is the restriction enzyme 
temperature. I was using BsmBI, which NEB 
recommends using at 55°C. In contrast, NEB 
recommends 37°C for most other golden gate 
enzymes, including BsaI, which is the most common 
Golden Gate enzyme. I was worried that the 
thermocycler protocols I was finding online were 
intended for BsaI, and that I should increase the 
temperature for BsmBI. However, the heat 
inactivation temperature for T4 ligase is 65°C, 
and I was also worried that 55°C was a little too 
close to that. I ended up using 42°C as 
recommended here:

http://barricklab.org/twiki/bin/view/Lab/ProtocolsGoldenGateAssembly

The second thing worth noting is the length of the 
two temperature steps.  Most protocols I found 
online hold each step for 5 min, but Anum cuts 
this down for simple assemblies.
"""

print(protocol)

# vim: tw=50

