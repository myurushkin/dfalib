from modules import helpers
import numpy as np


def hairpin_strength(hairpin, tail_left):
    strength = 0
    tail_center_right = tail_left + 5
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
        else:
            return strength
    return strength


def max_hairpin_strength(string):
    cw = 0
    tail_index = 0
    for i in range(len(string)):
        cw_new = hairpin_strength(string, i)
        if cw_new > cw:
            cw = cw_new
            tail_index = i
    return cw


def traverse_gquadruplex(string, ch, last_pos, last_group_id, groups):
    MinSBetweenGroups = 3
    new_pos = string.find(ch, last_pos + 1)
    if new_pos < 0:
        count = {}
        count[0] = count[1] = count[2] = count[3] = 0
        for gr in groups:
            count[gr[1]] += 1
        return min(count[0], count[1], count[2], count[3])

    result1 = traverse_gquadruplex(string, ch, new_pos, last_group_id, groups)


    current_group_id = last_group_id
    groups.append((new_pos, current_group_id))
    result2 = traverse_gquadruplex(string, ch, new_pos, current_group_id, groups)
    del groups[-1]
    if result2 > result1:
        result1 = result2

    if last_group_id < 3 and new_pos - groups[-1][0] > MinSBetweenGroups:
        current_group_id = last_group_id + 1
        groups.append((new_pos, current_group_id))
        result2 = traverse_gquadruplex(string, ch, new_pos, current_group_id, groups)
        del groups[-1]
        if result2 > result1:
            result1 = result2
    return result1

def max_gquadruplex_strength(string, ch):
    currentPos = string.find(ch)
    if currentPos < 0:
        return -1

    last_group_id = 0
    groups = [(currentPos, last_group_id)]
    return traverse_gquadruplex(string, ch, currentPos, last_group_id, groups)



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
                inverse = min(left_group_size, last_group_size) + min(third_group_size, last_group_size)
                result = max([result, direct, inverse])
    return result


test_strings = ["cgcgcgcg", "cgcabcgcg", "ccgcabcgccg", "ccgcabccgcg", "ccgcabcaacgcg"]
for s in test_strings:
    print("{}: {}".format(s, max_imotiv_stength(s)))



def find_complimentary_position(string, position, left_border):
    if string[position] == 'a':
        try:
            return string.index('t', left_border)
        except ValueError:
            return -1
    if string[position] == 't':
        try:
            return string.index('a', left_border)
        except ValueError:
            return -1
    if string[position] == 'c':
        try:
            return string.index('g', left_border)
        except ValueError:
            return -1
    if string[position] == 'g':
        try:
            return string.index('c', left_border)
        except ValueError:
            return -1

def is_triplex(string, first_position, second_position, third_position, triplex_examples):
    if (third_position - second_position) < 4:
        return False
    if (second_position - first_position) < 4:
        return False
    if (first_position < second_position < third_position) == False:
        return False
    if (first_position < 0) or(second_position < 0) or (third_position < 0):
        return False
    if (first_position > len(string) - 1)or(second_position > len(string) - 1) or (third_position > len(string) - 1):
        return False
    new_triplex = string[first_position] + string[second_position] + string[third_position]
    trps_set = set(helpers.get_triplex_set(triplex_examples))
    if new_triplex in trps_set:
        return True
    return False



def find_next_triplex(string, first_triplex_first_pos, first_triplex_second_pos, first_triplex_third_pos, triplex_examples):
    if (first_triplex_second_pos - first_triplex_first_pos) < 4:
        return 0
    max_strength = 0
    strength = 0
    for l in range(1, first_triplex_second_pos - first_triplex_first_pos):
        another_triplex_first_position = first_triplex_first_pos + l
        another_triplex_second_position = first_triplex_second_pos - l
        another_triplex_third_positon = first_triplex_third_pos + l
        if is_triplex(string, another_triplex_first_position, another_triplex_second_position, another_triplex_third_positon, triplex_examples):
            strength = 1 + find_next_triplex(string, another_triplex_first_position, another_triplex_second_position, another_triplex_third_positon, triplex_examples)
        if strength > max_strength:
            max_strength = strength

    return max_strength

def max_triplex_strength(string, triplex_examples):
    max_strength = 0
    for i in range(len(string)):
        for j in range(len(string)):
            for k in range(len(string)):
                triplex_candidate = sorted([i, j, k])
                if is_triplex(string, triplex_candidate[0], triplex_candidate[1], triplex_candidate[2], triplex_examples):
                    strength = 1
                    strength += find_next_triplex(string, triplex_candidate[0], triplex_candidate[1],
                                                  triplex_candidate[2], triplex_examples)
                    if strength > max_strength:
                        max_strength = strength
                else:
                    continue
    return max_strength


def analyze_string(string, find_params):
    result = []
    if find_params[0] == True:
        result.append(max_gquadruplex_strength(string, "g"))
    else:
        result.append(-1)
    if find_params[1] == True:
        result.append(max_imotiv_stength(string))
        # result.append(max_gquadruplex_strength(string, "c"))
    else:
        result.append(-1)
    if find_params[3] == True:
        result.append(max_hairpin_strength(string))
    else:
        result.append(-1)
    if find_params[2] > 0:
        result.append(max_triplex_strength(string, find_params[2]))
    else:
        result.append(-1)
    return tuple(result)

# find_GQD, find_IMT, find_TRP, find_HRP

