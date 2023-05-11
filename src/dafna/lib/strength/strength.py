from collections import defaultdict
import numpy as np
import regex
import random
import rstr, itertools
import re

from dafna.lib.strength import gqd_canonical
from dafna.lib.strength import gqd_tandem_repeats


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



def i_motif_max_strength(string, biological_significance: bool = False):
    x_group = '[a|c|g|t]'
    y_symbol = '[t|c]'
    n = '1,'
    m = '1,'
    strength = 0
    biological_significance_pattern = '((c{{{n}}}){X}{{1,}}?(c{{{m}}}){X}{{1,}}?()\\2{X}{{1,}}?()\\3)'
    pattern = biological_significance_pattern.format(Y=y_symbol, X=x_group, n=n, m=m)
    match = regex.findall(pattern, string)
    if any(match):
        for i_motif in match:
            sub_strength = (len(i_motif[1]) + len(i_motif[2])) / 2
            for i in range(3, len(i_motif[1]) + 1):
                sub_match = regex.findall(
                    biological_significance_pattern.format(Y=y_symbol, X=x_group, n=i, m=m), string)[0]
                if any(sub_match):
                    temp_strength = (len(sub_match[1]) + len(sub_match[2])) / 2
                    sub_strength = sub_strength if sub_strength > temp_strength else temp_strength

            strength = strength if strength > sub_strength else sub_strength

    return strength


def triplex_max_strength_for_patterns(val, patterns, dir):
    result = 0
    value = val.lower()
    for strength in range(1, len(value)):
        for indent in range(len(value)):
            for linker_first_size in range(3, len(value)):
                for linker_second_size in range(3, len(value)):
                    if indent + 3 * strength + linker_first_size + linker_second_size > len(value):
                        break

                    A = value[indent:indent+strength]
                    B = value[indent+strength+linker_first_size:indent+strength+linker_first_size+strength]
                    C = value[indent + strength + linker_first_size + strength + linker_second_size: indent + strength + linker_first_size + strength + linker_second_size + strength]

                    assert len(B) == strength

                    check = False
                    for i in range(strength):
                        for p in patterns:
                            if A[i] != p[0]:
                                continue
                            if dir == 1:
                                if B[len(B) - i - 1] != p[1]:
                                    continue
                                if C[i] != p[2]:
                                    continue
                            else:
                                if B[len(B) - i - 1] != p[2]:
                                    continue
                                if C[i] != p[1]:
                                    continue
                            check = True
                            break

                        if check == False:
                            break
                    if check == True:
                        result = max(result, strength)
                        break
                if result == strength:
                    break
            if result == strength:
                break
        if result != strength:
            break
    return result

def triplex_max_strength(val):
    patterns_first = [
        'tat', 'cat', 'cgc', 'ggc', 'agc', 'gta', 'tcg', 'ccg'
    ]

    # patterns_second = [
    #     'tta', 'cta', 'ccg', 'gcg', 'acg', 'gat', 'tgc', 'cgc'
    # ]

    return max(*[triplex_max_strength_for_patterns(val, patterns_first, dir=1),
                  triplex_max_strength_for_patterns(val[::-1], patterns_first, dir=1),
                 triplex_max_strength_for_patterns(val, patterns_first, dir=-1),
                 triplex_max_strength_for_patterns(val[::-1], patterns_first, dir=-1)])



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
        result.append(triplex_max_strength(string))
    else:
        result.append(-1)
    if find_params[3] == True:
        result.append(hairpin_max_strength(string))
    else:
        result.append(-1)
    return tuple(result)
