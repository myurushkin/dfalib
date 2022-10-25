from collections import defaultdict
import numpy as np
import regex
import random
import rstr, itertools


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


def gqd_max_strength_naive(input_string):
    positions = []
    g_count = [0] * len(input_string)
    for i in range(len(input_string)):
        if input_string[i] == 'g':
            positions.append(i)
        g_count[i] = 1 if input_string[i] == 'g' else 0
        if i > 0:
            g_count[i] += g_count[i-1]

    best_strength = 0
    for pos in list(itertools.combinations(positions, 8)):
        pos = sorted(pos)
        good = True
        bubble_count = 0
        strength = 1000
        for i in range(4):
            group_strength = g_count[pos[i * 2 + 1]] - g_count[pos[i * 2]] + 1
            strength = min(strength, group_strength)
            if group_strength < 2:
                good = False
                break
            assert group_strength <= pos[i * 2 + 1] - pos[i * 2] + 1

            bubble_count_in_group = 0
            for k in range(pos[i * 2] + 1, pos[i * 2 + 1] + 1):
                if input_string[k] == 'g' and input_string[k-1] != 'g':
                    bubble_count_in_group += 1

            if bubble_count_in_group > 1:
                good = False
                break

            if bubble_count_in_group == 1:
                bubble_count += 1

            if i > 0 and pos[i*2] == pos[(i-1)*2+1] + 1:
                good = False
                break

        if good == True and bubble_count <= 3:
            best_strength = max(strength, best_strength)
    return best_strength


def gqd_max_strength(input_string):
    total_g_count = input_string.count('g')
    max_group_size_estimate = total_g_count // 4
    min_possible_group_size = 2
    max_bubble_count = 3
    group_count_in_gqd = 4
    g_seqs = [len(g_group) for g_group in regex.findall(r'g+', input_string)]

    def check_str(filled_g_group_count, bubble_count, current_seq, used_g_in_seq_count):
        if bubble_count > max_bubble_count:
            return False
        if filled_g_group_count >= group_count_in_gqd:
            return True
        if current_seq >= len(g_seqs):
            return False
        rest = g_seqs[current_seq] - used_g_in_seq_count
        assert rest > 0

        if group_size <= rest:
            if group_size + 1 < rest:
                return check_str(filled_g_group_count + 1, bubble_count, current_seq, used_g_in_seq_count + group_size + 1)
            else:
                return check_str(filled_g_group_count + 1, bubble_count, current_seq + 1, 0)
        else:
            if current_seq + 1 >= len(g_seqs):
                return False

            if g_seqs[current_seq + 1] - (group_size - rest) >= 0:
                if filled_g_group_count + 1 >= group_count_in_gqd and bubble_count + 1 <= max_bubble_count:
                    return True

                if g_seqs[current_seq + 1] - (group_size - rest) > 1:
                    if check_str(filled_g_group_count + 1,
                                    bubble_count + 1,
                                    current_seq + 1,
                                    (group_size - rest) + 1):
                        return True
                else:
                    if check_str(filled_g_group_count + 1,
                                    bubble_count + 1,
                                    current_seq + 2,
                                    0):
                        return True

            return check_str(filled_g_group_count, bubble_count, current_seq + 1, 0)
        raise Exception("Control flow error")

    for group_size in range(max_group_size_estimate, min_possible_group_size - 1, -1):
        if check_str(filled_g_group_count=0, bubble_count=0, current_seq=0, used_g_in_seq_count=0):
            return group_size
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
