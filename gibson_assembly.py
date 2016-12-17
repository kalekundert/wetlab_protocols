#!/usr/bin/env python3

import sys, readline
import numpy as np
import numpy.linalg

print("""\
Please provide names, lengths (bp), and concentrations (ng/μL) for each 
fragment in the assembly.  Press Ctrl-D to finish, or Ctrl-C to abort.
""")
fragments = []

while True:
    try:
        frag_num = 'Fragment #{}'.format(len(fragments) + 1)
        print('%s name:' % frag_num, end=' ', file=sys.stderr)
        frag_name = input()
        print('%s size:' % frag_num, end=' ', file=sys.stderr)
        frag_size = float(input())
        print('%s conc:' % frag_num, end=' ', file=sys.stderr)
        frag_conc = float(input())
        fragments.append((frag_name, frag_size, frag_conc))
        print(file=sys.stderr)

    except ValueError as error:
        print('Error:', str(error).strip(':'), file=sys.stderr)
        print(file=sys.stderr)

    except EOFError:
        if len(fragments) < 2:
            print('Error: must provide at least two fragments', file=sys.stderr)
            print(file=sys.stderr)
        else:
            print(end='\r', file=sys.stderr)
            break

    except KeyboardInterrupt:
        print(file=sys.stderr)
        raise SystemExit

num_fragments = n = len(fragments)
num_equations = m = n + 1
names, molecular_weights, concentrations = zip(*fragments)
mw, cs = molecular_weights, concentrations 

# Construct the system of linear equations to solve 
# for the amount of each fragment to add to the 
# gibson.

A = np.zeros((m, m))

for i, c in enumerate(concentrations):
    A[i,i] = c / mw[i]

A[:,n] = -1
A[n,:] =  1
A[n,n] =  0

B = np.zeros((m, 1))
B[n] = 5

x = numpy.linalg.solve(A, B)

# Display the protocol.

import dirty_water

protocol = dirty_water.Protocol()

gibson = dirty_water.Reaction()
for i, name in enumerate(names):
    name = '{} ({} bp)'.format(name, mw[i])
    gibson[name].std_volume = x[i,0], 'μL'
    gibson[name].std_stock_conc = concentrations[i], 'ng/μL'
gibson['Gibson master mix'].std_volume = 15, 'μL'
gibson.show_master_mix = False

protocol += """\
Prepare the Gibson assembly reaction:

{gibson}"""

protocol += """\
Incubate at 50°C for 1h."""

protocol += """\
Transform 5 μL of the crude reaction mixture with 20 
μL chemically competent Top10 cells."""

print(protocol)

# vim: tw=53
