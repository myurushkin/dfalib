from collections import defaultdict
import numpy as np
import regex

import rstr


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


def gqd_max_strength(string):
    gqd_pattern = \
        '(((((g(a|c|t){{0,4}}){{{n_subtraction_one}}}g)(a|c|t|g)+)){{3}}(g(a|c|t){{0,4}}){{{n_subtraction_one}}}g)'
    whole_g_groups = [len(g_group) for g_group in regex.findall(r'g{2,}', string)]
    whole_g_groups.sort(reverse=True)

    for n in whole_g_groups:
        temp_pattern = gqd_pattern.format(n_subtraction_one=n - 1)
        match_sub_str = regex.findall(temp_pattern, string)
        a = [regex.findall(f'g{{{n}}}', sub_str[0]) for sub_str in match_sub_str]
        if match_sub_str and any([regex.findall(f'g{{{n}}}', sub_str[0]) for sub_str in match_sub_str]):
            return n
    return 0


def i_motif_max_strength(string, biological_significance: bool = False):
    x_group = '[a|c|g|t]'
    y_symbol = '[t|c]'
    n = '3,'
    m = '1,'
    strength = 0
    biological_significance_pattern = '((c{{{n}}}){X}{{3,}}?(c{{{m}}}){X}{{3,}}?()\\2{X}{{3,}}?()\\3)'
    no_biological_significance_pattern = '({Y}(c{{1,}})g{X}{{2}}{Y}(c{{1,}})g{X}{{1}}{Y}()\\2g{X}{{2}}{Y}()\\3g)'
    if biological_significance:
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
    else:
        pattern = no_biological_significance_pattern.format(Y=y_symbol, X=x_group)
        match = regex.findall(pattern, string)
        if any(match):
            for i_motif in match:
                sub_strength = (len(i_motif[1]) + len(i_motif[2])) / 2
                strength = strength if strength > sub_strength else sub_strength

    return strength


def triplex_max_strength(string):
    x_group = '[a|c|g|t]'
    triplex_forms = [
        '{A}{{{count}}}{X}{{4,}}{C}{{{count}}}{X}{{3,}}{B}{{{count}}}',
        '{A}{{{count}}}{X}{{3,}}{B}{{{count}}}{X}{{3,}}{C}{{{count}}}',
    ]
    triplex_groups_options = [
        {'A': '[t|c]', 'B': 'a', 'C': 't'},
        {'A': '[c|g|a]', 'B': 'g', 'C': 'c'},
        {'A': 'g', 'B': 't', 'C': 'a'},
        {'A': '[t|c]', 'B': 'c', 'C': 'g'},
    ]
    strength = 0
    for triplex_form in triplex_forms:
        groups = '({item}{{1,}})'
        for triplex_item in triplex_groups_options:
            b_match = regex.findall(groups.format(item=triplex_item['B']), string)
            c_match = regex.findall(groups.format(item=triplex_item['C']), string)
            if c_match and b_match:
                start_count_n = min(
                    [max([len(b_gr) for b_gr in b_match]), max([len(c_gr) for c_gr in c_match])]
                )
                for i in range(start_count_n, 1, -1):
                    triplex_match = regex.findall(
                        triplex_form.format(count=i, X=x_group, A=triplex_item['A'], B=triplex_item['B'],
                                            C=triplex_item['C']), string)
                    if any(triplex_match):
                        strength = strength if strength > i else i

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
        result.append(triplex_max_strength(string))
    else:
        result.append(-1)
    if find_params[3] == True:
        result.append(hairpin_max_strength(string))
    else:
        result.append(-1)
    return tuple(result)
