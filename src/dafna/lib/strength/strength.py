from collections import defaultdict
import numpy as np
import regex
import random
import rstr, itertools
import re

from dafna.lib.strength import gqd_canonical
from dafna.lib.strength import gqd_tandem_repeats
from dafna.lib.strength.i_motif import i_motif_max_strength
from dafna.lib.strength.triplex import triplex_max_strength, triplex_max_strength_for_patterns
from dafna.lib.strength.hairpin import max_hairpin_strength


def replace_complimentary_symbol(string):
    repl = {'a': 't', 't': 'a', 'g': 'c', 'c': 'g'}
    replacement = dict((regex.escape(k), v) for k, v in repl.items())
    pattern = regex.compile("|".join(replacement.keys()))
    return "".join(list(pattern.sub(lambda m: replacement[regex.escape(m.group(0))], string)))


def generate_random_string(min_size, max_size):
    if min_size > max_size:
        raise ValueError
    return rstr.xeger(f'(a|c|g|t){min_size, max_size}')


def generate_random_strings(min_size, max_size, count):
    for i in range(count):
        yield generate_random_string(min_size, max_size)


def gqd_max_strength_naive(input_string):
    return max(gqd_canonical.gqd_max_strength_naive(input_string), gqd_tandem_repeats.max_strength(input_string))

def gqd_max_strength(input_string):
    return max(gqd_canonical.gqd_max_strength(input_string), gqd_tandem_repeats.max_strength(input_string))

def hairpin_max_strength(string):
    strength = 0
    n_count = '1,'
    m_count = '1,'
    pattern = \
        '({at_group})[a|t|g|c]{{0,3}}?({gc_group})[a|t|g|c]{{3,7}}({gc_complimentary_group})[a|t|g|c]{{0,3}}({at_complimentary_group})'
    start_pattern = '([a|t]{{{n_count}}})[a|t|g|c]{{{bubble_count}}}([g|c]{{{m_count}}})'
    match = []
    for i in range(0, 4):
        match += regex.findall(start_pattern.format(n_count=n_count, m_count=m_count, bubble_count=i), string)
    if any(match):
        for hairpin_head_part in match:
            for temp_start_pos in range(len(string)):
                temp_string = string[temp_start_pos:]
                n = len(hairpin_head_part[0])
                for i in range(n, 0, -1):
                    for bubble_count in range(0, 4):
                        sub_match = regex.findall(
                            start_pattern.format(n_count=i, m_count=m_count, bubble_count=bubble_count), temp_string)
                        if any(sub_match):
                            at_group, at_complimentary_group = sub_match[0][0], replace_complimentary_symbol(
                                sub_match[0][0][::-1])
                            gc_group, gc_complimentary_group = sub_match[0][1], replace_complimentary_symbol(
                                sub_match[0][1][::-1])
                            full_match = regex.findall(pattern.format(
                                gc_group=gc_group,
                                gc_complimentary_group=gc_complimentary_group,
                                at_group=at_group,
                                at_complimentary_group=at_complimentary_group
                            ),
                                temp_string
                            )

                            if any(full_match):
                                for match_case in full_match:
                                    temp_strength = len(match_case[0]) + len(match_case[2])
                                    strength = strength if strength > temp_strength else temp_strength
    return strength



def analyze_string(string, find_params):
    result = []
    if find_params[0] == True:
        result.append(gqd_max_strength(string))
    else:
        result.append(-1)
    if find_params[1] == True:
        result.append(i_motif_max_strength(string))
    else:
        result.append(-1)
    if find_params[2] > 0:
        # triplex_max_strength returns (strength, picture); keep only the scalar.
        result.append(triplex_max_strength(string)[0])
    else:
        result.append(-1)
    if find_params[3] == True:
        # Use the current recursive hairpin implementation (the module-level
        # hairpin_max_strength below is the older regex prototype).
        result.append(max_hairpin_strength(string))
    else:
        result.append(-1)
    return tuple(result)
