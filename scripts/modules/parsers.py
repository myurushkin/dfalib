
def hairpin_weight(hairpin, tail_left):
    weight = 0
    tail_center_right = tail_left + 5
    tail_size = min(tail_left + 1, len(hairpin) - tail_center_right)

    for i in range(tail_size):
        if hairpin[tail_left - i] == 'a' and hairpin[tail_center_right + i] == 't':
            weight += 1
        elif hairpin[tail_left - i] == 't' and hairpin[tail_center_right + i] == 'a':
            weight += 1
        elif hairpin[tail_left - i] == 'c' and hairpin[tail_center_right + i] == 'g':
            weight += 1
        elif hairpin[tail_left - i] == 'g' and hairpin[tail_center_right + i] == 'c':
            weight += 1
        else:
            return weight
    return weight


def max_hairpin_weight(string):
    cw = 0
    tail_index = 0
    for i in range(len(string)):
        cw_new = hairpin_weight(string, i)
        if cw_new > cw:
            cw = cw_new
            tail_index = i
    return cw, tail_index


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


def analyze_string(string):
    return (max_gquadruplex_strength(string, "g"), max_gquadruplex_strength(string, "c"), max_hairpin_weight(string))