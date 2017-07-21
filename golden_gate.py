#!/usr/bin/env python3

"""\
Usage:
    golden_gate.py <num_inserts> <num_reactions> [options]

Options:
    -e --enzyme <type_IIS>
        The name of the Type IIS restriction enzyme to use for the reaction.  
        The default is to use a generic name.
"""

import docopt
import dirty_water

args = docopt.docopt(__doc__)
num_inserts = int(args['<num_inserts>'])
enzyme = args['--enzyme'] or 'Golden Gate enzyme'

golden_gate = dirty_water.Reaction()
golden_gate.num_reactions = args['<num_reactions>']
golden_gate['Water'].std_volume = 7 - num_inserts * 0.5, 'μL'
golden_gate['Backbone'].std_volume = 1.0, 'μL'

for i in range(num_inserts):
    name = f'Insert #{i+1}' if num_inserts > 1 else 'Insert'
    golden_gate[name].std_volume = 0.5, 'μL'

golden_gate['T4 ligase buffer'].std_volume = 1.0, 'μL'
golden_gate['T4 ligase buffer'].std_stock_conc = '10x'
golden_gate['T4 DNA ligase'].std_volume = 0.5, 'μL'
golden_gate['T4 DNA ligase'].std_stock_conc = 400, 'U/μL'
golden_gate[enzyme].std_volume = 0.5, 'μL'
golden_gate[enzyme].std_stock_conc = 10, 'U/μL'

protocol = dirty_water.Protocol()

protocol += """\
Setup the Golden Gate reaction:

{golden_gate}
"""

protocol += f"""\
Run the following thermocycler protocol:

(a) 42°C for 30 sec.
(b) 16°C for 1 min.
(c) Repeat steps (a) and (b) 30 times.
(d) 55°C for 5 min.
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

