from collections import defaultdict
import numpy as np
import regex

import rstr


def get_triplex_set(kind=1):
    assert kind == 1 or kind == 2
    if kind == 1:
        return ['tac', 'taa', 'tag', 'cgg', 'atg', 'cgt', 'cga', 'cgc', 'tat']
    return ['cat', 'agc', 'cgc', 'gat', 'ggc', 'tgc', 'tat', 'gta', 'aat']


def generate_random_string(min_size, max_size):
    if min_size > max_size:
        raise ValueError
    return rstr.xeger(f'(a|c|g|t){min_size, max_size}')


def generate_random_strings(min_size, max_size, count):
    for i in range(count):
        yield generate_random_string(min_size, max_size)


def is_complimentary_strings(ga_string, other_string, reverse_complimentary=False):
    if len(ga_string) != len(other_string):
        return False
    for i in range(len(ga_string)):
        left_letter = ga_string[i]
        right_letter = other_string[i] if not reverse_complimentary else other_string[-i - 1]
        if left_letter == 'a' and right_letter != 't':
            return False
        if left_letter == 't' and right_letter != 'a':
            return False
        if left_letter == 'g' and right_letter != 'c':
            return False
        if left_letter == 'c' and right_letter != 'g':
            return False
    return True


def is_weak_complimentary_strings(ga_string, other_string, reverse_complimentary=False):
    if len(ga_string) != len(other_string):
        return False
    for i in range(len(ga_string)):
        left_letter = ga_string[i]
        right_letter = other_string[i] if not reverse_complimentary else other_string[-i - 1]
        if left_letter == 'a' and right_letter != 't' and right_letter != 'a':
            return False
        if left_letter == 'g' and right_letter != 'g' and right_letter != 'a':
            return False
        if left_letter == 'c' or right_letter == 'c':
            return False
        if left_letter == 't':
            return False
    return True


def hairpin_strength(hairpin, tail_left):
    max_strength = 0
    max_head_size = 0
    for j in range(3, len(hairpin) - tail_left):
        head_size = j
        strength = 0
        tail_center_right = tail_left + head_size + 1
        tail_size = min(tail_left + 1, len(hairpin) - tail_center_right)

        for i in range(tail_size):
            if hairpin[tail_left - i] == 'a' and hairpin[tail_center_right + i] == 't':
                strength += 1
            elif hairpin[tail_left - i] == 't' and hairpin[tail_center_right + i] == 'a':
                strength += 1
            elif hairpin[tail_left - i] == 'c' and hairpin[tail_center_right + i] == 'g':
                strength += 1
            elif hairpin[tail_left - i] == 'g' and hairpin[tail_center_right + i] == 'c':
                strength += 1
        if strength > max_strength:
            max_strength = strength
            max_head_size = head_size
    return max_strength, max_head_size


def max_hairpin_strength(string):
    cw = 0
    max_i = 0
    max_head_size = 0
    for i in range(len(string)):
        cw_new, new_head_size = hairpin_strength(string, i)
        if cw_new > cw:
            max_head_size = new_head_size
            max_i = i
            cw = cw_new
    #    print("head_start: {}".format(max_i + 1))
    #    print("head_size: {}".format(max_head_size))
    return cw


def gqd_max_strength(string):
    gqd_pattern = \
        '(((((g(a|c|t){{0,4}}){{{n_subtraction_one}}}g)(a|c|t|g)+)){{3}}(g(a|c|t){{0,4}}){{{n_subtraction_one}}}g)'
    whole_g_groups = [len(g_group) for g_group in re.findall(r'g{2,}', string)]
    whole_g_groups.sort(reverse=True)

    for n in whole_g_groups:
        temp_pattern = gqd_pattern.format(n_subtraction_one=n - 1)
        match_sub_str = regex.findall(temp_pattern, string)
        a = [regex.findall(f'g{{{n}}}', sub_str[0]) for sub_str in match_sub_str]
        if match_sub_str and any([regex.findall(f'g{{{n}}}', sub_str[0]) for sub_str in match_sub_str]):
            return n
    return 0


def max_imotiv_stength(input_string):
    # first_group = [0.. cursor_left)
    # second_group = [cursor_left+1, cursor_central)
    # third_group = [cursor_central+2, cursor_right)
    # last_group = [cursor_right+1, len(string))
    result = 0

    counts = np.zeros(len(input_string) + 1, dtype=np.int)
    for i, c in enumerate(input_string):
        counts[i + 1] = counts[i]
        if c == 'c':
            counts[i + 1] += 1

    def cnt(begin, end):
        if begin >= end:
            return 0
        return counts[end] - counts[begin]

    for cursor_central in range(len(input_string)):
        for cursor_left in range(cursor_central):
            for cursor_right in range(cursor_central, len(input_string)):
                left_group_size = cnt(0, cursor_left)
                second_group_size = cnt(cursor_left + 1, cursor_central)
                third_group_size = cnt(cursor_central + 2, cursor_right)
                last_group_size = cnt(cursor_right + 1, len(input_string))

                if min([left_group_size, second_group_size, third_group_size, last_group_size]) == 0:
                    continue
                direct = min(left_group_size, third_group_size) + min(second_group_size, last_group_size)
                inverse = min(left_group_size, last_group_size) + min(second_group_size, third_group_size)
                result = max([result, direct, inverse])
    return result


def is_triplex(left_part, center_part, right_part, case):
    if case == "left":
        # yry
        if is_complimentary_strings(left_part, center_part) \
                and is_complimentary_strings(left_part, right_part, reverse_complimentary=True):
            return True
        # yrr
        if is_complimentary_strings(left_part, center_part) \
                and is_weak_complimentary_strings(left_part, right_part):
            return True
    if case == "center":
        # yry
        if is_complimentary_strings(center_part, left_part, reverse_complimentary=True) \
                and is_complimentary_strings(center_part, right_part, reverse_complimentary=True):
            return True
        # yrr
        if is_complimentary_strings(center_part, left_part, reverse_complimentary=True) \
                and is_weak_complimentary_strings(center_part, right_part, reverse_complimentary=True):
            return True
    if case == "right":
        # yry
        if is_complimentary_strings(right_part, center_part, reverse_complimentary=True) \
                and is_complimentary_strings(right_part, left_part):
            return True
        # yrr
        if is_complimentary_strings(right_part, center_part, reverse_complimentary=True) \
                and is_weak_complimentary_strings(right_part, left_part):
            return True
    return False


def max_triplex_strength(string):
    max_strength = 0
    ag_set = {'a', 'g'}
    a_set = {'a'}
    g_set = {'g'}

    cash_dict = defaultdict(lambda: defaultdict(str))
    for i in range(len(string)):
        for j in range(i + 1, len(string)):
            cash_dict[i][j] = string[i:j]

    for i in range(len(string)):
        for j in range(i + 1, len(string)):
            candidate = cash_dict[i][j]
            set_candidate = set(candidate)
            if set_candidate != ag_set and set_candidate != a_set and set_candidate != g_set:
                continue

            candidate_len = len(candidate)
            for x in range(3, len(string)):
                for y in range(3, len(string)):
                    # center case:

                    left_end = i - x
                    left_start = i - x - candidate_len
                    right_start = i + candidate_len + y
                    right_end = i + 2 * candidate_len + y

                    left_part = cash_dict[left_start][left_end]
                    right_part = cash_dict[right_start][right_end]
                    center_part = candidate
                    if is_triplex(left_part, center_part, right_part, "center"):
                        max_strength = max(max_strength, candidate_len)
                        continue
                    if is_triplex(right_part[::-1], center_part[::-1], left_part[::-1], "center"):
                        max_strength = max(max_strength, candidate_len)
                        continue

                    # left_case:
                    center_start = i + candidate_len + x
                    center_end = i + 2 * candidate_len + x
                    right_start = center_end + y
                    right_end = center_end + y + candidate_len
                    left_part = candidate
                    center_part = cash_dict[center_start][center_end]
                    right_part = cash_dict[right_start][right_end]
                    if is_triplex(left_part, center_part, right_part, "left"):
                        max_strength = max(max_strength, candidate_len)
                        continue
                    if is_triplex(right_part[::-1], center_part[::-1], left_part[::-1], "left"):
                        max_strength = max(max_strength, candidate_len)
                        continue
                    # right case
                    center_start = i - candidate_len - x
                    center_end = center_start + candidate_len
                    left_start = center_start - y - candidate_len
                    left_end = left_start + candidate_len
                    center_part = cash_dict[center_start][center_end]
                    left_part = cash_dict[left_start][left_end]
                    right_part = candidate
                    if is_triplex(left_part, center_part, right_part, "right"):
                        max_strength = max(max_strength, candidate_len)
                        continue
                    if is_triplex(right_part[::-1], center_part[::-1], left_part[::-1], "right"):
                        max_strength = max(max_strength, candidate_len)
                        continue
    return max_strength


def analyze_string(string, find_params):
    result = []
    if find_params[0] == True:
        result.append(max_gquadruplex_strength(string))
    else:
        result.append(-1)
    if find_params[1] == True:
        result.append(max_imotiv_stength(string))
    else:
        result.append(-1)
    if find_params[2] > 0:
        result.append(max_triplex_strength(string))
    else:
        result.append(-1)
    if find_params[3] == True:
        result.append(max_hairpin_strength(string))
    else:
        result.append(-1)
    return tuple(result)
