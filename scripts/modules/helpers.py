import numpy as np
import random


def get_triplex_set(kind=1):
    assert kind == 1 or kind == 2
    if kind == 1:
        return ['tac', 'taa', 'tag', 'cgg', 'atg', 'cgt', 'cga', 'cgc', 'tat']
    return ['cat', 'agc', 'cgc', 'gat', 'ggc', 'tgc', 'tat', 'gta', 'aat']


def generate_random_string(min_size, max_size):
    size = random.randint(min_size, max_size)
    map_array = ['a', 't', 'g', 'c']
    arr = np.random.randint(4, size=size)
    return ''.join(list(map(lambda x: map_array[x], arr)))


def generate_random_strings(min_size, max_size, count):
    for i in range(count):
        yield generate_random_string(min_size, max_size)


def is_complimentary_strings(left_string, right_string, reverse_complimentary=False):
    if len(left_string) != len(right_string):
        return False
    for i in range(len(left_string)):
        left_letter = left_string[i]
        right_letter = right_string[i] if not reverse_complimentary else right_string[-i-1]
        if left_letter == 'a' and right_letter != 't':
            return False
        if left_letter == 't' and right_letter != 'a':
            return False
        if left_letter == 'g' and right_letter != 'c':
            return False
        if left_letter == 'c' and right_letter != 'g':
            return False
    return True
