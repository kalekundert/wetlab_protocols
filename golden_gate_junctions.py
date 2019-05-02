#!/usr/bin/env python3

"""
Suggest 4-bp Golden Gate junction sequences that are likely to assemble 
successfully and in the correct order.

Usage:
    golden_gate_junctions.py <num> [<set>]

Arguments:
    <num>
        The number of junctions you need.  The set you choose must contain at 
        least this many junctions.

    <set>
        Which set of junction sequences to use.  Each is from a different 
        publication, but has been validated experimentally.  The options are:

        Potapov2018/37C (default, aka "neb")
            Up to 35 distinct junctions identified in a large-scale sequencing 
            experiment, for use in 1h 37°C assemblies.  Somewhat better 
            orthogonality can be achieved if fewer junctions are needed.  This 
            is the recommended set to use when only inserting a few fragments, 
            because the 37°C protocol is short and these junctions (unlike 
            MoClo or GoldenBraid) are specifically optimized for orthogonality.

        Potapov2018/16C (aka "neb/16")
            See Potapov2018/37, except these junctions are optimized for use in 
            5h cycled 16°C/37°C assemblies.  This is the recommended set to use 
            when inserting a large number of fragments, because the cycling 
            protocol is more robust.

        Potapov2018/MoClo (aka "neb/moclo")
            See Potapov2018/16C, except this set was explicitly designed to 
            include the standard MoClo junctions.  This is the recommended set 
            to use when working with MoClo parts.  If compatibility with MoClo 
            isn't important, use Potapov2018/37C or Potapov2018/16C instead.

        Weber2011 (aka "moclo")
            More commonly known as the MoClo system.  6 validated junctions, 
            two of which were chosen to match particular codons (start/Met and 
            Gly), the rest of which were just designed to be orthogonal.

        Iverson2016 (aka "moclo2")
            A variant of MoClo with 2 additional validated junctions, for a 
            total of 8.

        SarrionPerdigones2011 (aka "braid")
            More commonly known as GoldenBraid.  7 validated junctions, two of 
            which were design to encode start/stop codons, the rest of which 
            were designed to be orthogonal.

        SarrionPerdigones2013 (aka "braid2")
            More commonly known as GB2.0 (GoldenBraid 2.0).  15 validated 
            junctions, although I may have missed some because I didn't read 
            the paper that closely.  I'm also not sure what the connection to 
            GoldenBraid is (all the junctions are different).

        Note that all of the sets can be referred to either by a full name 
        (author/year for the relevant publication) or by a shorter alias.  A 
        fuzzy match is used to identify sets as well, so you can often get away 
        with typing just a few characters of whichever name you want.
"""

aliases = {
        'neb': 'Potapov2018/37C',
        '37': 'Potapov2018/37C',
        'neb/37': 'Potapov2018/37C',
        '16': 'Potapov2018/16C',
        'neb/16': 'Potapov2018/16C',
        'neb/moclo': 'Potapov2018/MoClo',
        'moclo': 'Weber2011',
        'moclo2': 'Iverson2016',
        'cidar': 'Iverson2016',
        'sarrion2011': 'SarrionPerdigones2011',
        'goldenbraid': 'SarrionPerdigones2011',
        'braid': 'SarrionPerdigones2011',
        'sarrion2013': 'SarrionPerdigones2013',
        'goldenbraid2': 'SarrionPerdigones2013',
        'braid2': 'SarrionPerdigones2013',
}
junctions = {
        'Potapov2018/16C': [
            ['AGTG', 'CAGG', 'ACTC', 'AAAA', 'AGAC', 'CGAA', 'ATAG', 'AACC', 'TACA', 'TAGA', 'ATGC', 'GATA', 'CTCC', 'GTAA', 'CTGA', 'ACAA', 'AGGA', 'ATTA', 'ACCG', 'GCGA'],
            ['CCTC', 'CTAA', 'GACA', 'GCAC', 'AATC', 'GTAA', 'TGAA', 'ATTA', 'CCAG', 'AGGA', 'ACAA', 'TAGA', 'CGGA', 'CATA', 'CAGC', 'AACG', 'AAGT', 'CTCC', 'AGAT', 'ACCA', 'AGTG', 'GGTA', 'GCGA', 'AAAA', 'ATGA'],
            ['TACA', 'CTAA', 'GGAA', 'GCCA', 'CACG', 'ACTC', 'CTTC', 'TCAA', 'GATA', 'ACTG', 'AACT', 'AAGC', 'CATA', 'GACC', 'AGGA', 'ATCG', 'AGAG', 'ATTA', 'CGGA', 'TAGA', 'AGCA', 'TGAA', 'ACAT', 'CCAG', 'GTGA', 'ACGA', 'ATAC', 'AAAA', 'AAGG', 'CAAC'],
        ],
        'Potapov2018/37C': [
            ['CTTA', 'CTCC', 'ACTA', 'GGTA', 'TCCA', 'CGAA', 'AATG', 'AGCG', 'ATGG', 'AGAT'],
            ['AGAG', 'ACAT', 'GACA', 'AGCA', 'AATC', 'GGTA', 'CAAA', 'CCAA', 'AACG', 'CTGA', 'CCTC', 'ACGG', 'TCCA', 'CAGC', 'ACTA'],
            ['GACA', 'ACTA', 'CGGA', 'ATTA', 'AGAG', 'AACG', 'CCAA', 'GGTA', 'CTGA', 'AGGA', 'CAGC', 'ACGG', 'CAAA', 'GAAC', 'AGAT', 'CCTC', 'CTAC', 'AGCA', 'AATC', 'ATGA'],
            ['AGCA', 'GACA', 'GTAA', 'CAGC', 'AATC', 'ATAG', 'GAAC', 'ATGA', 'AACT', 'CAAA', 'CTTC', 'CGTA', 'ATTA', 'CTGA', 'TCCA', 'ACTC', 'AATG', 'GCGA', 'ACAA', 'AGGG', 'CTCA', 'ACCG', 'CCAA', 'GGTA', 'AGAT'],
            ['GTAA', 'AAGT', 'ATAG', 'GAAA', 'CCAG', 'AATC', 'ATGA', 'GCAC', 'GGTA', 'CGTC', 'ACCG', 'ACAA', 'GCCA', 'AGGG', 'AATG', 'CAAC', 'AACT', 'CACA', 'AGCA', 'ATTA', 'CGAA', 'GAGA', 'CTTA', 'CCGA', 'ACGC', 'AGAT', 'CTCC', 'CAGA', 'CCTA', 'TCCA'],
            ['TCCA', 'AACT', 'CGTA', 'GTAA', 'AAGC', 'CCGA', 'GGGA', 'GCAA', 'ATAG', 'ATCC', 'AAGA', 'CCAG', 'ATGA', 'AATC', 'AGAA', 'ACAT', 'CAGA', 'CTCA', 'CCTA', 'ACGA', 'GACA', 'ATTA', 'AGAC', 'CAAA', 'GGTA', 'CGAA', 'CCAC', 'GAAC', 'AGGG', 'AATG', 'ACTA', 'CTTC', 'ACCG', 'ACTC', 'AGCA'],
        ],
        'Potapov2018/MoClo': [
            ['TGCC', 'GCAA', 'ACTA', 'TTAC', 'CAGA', 'TGTG', 'GAGC', 'AGGA', 'ATTC', 'CGAA', 'ATAG', 'AAGG', 'AACT', 'AAAA', 'ACCG'],
        ],
        'Weber2011': [
            ['GGAG', 'TACT', 'AATG', 'AGGT', 'GCTT', 'CGCT'],         # Level 1
            ['TGCC', 'GGCA', 'ACTA', 'TTAC', 'CAGA', 'TGTG', 'GAGC'], # Level 2
        ],
        'Iverson2016': [
            ['GGAG', 'TACT', 'AATG', 'AGGT', 'GCTT', 'CGCT', 'TGCC', 'ACTA'],
        ],
        'SarrionPerdigones2011': [
            ['CCAC', 'CGTC', 'GGCA', 'TGGC', 'CGAC', 'GATG', 'TGAG'],
        ],
        'SarrionPerdigones2013': [
            ['GGAG', 'TGAC', 'TCCC', 'TACT', 'CCAT', 'AATG', 'AGCC', 'TTCG', 'GCAG', 'GCTT', 'GGTA', 'CGCT', 'GTCA', 'CTCC', 'AGCG'],
        ],
}

if __name__== '__main__':
    import docopt, sys
    from textdistance import levenshtein
    from functools import partial

    args = docopt.docopt(__doc__)
    n = int(args['<num>'])

    # Decide which set the user asked for (using fuzzy matching):

    keys = list(aliases.keys()) + list(junctions.keys())
    by_edit_dist = partial(levenshtein, args['<set>'] or 'Potapov2018/37C')
    key = sorted(keys, key=by_edit_dist)[0]

    if key not in junctions:
        key = aliases.get(key, key)
        print(f"Info: Chose {key} based on similarity to '{args['<set>']}'.")

    # Find the smallest set with at least the requested number of junctions:
    
    smallest_set = None

    for set in junctions[key]:
        if len(set) < n:
            continue
        if smallest_set is None or len(set) < len(smallest_set):
            smallest_set = set

    if smallest_set is None:
        print(f"Error: {key} contains only {max(len(x) for x in junctions[key])} junctions, but {n} were requested.")
        sys.exit()

    # Print the junctions.

    print('\n'.join(smallest_set[:n]))



