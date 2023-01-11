from collections import defaultdict
import numpy as np
import regex
import random
import rstr, itertools
import re

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
