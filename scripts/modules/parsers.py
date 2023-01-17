from modules import helpers
from collections import defaultdict
import numpy as np

# def hairpin_strength(hairpin, tail_left):
#     max_strength = 0
#     max_head_size = 0
#     for j in range(3, len(hairpin) - tail_left):
#         head_size = j
#         strength = 0
#         tail_center_right = tail_left + head_size + 1
#         tail_size = min(tail_left + 1, len(hairpin) - tail_center_right)
#
#         for i in range(tail_size):
#             if hairpin[tail_left - i] == 'a' and hairpin[tail_center_right + i] == 't':
#                 strength += 1
#             elif hairpin[tail_left - i] == 't' and hairpin[tail_center_right + i] == 'a':
#                 strength += 1
#             elif hairpin[tail_left - i] == 'c' and hairpin[tail_center_right + i] == 'g':
#                 strength += 1
#             elif hairpin[tail_left - i] == 'g' and hairpin[tail_center_right + i] == 'c':
#                 strength += 1
#         if strength > max_strength:
#             max_strength = strength
#             max_head_size = head_size
#     return max_strength, max_head_size
#
#
# def max_hairpin_strength(string):
#     cw = 0
#     max_i = 0
#     max_head_size = 0
#     for i in range(len(string)):
#         cw_new, new_head_size = hairpin_strength(string, i)
#         if cw_new > cw:
#             max_head_size = new_head_size
#             max_i = i
#             cw = cw_new
# #    print("head_start: {}".format(max_i + 1))
# #    print("head_size: {}".format(max_head_size))
#     return cw


def max_gquadruplex_strength(string):
    min_g_count = 8
    g_count = 0
    for s in string:
        if s == 'g':
            g_count += 1
    if g_count < min_g_count:
        return 0
    groups_count = 4
    max_strength = 0
    while True:
        new_strength = max_strength + 1
        finded_groups = 0
        current_count_in_group = 0
        i = 0
        while i < len(string):
            if string[i] == 'g':
                current_count_in_group += 1
                if current_count_in_group == new_strength:
                    current_count_in_group = 0
                    finded_groups += 1
                    i += 1
            i += 1
        if finded_groups < groups_count:
           return max_strength
        max_strength = new_strength


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
            counts[i+1] += 1


    def cnt(begin, end):
        if begin >= end:
            return 0
        return counts[end] - counts[begin]

    for cursor_central in range(len(input_string)):
        for cursor_left in range(cursor_central):
            for cursor_right in range(cursor_central, len(input_string)):
                left_group_size = cnt(0, cursor_left)
                second_group_size = cnt(cursor_left+1, cursor_central)
                third_group_size = cnt(cursor_central+2, cursor_right)
                last_group_size = cnt(cursor_right+1, len(input_string))

                if min([left_group_size, second_group_size, third_group_size, last_group_size]) == 0:
                    continue
                direct = min(left_group_size, third_group_size) + min(second_group_size, last_group_size)
                inverse = min(left_group_size, last_group_size) + min(second_group_size, third_group_size)
                result = max([result, direct, inverse])
    return result


def is_triplex(left_part, center_part, right_part, case):
    if case == "left":
        #yry
        if helpers.is_complimentary_strings(left_part, center_part) \
                and helpers.is_complimentary_strings(left_part, right_part, reverse_complimentary=True):
            return True
        #yrr
        if helpers.is_complimentary_strings(left_part, center_part) \
                and helpers.is_weak_complimentary_strings(left_part, right_part):
            return True
    if case == "center":
        #yry
        if helpers.is_complimentary_strings(center_part, left_part, reverse_complimentary=True) \
                and helpers.is_complimentary_strings(center_part, right_part, reverse_complimentary=True):
            return True
        #yrr
        if helpers.is_complimentary_strings(center_part, left_part, reverse_complimentary=True) \
                and helpers.is_weak_complimentary_strings(center_part, right_part, reverse_complimentary=True):
            return True
    if case == "right":
        #yry
        if helpers.is_complimentary_strings(right_part, center_part, reverse_complimentary=True) \
                and helpers.is_complimentary_strings(right_part, left_part):
            return True
        #yrr
        if helpers.is_complimentary_strings(right_part, center_part, reverse_complimentary=True) \
                and helpers.is_weak_complimentary_strings(right_part, left_part):
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
        for j in range(i+1, len(string)):
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
                    right_end = i + 2*candidate_len + y

                    left_part = cash_dict[left_start][left_end]
                    right_part = cash_dict[right_start][right_end]
                    center_part = candidate
                    if is_triplex(left_part, center_part, right_part, "center"):
                        max_strength = max(max_strength, candidate_len)
                        continue
                    if is_triplex(right_part[::-1], center_part[::-1], left_part[::-1], "center"):
                        max_strength = max(max_strength, candidate_len)
                        continue

                    #left_case:
                    center_start = i + candidate_len + x
                    center_end = i + 2*candidate_len + x
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
                    #right case
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

# find_GQD, find_IMT, find_TRP, find_HRP



if __name__ == "__main__":
    test_strings = ["ccccccccccccc", "cgcgcgcg", "cgcabcgcg", "ccgcabcgccg", "ccgcabccgcg", "ccgcabcaacgcg"]
    for s in test_strings:
        print("{}: {}".format(s, max_imotiv_stength(s)))
