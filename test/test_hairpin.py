import random
import unittest
import regex
import rstr
import dafna
from dafna.lib.strength import hairpin
from collections import defaultdict
import json

import json
from random import random

import networkx as nx
import matplotlib.pyplot as plt


def draw(n : dict):
    g = nx.PlanarEmbedding()
    g.set_data(n)
    pos = nx.planar_layout(g)  # here are your positions.
    # pos = nx.spring_layout(g, pos=pos, seed=int(2**32 - 1 * random()))
    nx.draw_networkx(g, pos, with_labels=True)
    plt.show()


def print_pic(nucls, pic):
    nodes = defaultdict(list)
    def name(ind):
        return f"{nucls[ind]}{ind}"

    for i in range(len(nucls) - 1):
        nodes[name(i)].append(name(i+1))

    for i in range(1, len(nucls)):
        nodes[name(i)].append(name(i-1))

    for pair in pic:
        nodes[name(pair[0])].append(name(pair[1]))
        nodes[name(pair[1])].append(name(pair[0]))

    draw(nodes)


class TestHairpin(unittest.TestCase):

    def test_01(self):
        ss = 'gcggatttagctcagttgggagagcgccagactgaatatctggaggtcctgtgttcgatccacagaattcgcacc'
        #ss = 'atatatatatatatatatatatatatatatatatatatatatatatatatatatatatat'
        # res, pic = hairpin.max_hairpin_strength_2(ss)
        #
        # with open("graph.json", 'w') as f:
        #     json.dump({"string": ss, "edges": pic}, f, indent=4)


        s = 'acg' * 6
        values = [
           # ('gcggatttagctcagttgggagagcgccagactgaatatctggaggtcctgtgttcgatccacagaattcgcacc', 12),
            (s, 5),
            ('aagcatt', 2),
            ('', 0),
            ('aaat', 0),
            ('aaaat', 1),

            ('aaattaaattaaattaaattaaattaaattaaattaaattaaattaaattaaattaaatt', 23),
            ('atatatatatatatatatatatatatatatatatatatatatatatatatatatatatat', 28),
            #('acgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacgacg', 18),
        ]

        for str_val, val in values:
            print(str_val)
            self.assertEqual(hairpin.max_hairpin_strength(str_val), val)

    def test_02(self):
        return
        def hairpin_random_string(strength):
            n = random.randint(1, strength - 1)
            m = strength - n

            hairpin_head_pattern = f'((a|t){{{n}}})((g|c){{{m}}})'
            hairpin_loop_pattern = '(a|t){3,7}'
            hairpin_tail_pattern = '({gc_group}{at_group})'

            hairpin_head = rstr.xeger(hairpin_head_pattern)
            hairpin_loop = rstr.xeger(hairpin_loop_pattern)
            sub_groups = regex.findall(hairpin_head_pattern, hairpin_head)[0]
            hairpin_tail = rstr.xeger(hairpin_tail_pattern.format(
                gc_group=dafna.replace_complimentary_symbol(sub_groups[2][::-1]),
                at_group=dafna.replace_complimentary_symbol(sub_groups[0][::-1])
                )
            )

            return f'{hairpin_head}{hairpin_loop}{hairpin_tail}'

        hairpin_strings = [hairpin_random_string(n) for n in range(3, 20)]

        self.assertEqual(list(range(3, 20)), [dafna.hairpin_max_strength(hairpin) for hairpin in hairpin_strings])


