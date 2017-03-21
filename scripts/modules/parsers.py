
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

def is_triplex(string, first_position, second_position, third_position):
    if (third_position - second_position) < 4:
        return False
    if (second_position - first_position) < 4:
        return False
    if (first_position < second_position < third_position) == False:
        return False
    if (first_position < 0)or(second_position < 0) or (third_position < 0):
        return False
    if (first_position > len(string) - 1)or(second_position > len(string) - 1) or (third_position > len(string) - 1):
        return False
    if string[second_position] == 'a' and string[third_position] == 't':
        return True
    if string[second_position] == 't' and string[third_position] == 'a':
        return True
    if string[second_position] == 'c' and string[third_position] == 'g':
        return True
    if string[second_position] == 'c' and string[third_position] == 'g':
        return True
    return False


def find_next_triplex(string, first_triplex_first_pos, first_triplex_second_pos, first_triplex_third_pos, strength):
    if (first_triplex_second_pos - first_triplex_first_pos < 3):
        return strength
    max_strength = strength
    for l in range(1, first_triplex_second_pos - first_triplex_first_pos):
        another_triplex_first_position = first_triplex_first_pos + l
        another_triplex_second_position = first_triplex_second_pos - l
        another_triplex_third_positon = first_triplex_third_pos + l
        print(another_triplex_first_position, another_triplex_second_position, another_triplex_third_positon)
        if is_triplex(string, another_triplex_first_position, another_triplex_second_position, another_triplex_third_positon):
            strength = find_next_triplex(string, another_triplex_first_position, another_triplex_second_position, another_triplex_third_positon, strength + 1)
        if (strength > max_strength):
            max_strength = strength
    return max_strength

def max_triplex_strength(string):
    strength = 0
    max_strength = 0
    for i in range(1, len(string) - 1):
        for j in range(i + 4, len(string) - 1):
            complimentary_position = find_complimentary_position(string, i, j)
            if complimentary_position == -1:
                continue
            strength = 1
            if strength > max_strength:
                max_strength = strength
            # for k in range(0, i):
            #     first_triplex_position = k
            #     print(first_triplex_position, i, complimentary_position)
            #
            #     strength = find_next_triplex(string, first_triplex_position, i, complimentary_position, strength)
            #     if strength > max_strength:
            #         max_strength = strength
            for k in range(0, i):
                first_triplex_position = k
                if (i - first_triplex_position) < 3:
                    continue
                for l in range(1, i - first_triplex_position):
                    second_triplex_first_position = first_triplex_position + l
                    second_triplex_second_position = i - l
                    second_triplex_third_positon = complimentary_position + l
                    if is_triplex(string, second_triplex_first_position, second_triplex_second_position,
                                  second_triplex_third_positon):
                        strength = 2
                        if strength > max_strength:
                            max_strength = strength
                        if (second_triplex_second_position - second_triplex_first_position) < 3:
                            continue
                        for s in range(1, second_triplex_second_position - second_triplex_first_position):
                             third_triplex_first_position = second_triplex_first_position + s
                             third_triplex_second_position = second_triplex_second_position - s
                             third_triplex_third_positon = second_triplex_third_positon + s
                             if is_triplex(string, third_triplex_first_position, third_triplex_second_position,
                                           third_triplex_third_positon):
                                 strength = 3

                                 if strength > max_strength:
                                     max_strength = strength
                             if (third_triplex_second_position - third_triplex_first_position) < 3:
                                 continue
                             for r in range(1, third_triplex_second_position - third_triplex_first_position):
                                 fourth_triplex_first_position = third_triplex_first_position + r
                                 fourth_triplex_second_position = third_triplex_second_position - r
                                 fourth_triplex_third_positon = third_triplex_third_positon + r
                                 if is_triplex(string, fourth_triplex_first_position, fourth_triplex_second_position,
                                               fourth_triplex_third_positon):
                                     strength = 4
                                     if strength > max_strength:
                                         max_strength = strength
                                 if (fourth_triplex_second_position - fourth_triplex_first_position) < 3:
                                     continue
                                 for t in range(1, fourth_triplex_second_position - fourth_triplex_first_position):
                                     fifth_triplex_first_position = fourth_triplex_first_position + t
                                     fifth_triplex_second_position = fourth_triplex_second_position - t
                                     fifth_triplex_third_positon = fourth_triplex_third_positon + t
                                     if is_triplex(string, fifth_triplex_first_position,
                                                   fifth_triplex_second_position,
                                                   fifth_triplex_third_positon):
                                         strength = 5
                                         if strength > max_strength:
                                             max_strength = strength


    return max_strength


def analyze_string(string):
    return (max_gquadruplex_strength(string, "g"), max_gquadruplex_strength(string, "c"), max_hairpin_strength(string), max_triplex_strength(string))